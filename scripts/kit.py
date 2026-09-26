#!/usr/bin/env python3
"""Kit manager. kit.toml is the source of truth; everything else is generated.

  python scripts/kit.py build             validate + regenerate all generated files + bump changed plugin versions
  python scripts/kit.py check             validate + fail if generated files are stale (CI runs this)
  python scripts/kit.py new-skill ID -p PLUGIN   scaffold a local skill and register it in kit.toml
  python scripts/kit.py vendor ID|--all   (re)fetch vendored github skills
  python scripts/kit.py audit ID|--stale|--all   SkillSpector scan + triage gate for skills, agents, plugins, MCPs
  python scripts/kit.py drift             compare pinned upstreams with their latest commit
  python scripts/kit.py list              print what the kit contains
  python scripts/kit.py embed DIR [--profile P] [--add X]   optional: copy the kit into a project's .claude/ (private add-on repos)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    try:
        import tomli as tomllib  # type: ignore
    except ModuleNotFoundError:
        sys.exit("Needs Python 3.11+ (or: pip install tomli)")

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "kit.toml"
LOCK = ROOT / "kit.lock.json"
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
GH_RE = re.compile(r"^github:([\w.-]+/[\w.-]+)(?:@([^:]+))?:(.+)$")
DESC_MAX = 1024
PLACEHOLDER = "TODO"


class Plan:
    """Virtual file system: generated writes and deletes, applied or diffed."""

    def __init__(self) -> None:
        self.writes: dict[Path, str] = {}
        self.deletes: set[Path] = set()

    def write(self, path: Path, text: str) -> None:
        self.writes[path] = text if text.endswith("\n") else text + "\n"
        self.deletes.discard(path)

    def delete(self, path: Path) -> None:
        if path.exists():
            self.deletes.add(path)
        self.writes.pop(path, None)

    def read(self, path: Path) -> bytes | None:
        if path in self.writes:
            return self.writes[path].encode()
        if path in self.deletes or not path.exists():
            return None
        return path.read_bytes()

    def stale(self) -> list[str]:
        out = []
        for p, t in self.writes.items():
            if not p.exists() or p.read_text(encoding="utf-8") != t:
                out.append(str(p.relative_to(ROOT)))
        out += [str(p.relative_to(ROOT)) for p in self.deletes if p.exists()]
        return sorted(out)

    def apply(self) -> None:
        for p, t in self.writes.items():
            p.parent.mkdir(parents=True, exist_ok=True)
            if not p.exists() or p.read_text(encoding="utf-8") != t:
                p.write_text(t, encoding="utf-8")
        for p in self.deletes:
            p.unlink(missing_ok=True)


# ── helpers ──────────────────────────────────────────────────

def load() -> dict:
    return tomllib.loads(REG.read_text(encoding="utf-8"))


def sentence(s: str) -> str:
    s = " ".join(s.split())
    return s if s.endswith((".", "!", "?")) else s + "."


def cell(s: str) -> str:
    return sentence(s).replace("|", "\\|")


def skill_dir(s: dict) -> Path:
    return ROOT / "plugins" / s["plugin"] / "skills" / s["id"]


def agent_file(a: dict) -> Path:
    return ROOT / "plugins" / a["plugin"] / "agents" / f"{a['id']}.md"


def description(s: dict) -> str:
    return f"{sentence(s['summary'])} Use when: {sentence(s['when'])} Not for: {sentence(s['not_when'])}"


def npx_package(m: dict) -> str | None:
    if m.get("command") != "npx":
        return None
    return next((a for a in m.get("args", []) if not a.startswith("-")), None)


def rewrite_frontmatter(text: str, name: str, desc: str) -> str:
    text = text.replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---[ \t]*\n?", text, re.S)
    fm, body = (m.group(1).split("\n"), text[m.end():]) if m else ([], text)
    kept, skipping = [], False
    for line in fm:
        indented = line[:1] in (" ", "\t")
        if skipping and (indented or not line.strip()):
            continue
        skipping = False
        if not indented and line.split(":", 1)[0].strip() in ("name", "description"):
            skipping = True
            continue
        kept.append(line)
    head = [f"name: {name}", f"description: {json.dumps(desc, ensure_ascii=False)}", *kept]
    return "---\n" + "\n".join(head) + "\n---\n\n" + body.lstrip("\n")


def plugin_hash(plan: Plan, pdir: Path) -> str:
    skip = pdir / ".claude-plugin" / "plugin.json"
    paths = {p for p in pdir.rglob("*") if p.is_file()} | {p for p in plan.writes if pdir in p.parents}
    h = hashlib.sha256()
    for p in sorted(paths - {skip} - plan.deletes):
        data = plan.read(p)
        if data is None:
            continue
        h.update(str(p.relative_to(pdir)).encode() + b"\0" + data + b"\0")
    return h.hexdigest()[:16]


def bump(v: str) -> str:
    a, b, c = (int(x) for x in v.split("."))
    return f"{a}.{b}.{c + 1}"


def dumps(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


# ── validation ───────────────────────────────────────────────

def validate(reg: dict) -> list[str]:
    e: list[str] = []
    kit = reg.get("kit", {})
    for k in ("name", "owner", "repo"):
        if not kit.get(k):
            e.append(f"[kit] missing '{k}'")
    plugins = reg.get("plugins", {})
    if "core" not in plugins:
        e.append("[plugins.core] is required")
    for name, p in plugins.items():
        if not ID_RE.match(name):
            e.append(f"plugin '{name}': must be lowercase-hyphen")
        if not p.get("description"):
            e.append(f"plugin '{name}': missing description")

    seen: dict[str, str] = {n: "plugin" for n in plugins}

    def claim(i: str, kind: str) -> None:
        if i in seen:
            e.append(f"{kind} '{i}': id already used by a {seen[i]}")
        seen[i] = kind

    def routing(kind: str, x: dict, fields=("when", "not_when")) -> None:
        for f in fields:
            v = x.get(f, "")
            if not v or PLACEHOLDER in v:
                e.append(f"{kind} '{x.get('id')}': '{f}' is empty or still {PLACEHOLDER}")
            elif len(v) < 25:
                e.append(f"{kind} '{x.get('id')}': '{f}' too vague ({len(v)} chars); describe concrete situations")

    for s in reg.get("skill", []):
        sid = s.get("id", "?")
        if not ID_RE.match(sid) or len(sid) > 64:
            e.append(f"skill '{sid}': id must be lowercase-hyphen, max 64 chars")
        claim(sid, "skill")
        if s.get("plugin") not in plugins:
            e.append(f"skill '{sid}': unknown plugin '{s.get('plugin')}'")
            continue
        routing("skill", s, ("summary", "when", "not_when"))
        src = s.get("source", "")
        if src != "local" and not GH_RE.match(src):
            e.append(f"skill '{sid}': source must be 'local' or 'github:owner/repo@ref:path'")
        if not (skill_dir(s) / "SKILL.md").is_file():
            hint = f" (run: kit.py vendor {sid})" if src.startswith("github:") else ""
            e.append(f"skill '{sid}': {skill_dir(s).relative_to(ROOT)}/SKILL.md not found{hint}")
        elif not any(PLACEHOLDER in s.get(f, "") for f in ("summary", "when", "not_when")):
            if len(description(s)) > DESC_MAX:
                e.append(f"skill '{sid}': composed description is {len(description(s))} chars (max {DESC_MAX})")

    for a in reg.get("agent", []):
        aid = a.get("id", "?")
        if not ID_RE.match(aid):
            e.append(f"agent '{aid}': id must be lowercase-hyphen")
        claim(aid, "agent")
        if a.get("plugin") not in plugins:
            e.append(f"agent '{aid}': unknown plugin '{a.get('plugin')}'")
            continue
        routing("agent", a, ("summary", "when", "not_when"))
        if not agent_file(a).is_file():
            e.append(f"agent '{aid}': {agent_file(a).relative_to(ROOT)} not found")
    reg_agents = {(a.get("plugin"), a.get("id")) for a in reg.get("agent", [])}
    for pname in plugins:
        adir = ROOT / "plugins" / pname / "agents"
        if adir.is_dir():
            for f in sorted(adir.glob("*.md")):
                if (pname, f.stem) not in reg_agents:
                    e.append(f"orphan agent plugins/{pname}/agents/{f.name} is not in kit.toml")

    registered = {(s.get("plugin"), s.get("id")) for s in reg.get("skill", [])}
    for pname in plugins:
        sroot = ROOT / "plugins" / pname / "skills"
        if sroot.is_dir():
            for d in sorted(x for x in sroot.iterdir() if x.is_dir()):
                if (pname, d.name) not in registered:
                    e.append(f"orphan skill folder plugins/{pname}/skills/{d.name} is not in kit.toml")

    for m in reg.get("mcp", []):
        mid = m.get("id", "?")
        claim(mid, "mcp")
        if m.get("plugin") not in plugins:
            e.append(f"mcp '{mid}': unknown plugin '{m.get('plugin')}'")
        routing("mcp", m)
        t = m.get("type", "stdio")
        if t == "stdio" and not m.get("command"):
            e.append(f"mcp '{mid}': stdio server needs 'command'")
        if t in ("http", "sse") and not m.get("url"):
            e.append(f"mcp '{mid}': {t} server needs 'url'")
        if t not in ("stdio", "http", "sse"):
            e.append(f"mcp '{mid}': type must be stdio, http or sse")
        pkg = npx_package(m)
        if m.get("command") == "npx" and (not pkg or not re.search(r"@\d[\w.-]*$", pkg)):
            e.append(f"mcp '{mid}': pin an exact npm version in args (e.g. pkg@1.2.3), never @latest")
        if t != "stdio" or m.get("command") not in ("npx",):
            if not m.get("manual_review"):
                e.append(f"mcp '{mid}': cannot be auto-scanned; add manual_review = \"<what you checked>\"")
        blob = json.dumps({k: m.get(k) for k in ("env", "headers", "args", "url")})
        if re.search(r"(sk-|ghp_|xox[bp]-|AKIA)[A-Za-z0-9]{8,}", blob):
            e.append(f"mcp '{mid}': looks like an inline secret; use \"${{VAR}}\" instead")

    for x in reg.get("external", []):
        xid = x.get("id", "?")
        claim(xid, "external plugin")
        if not x.get("repo") or "/" not in x.get("repo", ""):
            e.append(f"external '{xid}': needs repo = 'owner/name'")
        if x.get("attach") not in plugins:
            e.append(f"external '{xid}': attach must be a kit plugin")
        routing("external", x)
        if not x.get("description"):
            e.append(f"external '{xid}': missing description")

    rejected = {r.get("id"): r for r in reg.get("rejected", [])}
    for r in reg.get("rejected", []):
        if not r.get("reason") or not r.get("date"):
            e.append(f"rejected '{r.get('id')}': needs reason and date")
    for i, kind in seen.items():
        if i in rejected:
            r = rejected[i]
            e.append(f"{kind} '{i}' was rejected on {r.get('date')}: {r.get('reason')} (remove the [[rejected]] entry only with the user's yes)")

    ext_ids = {x.get("id") for x in reg.get("external", [])}
    for x in reg.get("external", []):
        if x.get("sha") and not re.fullmatch(r"[0-9a-f]{40}", x["sha"]):
            e.append(f"external '{x.get('id')}': sha must be a full 40-char commit")
    for s in reg.get("skill", []):
        for o in s.get("overrides", []):
            if ":" not in o or o.split(":", 1)[0] not in ext_ids:
                e.append(f"skill '{s.get('id')}': override '{o}' must be '<external-plugin>:<skill>'")

    known = set(plugins) | {x["id"] for x in reg.get("external", []) if "id" in x}
    for prof, items in reg.get("profiles", {}).items():
        if "core" not in items:
            e.append(f"profile '{prof}': must include core")
        for i in items:
            if i not in known:
                e.append(f"profile '{prof}': unknown plugin '{i}'")
    return e


# ── generation ───────────────────────────────────────────────

def index_md(reg: dict, pname: str) -> str:
    p = reg["plugins"][pname]
    out = []
    if pname == "core":
        out += ["# Kit router", ""]
        out += [f"{i}. {r}" for i, r in enumerate(reg.get("router", {}).get("rules", []), 1)]
        out += [""]
    out += [f"## Kit plugin: {pname}", sentence(p["description"]), ""]
    skills = [s for s in reg.get("skill", []) if s["plugin"] == pname]
    mcps = [m for m in reg.get("mcp", []) if m["plugin"] == pname]
    ext = [x for x in reg.get("external", []) if x["attach"] == pname]
    if skills:
        out += ["### Skills", "| Skill | Use when | Not for |", "|---|---|---|"]
        out += [f"| `{s['id']}` | {cell(s['when'])} | {cell(s['not_when'])} |" for s in skills]
        out += [""]
    if mcps:
        out += ["### MCP servers", "| Server | Use when | Not for |", "|---|---|---|"]
        out += [f"| `{m['id']}` | {cell(m['when'])} | {cell(m['not_when'])} |" for m in mcps]
        out += [""]
    agents = [a for a in reg.get("agent", []) if a["plugin"] == pname]
    if agents:
        out += ["### Subagents (delegate with the Task tool; they start with a fresh context)", "| Agent | Use when | Not for |", "|---|---|---|"]
        out += [f"| `{a['id']}` | {cell(a['when'])} | {cell(a['not_when'])} |" for a in agents]
        out += [""]
    prec = [(s["id"], o) for s in skills for o in s.get("overrides", [])]
    if prec:
        out += ["### Precedence (same job, ours wins)"]
        out += [f"- `{a}` over `{b}`" for a, b in prec]
        out += [""]
    if ext:
        out += ["### Companion plugins (use their skills when enabled)", "| Plugin | Use when | Not for |", "|---|---|---|"]
        out += [f"| `{x['id']}` | {cell(x['when'])} | {cell(x['not_when'])} |" for x in ext]
        out += [""]
    return "<!-- GENERATED by scripts/kit.py from kit.toml. Do not edit. -->\n" + "\n".join(out)


def mcp_entry(m: dict) -> dict:
    t = m.get("type", "stdio")
    if t == "stdio":
        d = {"command": m["command"], "args": m.get("args", [])}
        if m.get("env"):
            d["env"] = m["env"]
        return d
    d = {"type": t, "url": m["url"]}
    if m.get("headers"):
        d["headers"] = m["headers"]
    return d


def plan_build(reg: dict, lock: dict) -> tuple[Plan, dict, list[str]]:
    plan, changed = Plan(), []
    kit = reg["kit"]

    for s in reg.get("skill", []):
        f = skill_dir(s) / "SKILL.md"
        plan.write(f, rewrite_frontmatter(f.read_text(encoding="utf-8"), s["id"], description(s)))
    for a in reg.get("agent", []):
        f = agent_file(a)
        plan.write(f, rewrite_frontmatter(f.read_text(encoding="utf-8"), a["id"], description(a)))

    new_lock = {"plugins": {}}
    market_plugins = []
    for pname, p in reg["plugins"].items():
        pdir = ROOT / "plugins" / pname
        (pdir / "skills").mkdir(parents=True, exist_ok=True)
        plan.write(pdir / "INDEX.md", index_md(reg, pname))

        mcps = {m["id"]: mcp_entry(m) for m in reg.get("mcp", []) if m["plugin"] == pname}
        if mcps:
            plan.write(pdir / ".mcp.json", dumps({"mcpServers": mcps}))
        else:
            plan.delete(pdir / ".mcp.json")

        custom = pdir / "hooks" / "session-start.sh"
        cmd = f'bash "${{CLAUDE_PLUGIN_ROOT}}/hooks/session-start.sh"' if custom.exists() else 'cat "${CLAUDE_PLUGIN_ROOT}/INDEX.md"'
        plan.write(pdir / "hooks" / "hooks.json", dumps(
            {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": cmd}]}]}}))

        h = plugin_hash(plan, pdir)
        old = lock.get("plugins", {}).get(pname, {})
        version = old.get("version", "1.0.0")
        if old and old.get("hash") != h:
            version = bump(version)
            changed.append(pname)
        elif not old:
            changed.append(pname)
        new_lock["plugins"][pname] = {"version": version, "hash": h}

        plan.write(pdir / ".claude-plugin" / "plugin.json", dumps({
            "name": pname, "version": version, "description": sentence(p["description"]),
            "author": {"name": kit["owner"]},
        }))
        market_plugins.append({"name": pname, "source": f"./plugins/{pname}",
                               "description": sentence(p["description"]), "version": version})

    for x in reg.get("external", []):
        src = {"source": "github", "repo": x["repo"]}
        for k in ("ref", "sha"):
            if x.get(k):
                src[k] = x[k]
        market_plugins.append({"name": x["id"], "source": src, "description": sentence(x["description"])})

    plan.write(ROOT / ".claude-plugin" / "marketplace.json", dumps({
        "name": kit["name"], "owner": {"name": kit["owner"]},
        "metadata": {"description": sentence(kit.get("description", ""))},
        "plugins": market_plugins,
    }))

    for prof, items in reg.get("profiles", {}).items():
        plan.write(ROOT / "install" / "profiles" / f"{prof}.json", dumps({
            "extraKnownMarketplaces": {kit["name"]: {"source": {"source": "github", "repo": kit["repo"]}}},
            "enabledPlugins": {f"{i}@{kit['name']}": True for i in items},
        }))
    pdir_profiles = ROOT / "install" / "profiles"
    if pdir_profiles.is_dir():
        for f in pdir_profiles.glob("*.json"):
            if f.stem not in reg.get("profiles", {}):
                plan.delete(f)

    plan.write(ROOT / "CATALOG.md", catalog_md(reg, new_lock, plan))
    plan.write(LOCK, dumps(new_lock))
    return plan, new_lock, changed


def catalog_md(reg: dict, lock: dict, plan: "Plan") -> str:
    out = ["<!-- GENERATED by scripts/kit.py from kit.toml. Do not edit. -->", "# Catalog", ""]
    out += ["| Plugin | Version | Skills | MCPs | Companions |", "|---|---|---|---|---|"]
    for pname in reg["plugins"]:
        sk = ", ".join(f"`{s['id']}`" for s in reg.get("skill", []) if s["plugin"] == pname) or "-"
        mc = ", ".join(f"`{m['id']}`" for m in reg.get("mcp", []) if m["plugin"] == pname) or "-"
        ex = ", ".join(f"`{x['id']}`" for x in reg.get("external", []) if x["attach"] == pname) or "-"
        out.append(f"| **{pname}** | {lock['plugins'][pname]['version']} | {sk} | {mc} | {ex} |")
    out += ["", "## Profiles", "", "| Profile | Plugins |", "|---|---|"]
    out += [f"| `{k}` | {', '.join(v)} |" for k, v in reg.get("profiles", {}).items()]
    out += ["", "## Vendored skills", ""]
    vend = [s for s in reg.get("skill", []) if s.get("source", "").startswith("github:")]
    out += [f"- `{s['id']}` from `{s['source']}`" for s in vend] or ["None."]
    out += ["", "## External plugins", ""]
    out += [f"- `{x['id']}` github:{x['repo']} @ {x.get('sha', 'unpinned')[:8]}" + (f"  \n  **Accepted risk:** {x['risk']}" if x.get("risk") else "") for x in reg.get("external", [])] or ["None."]
    out += ["", "## Audits (SkillSpector + reviewed baseline)", "", "| Item | Status | Score (raw) | Active H/C | Suppressed | Scanned |", "|---|---|---|---|---|---|"]
    for kind, item in audit_items(reg):
        rec = read_record(kind, item["id"])
        if not rec:
            out.append(f"| {kind} `{item['id']}` | MISSING | - | - | - | - |")
            continue
        fresh = rec.get("target") == audit_target(kind, item, plan)
        st = ("MANUAL" if rec.get("verdict") == "manual" else rec.get("verdict", "?").upper()) + ("" if fresh else " (STALE)")
        out.append(f"| {kind} `{item['id']}` | {st} | {rec.get('raw_score', '-')} | {rec.get('active_high_critical', '-')} | {rec.get('suppressed', '-')} | {rec.get('date', '-')} |")
    out += ["", "## Rejected (do not re-add without a new reason)", "", "| Item | Date | Reason |", "|---|---|---|"]
    out += [f"| `{r['id']}` | {r['date']} | {r['reason']} |" for r in reg.get("rejected", [])]
    return "\n".join(out)



# ── audit (SkillSpector) ─────────────────────────────────────
AUDITS = ROOT / "audits"
SURFACE = {".claude-plugin", "skills", "commands", "agents", "hooks", ".mcp.json"}
MIN_REASON = 20
GENERIC = {"accepted", "false positive", "fp", "ok", "fine", "safe", "not an issue", "test"}


def audit_items(reg: dict) -> list[tuple[str, dict]]:
    items = [("skill", x) for x in reg.get("skill", [])] + [("agent", x) for x in reg.get("agent", [])]
    items += [("plugin", x) for x in reg.get("external", [])] + [("mcp", x) for x in reg.get("mcp", [])]
    return items


def dir_hash(plan: "Plan | None", root: Path) -> str:
    h = hashlib.sha256()
    files = {p for p in root.rglob("*") if p.is_file()} if root.is_dir() else {root}
    if plan:
        files |= {p for p in plan.writes if p == root or root in p.parents}
    for p in sorted(files):
        data = plan.read(p) if plan else (p.read_bytes() if p.exists() else None)
        if data is None:
            continue
        rel = p.name if root.is_file() or not root.is_dir() else str(p.relative_to(root))
        h.update(rel.encode() + b"\0" + data + b"\0")
    return "sha256:" + h.hexdigest()[:24]


def audit_target(kind: str, item: dict, plan: "Plan | None" = None) -> str:
    if kind == "skill":
        return dir_hash(plan, skill_dir(item))
    if kind == "agent":
        return dir_hash(plan, agent_file(item))
    if kind == "plugin":
        return f"{item['repo']}@{item.get('sha', 'unpinned')}"
    pkg = npx_package(item)
    return f"npm:{pkg}" if pkg else f"manual:{item.get('url') or item.get('command')}"


def rec_path(kind: str, iid: str) -> Path:
    return AUDITS / f"{kind}-{iid}.json"


def read_record(kind: str, iid: str) -> dict | None:
    p = rec_path(kind, iid)
    return json.loads(p.read_text()) if p.exists() else None


def scanner_cfg(reg: dict) -> dict:
    return reg.get("audit", {})


def ensure_scanner(reg: dict) -> str:
    want = scanner_cfg(reg).get("version", "")
    exe = shutil.which("skillspector")
    have = subprocess.run([exe, "--version"], capture_output=True, text=True).stdout if exe else ""
    if exe and want and want in have:
        return exe
    src = scanner_cfg(reg).get("install")
    if not src:
        sys.exit("[audit] install is not set in kit.toml")
    print(f"installing skillspector {want} ...")
    base = [sys.executable, "-m", "pip", "install", "-q", src]
    if subprocess.run(base).returncode != 0:
        subprocess.run(base + ["--break-system-packages"], check=True)
    exe = shutil.which("skillspector")
    if not exe:
        sys.exit("skillspector installed but not on PATH")
    return exe


def build_surface(kind: str, item: dict, tmp: Path) -> tuple[Path, str]:
    """Return (path to scan, scope note)."""
    if kind == "skill":
        return skill_dir(item), "whole skill folder"
    if kind == "agent":
        d = tmp / "agent"
        d.mkdir()
        shutil.copy(agent_file(item), d / agent_file(item).name)
        return d, "agent file"
    if kind == "plugin":
        repo_dir = tmp / "repo"
        repo_dir.mkdir()
        git("init", "-q", cwd=str(repo_dir))
        git("remote", "add", "origin", f"https://github.com/{item['repo']}", cwd=str(repo_dir))
        git("fetch", "-q", "--depth", "1", "origin", item.get("sha") or "HEAD", cwd=str(repo_dir))
        git("checkout", "-q", "FETCH_HEAD", cwd=str(repo_dir))
        include = set(SURFACE)
        pj = repo_dir / ".claude-plugin" / "plugin.json"
        if pj.exists():
            for v in json.loads(pj.read_text()).values():
                for ref in (v if isinstance(v, list) else [v]):
                    if isinstance(ref, str) and ref.startswith("./"):
                        include.add(ref[2:].strip("/").split("/")[0])
        # anything a hook executes is part of the surface too
        for hj in list((repo_dir / "hooks").glob("*.json")) + [repo_dir / p for p in include if p.endswith(".json")]:
            if hj.is_file():
                for ref in re.findall(r"CLAUDE_PLUGIN_ROOT\}?/([\w.-]+)", hj.read_text(errors="ignore")):
                    include.add(ref)
        surf = tmp / "surface"
        surf.mkdir()
        for name in sorted(include):
            src = repo_dir / name
            if src.is_dir():
                shutil.copytree(src, surf / name, ignore=shutil.ignore_patterns(".git", "node_modules", "tests", "test", "docs"))
            elif src.is_file():
                shutil.copy(src, surf / name)
        return surf, "installable surface: " + ", ".join(sorted(p.name for p in surf.iterdir()))
    pkg = npx_package(item)
    if not pkg:
        return tmp, "manual"
    subprocess.run(["npm", "pack", pkg, "--silent", "--pack-destination", str(tmp)], check=True, capture_output=True)
    tgz = next(tmp.glob("*.tgz"))
    subprocess.run(["tar", "xzf", str(tgz), "-C", str(tmp)], check=True)
    pkg_dir = tmp / "package"
    for doc in list(pkg_dir.glob("*.md")) + [pkg_dir / "docs"]:  # prose is never sent to the model by an MCP server
        shutil.rmtree(doc) if doc.is_dir() else doc.unlink(missing_ok=True)
    return pkg_dir, f"npm package {pkg} minus markdown docs; transitive dependencies not scanned"


def triage_path(kind: str, iid: str) -> Path:
    return AUDITS / f"{kind}-{iid}.triage.json"


def load_baseline(kind: str, iid: str, version: str) -> dict | None:
    tp = triage_path(kind, iid)
    if not tp.exists():
        return None
    ok = [t for t in json.loads(tp.read_text()) if len(t.get("reason", "").strip()) >= MIN_REASON]
    fps = [{"hash": t["hash"], "rule_id": t["rule_id"], "file": t["file"], "reason": t["reason"]} for t in ok if not t.get("as_rule")]
    # as_rule: for repeated identical findings the scanner fingerprints once; scope a glob rule to that file (+ message)
    rules = [{"id": t["rule_id"], "path": t["file"], "message": t.get("message", "*"), "reason": t["reason"]} for t in ok if t.get("as_rule")]
    return {"version": 2, "scanner_version": version, "rules": rules, "fingerprints": fps} if (fps or rules) else None


def audit_one(reg: dict, exe: str, kind: str, item: dict) -> dict:
    iid = item["id"]
    version = scanner_cfg(reg).get("version", "")
    if kind == "mcp" and not npx_package(item):
        rec = {"kind": kind, "id": iid, "target": audit_target(kind, item), "verdict": "manual",
               "scope": "not auto-scannable", "note": item.get("manual_review", ""),
               "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")}
        rec_path(kind, iid).write_text(dumps(rec) + "\n")
        return rec
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        target_dir, scope = build_surface(kind, item, tmp)
        base = load_baseline(kind, iid, version)
        bfile = tmp / "baseline.json"
        cmd = [exe, "scan", str(target_dir), "--no-llm", "--format", "json", "-o", str(tmp / "report.json")]
        if base:
            bfile.write_text(json.dumps(base))
            cmd += ["-b", str(bfile)]
        subprocess.run(cmd, capture_output=True, text=True)
        rp = tmp / "report.json"
        if not rp.exists():
            sys.exit(f"scan failed for {kind} {iid}")
        rep = json.loads(rp.read_text())
        active = [i for i in rep.get("issues", []) if i.get("severity") in ("HIGH", "CRITICAL")]
        if active:  # write triage entries for the findings still open
            subprocess.run([exe, "baseline", str(target_dir), "--no-llm", "-o", str(tmp / "all.json")], capture_output=True)
            all_fp = json.loads((tmp / "all.json").read_text()).get("fingerprints", []) if (tmp / "all.json").exists() else []
            old = {x["hash"]: x for x in json.loads(triage_path(kind, iid).read_text())} if triage_path(kind, iid).exists() else {}
            groups: dict = {}
            for i in active:
                groups.setdefault((i["id"], i["location"].get("file")), []).append(i)
            seen_n: dict = {}
            entries = []
            for fp in all_fp:
                key = (fp["rule_id"], fp["file"])
                if key not in groups:
                    continue
                n = seen_n.get(key, 0)
                seen_n[key] = n + 1
                g = groups[key]
                f = g[min(n, len(g) - 1)]
                ev = f"L{f['location'].get('start_line')}: {f.get('pattern')}: {' '.join(str(f.get('code_snippet', '')).split())[:200]}"
                entries.append({"hash": fp["hash"], "rule_id": fp["rule_id"], "file": fp["file"],
                                "evidence": ev, "reason": old.get(fp["hash"], {}).get("reason", "")})
            fp_count: dict = {}
            for fp in all_fp:
                fp_count[(fp["rule_id"], fp["file"])] = fp_count.get((fp["rule_id"], fp["file"]), 0) + 1
            old_rules = {(v["rule_id"], v["file"]) for v in old.values() if v.get("as_rule")}
            for key, g in groups.items():
                mine = [e for e in entries if (e["rule_id"], e["file"]) == key]
                reasoned = [e for e in mine if e["reason"]]
                if key in old_rules or (mine and not reasoned):
                    continue  # fingerprint entries still need reasons first
                # identical findings share one fingerprint: offer a file-scoped rule for the repeats
                entries.append({"hash": f"rule:{key[0]}:{key[1]}", "rule_id": key[0], "file": key[1], "as_rule": True,
                                "message": f"*{g[0].get('pattern', '')}*", "evidence": f"{len(g)}x, first L{g[0]['location'].get('start_line')}: {' '.join(str(g[0].get('code_snippet', '')).split())[:160]}",
                                "reason": ""})
            kept = [v for h, v in old.items() if h not in {e["hash"] for e in entries} and v.get("reason")]
            triage_path(kind, iid).write_text(dumps(kept + entries) + "\n")
        sev = {}
        for i in rep.get("issues", []):
            sev[i.get("severity")] = sev.get(i.get("severity"), 0) + 1
        ra = rep.get("risk_assessment", {})
        rec = {
            "kind": kind, "id": iid, "target": audit_target(kind, item), "scope": scope,
            "scanner": f"skillspector {rep.get('metadata', {}).get('skillspector_version', version)}",
            "mode": "static (--no-llm) + Claude review of triage",
            "raw_score": ra.get("score"), "raw_recommendation": ra.get("recommendation"),
            "active_by_severity": sev, "active_high_critical": len(active),
            "suppressed": rep.get("suppressed_count", 0),
            "completeness": rep.get("analysis_completeness", {}).get("status"),
            "verdict": "pass" if not active and rep.get("execution_successful", True) else "fail",
            "open_findings": [f"{i['id']} {i['location'].get('file')}:{i['location'].get('start_line')} {i.get('pattern')}" for i in active][:50],
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        }
        rec_path(kind, iid).write_text(dumps(rec) + "\n")
        return rec


def audit_errors(reg: dict, plan: "Plan") -> list[str]:
    e = []
    for kind, item in audit_items(reg):
        rec = read_record(kind, item["id"])
        label = f"{kind} '{item['id']}'"
        if not rec:
            e.append(f"{label}: no audit record (run: kit.py audit {item['id']})")
            continue
        if rec.get("target") != audit_target(kind, item, plan):
            e.append(f"{label}: audit is stale, content or pin changed since the scan (run: kit.py audit --stale)")
        if rec.get("verdict") not in ("pass", "manual"):
            e.append(f"{label}: audit FAILED with {rec.get('active_high_critical')} open HIGH/CRITICAL finding(s); triage {triage_path(kind, item['id']).relative_to(ROOT)}")
        tp = triage_path(kind, item["id"])
        if tp.exists():
            for t in json.loads(tp.read_text()):
                if t.get("as_rule") and (not t.get("file") or t.get("message", "*") == "*"):
                    e.append(f"{label}: as_rule triage for {t.get('rule_id')} needs a specific message glob, not '*'")
                r = t.get("reason", "").strip()
                if r and (len(r) < MIN_REASON or r.lower().strip(". ") in GENERIC):
                    e.append(f"{label}: triage reason for {t.get('rule_id')} in {t.get('file')} is too vague; say why it is a false positive")
    known = {f"{k}-{i['id']}" for k, i in audit_items(reg)}
    if AUDITS.is_dir():
        for f in AUDITS.glob("*.json"):
            stem = f.name.removesuffix(".triage.json").removesuffix(".json")
            if stem not in known:
                e.append(f"orphan audit file audits/{f.name}")
    return e


def cmd_audit(a) -> None:
    reg = load()
    errs = validate(reg)
    if errs:
        fail(errs)
    AUDITS.mkdir(exist_ok=True)
    lock = json.loads(LOCK.read_text()) if LOCK.exists() else {}
    plan, _, _ = plan_build(reg, lock)
    if [f for f in plan.stale() if f != "CATALOG.md"]:
        sys.exit("generated files are stale: run kit.py build first, then audit")
    items = audit_items(reg)
    if a.id:
        items = [(k, i) for k, i in items if i["id"] == a.id]
        if not items:
            sys.exit(f"nothing called '{a.id}' in kit.toml")
    elif a.stale:
        items = [(k, i) for k, i in items
                 if not (r := read_record(k, i["id"])) or r.get("target") != audit_target(k, i, plan) or r.get("verdict") == "fail"]
    exe = ensure_scanner(reg) if any(not (k == "mcp" and not npx_package(i)) for k, i in items) else ""
    failed = 0
    for kind, item in items:
        rec = audit_one(reg, exe, kind, item)
        mark = {"pass": "✓", "manual": "•"}.get(rec["verdict"], "✗")
        failed += rec["verdict"] == "fail"
        extra = f"raw {rec.get('raw_score')}/100, open H/C {rec.get('active_high_critical')}, suppressed {rec.get('suppressed')}" if rec["verdict"] != "manual" else "manual review"
        print(f"  {mark} {kind:<6} {item['id']:<30} {extra}")
        if rec["verdict"] == "fail":
            print(f"      triage: {triage_path(kind, item['id']).relative_to(ROOT)}")
    print(f"\n{len(items)} audited, {failed} need triage." if items else "nothing to audit")
    if failed:
        print("For each triage entry: read the evidence in context. False positive -> write a specific reason (>= 20 chars). "
              "Real risk -> REFUSE the item. Then: kit.py audit --stale")
        sys.exit(1)


# ── commands ─────────────────────────────────────────────────

def fail(errors: list[str]) -> None:
    print("✗ kit.toml has problems:\n" + "\n".join(f"  - {x}" for x in errors))
    sys.exit(1)


def cmd_build(_) -> None:
    reg = load()
    errs = validate(reg)
    if errs:
        fail(errs)
    lock = json.loads(LOCK.read_text()) if LOCK.exists() else {}
    plan, new_lock, changed = plan_build(reg, lock)
    touched = plan.stale()
    plan.apply()
    print("✓ build ok")
    for f in touched:
        print(f"  updated {f}")
    for p in changed:
        print(f"  {p} -> {new_lock['plugins'][p]['version']}")


def cmd_check(_) -> None:
    reg = load()
    errs = validate(reg)
    if errs:
        fail(errs)
    lock = json.loads(LOCK.read_text()) if LOCK.exists() else {}
    plan, _, _ = plan_build(reg, lock)
    stale = plan.stale()
    if stale:
        fail([f"stale generated file: {f}" for f in stale] + ["run: python scripts/kit.py build"])
    errs = audit_errors(reg, plan)
    if errs:
        fail(errs)
    print("✓ check ok (registry, generated files, audits)")


def cmd_new_skill(a) -> None:
    reg = load()
    if a.plugin not in reg.get("plugins", {}):
        sys.exit(f"unknown plugin '{a.plugin}'. Options: {', '.join(reg.get('plugins', {}))}")
    if not ID_RE.match(a.id):
        sys.exit("id must be lowercase-hyphen")
    if any(s["id"] == a.id for s in reg.get("skill", [])):
        sys.exit(f"skill '{a.id}' already exists")
    d = ROOT / "plugins" / a.plugin / "skills" / a.id
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(
        f"---\nname: {a.id}\ndescription: generated from kit.toml\n---\n\n# {a.id}\n\n"
        "## Goal\n\n## Steps\n\n1. \n\n## Rules\n\n## Output\n", encoding="utf-8")
    with REG.open("a", encoding="utf-8") as f:
        f.write(f'\n[[skill]]\nid = "{a.id}"\nplugin = "{a.plugin}"\nsource = "local"\n'
                f'summary = "{PLACEHOLDER}"\nwhen = "{PLACEHOLDER}"\nnot_when = "{PLACEHOLDER}"\n')
    print(f"✓ scaffolded {d.relative_to(ROOT)} and registered it in kit.toml (fill the {PLACEHOLDER}s, then build)")


def git(*args: str, cwd: str | None = None) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def vendor_one(s: dict) -> None:
    m = GH_RE.match(s.get("source", ""))
    if not m:
        sys.exit(f"skill '{s['id']}' is not a github source")
    repo, ref, sub = m.groups()
    with tempfile.TemporaryDirectory() as tmp:
        git("init", "-q", cwd=tmp)
        git("remote", "add", "origin", f"https://github.com/{repo}", cwd=tmp)
        git("fetch", "-q", "--depth", "1", "origin", ref or "HEAD", cwd=tmp)
        git("checkout", "-q", "FETCH_HEAD", cwd=tmp)
        commit = git("rev-parse", "HEAD", cwd=tmp)
        src = Path(tmp) / sub.strip("/")
        if not (src / "SKILL.md").is_file():
            sys.exit(f"{repo}:{sub} has no SKILL.md")
        dst = skill_dir(s)
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git"))
        if not any(dst.glob("LICENSE*")):
            for lic in sorted(Path(tmp).glob("LICENSE*")):
                shutil.copy(lic, dst / lic.name)
                break
        (dst / ".upstream.json").write_text(dumps({
            "repo": repo, "ref": ref or "HEAD", "path": sub, "commit": commit,
        }) + "\n", encoding="utf-8")
    print(f"✓ vendored {s['id']} @ {commit[:8]}")


def cmd_vendor(a) -> None:
    reg = load()
    targets = [s for s in reg.get("skill", []) if s.get("source", "").startswith("github:")]
    if not a.all:
        targets = [s for s in targets if s["id"] == a.id]
        if not targets:
            sys.exit(f"no vendored skill '{a.id}' in kit.toml")
    for s in targets:
        vendor_one(s)
    print("next: python scripts/kit.py build")


def remote_head(repo: str) -> str:
    try:
        return git("ls-remote", f"https://github.com/{repo}", "HEAD").split()[0]
    except Exception:
        return "unreachable"


def cmd_drift(_) -> None:
    reg = load()
    rows = []
    for s in reg.get("skill", []):
        m = GH_RE.match(s.get("source", ""))
        if not m:
            continue
        up = skill_dir(s) / ".upstream.json"
        have = json.loads(up.read_text())["commit"] if up.exists() else "missing"
        rows.append((f"skill {s['id']}", m.group(1), have))
    for x in reg.get("external", []):
        rows.append((f"plugin {x['id']}", x["repo"], x.get("sha", "unpinned")))
    cache: dict[str, str] = {}
    behind = 0
    for name, repo, have in rows:
        head = cache.setdefault(repo, remote_head(repo))
        state = "ok" if head.startswith(have[:12]) else ("UNPINNED" if have == "unpinned" else "behind")
        behind += state != "ok"
        print(f"  {state:<9} {name:<32} {have[:8]:<9} -> {head[:8]}  {repo}")
    print(f"\n{behind} item(s) not at upstream HEAD. Review upstream changes before updating any of them.")


def cmd_list(_) -> None:
    reg = load()
    for pname, p in reg.get("plugins", {}).items():
        print(f"\n{pname}: {p['description']}")
        for s in reg.get("skill", []):
            if s["plugin"] == pname:
                print(f"  skill    {s['id']:<24} {s.get('source', 'local')}")
        for m in reg.get("mcp", []):
            if m["plugin"] == pname:
                print(f"  mcp      {m['id']}")
        for x in reg.get("external", []):
            if x["attach"] == pname:
                print(f"  plugin   {x['id']:<24} github:{x['repo']}")
    print("\nprofiles: " + ", ".join(f"{k}={'+'.join(v)}" for k, v in reg.get("profiles", {}).items()))


# ── embed (optional): copy the kit into a project's .claude/ ──
# The marketplace is the default install path. embed exists for private add-on repos that a
# session cannot fetch as a marketplace: their content is copied into the project instead.

EMBED_DIR = Path(".claude") / "kit"
EMBED_MARK = "/.claude/kit/hooks/"
# never needed at runtime; keeps project repos small
EMBED_SKIP = (".git", ".done", "skills", "node_modules", "tests", "docs", "benchmarks", "examples",
              "research", "assets", "*.png", "*.jpg", "*.gif", "*.webp", "*.mp4")


def fetch_external(x: dict) -> Path:
    """Checkout an external plugin at its pinned sha; return the plugin root."""
    cache = Path.home() / ".cache" / "claude-kit" / "ext" / f"{x['id']}-{x['sha'][:12]}"
    if not (cache / ".done").is_file():
        if cache.exists():
            shutil.rmtree(cache)
        cache.mkdir(parents=True)
        git("init", "-q", cwd=str(cache))
        git("fetch", "-q", "--depth", "1", f"https://github.com/{x['repo']}", x["sha"], cwd=str(cache))
        git("checkout", "-q", "FETCH_HEAD", cwd=str(cache))
        (cache / ".done").write_text(x["sha"])
    root = cache
    mp = cache / ".claude-plugin" / "marketplace.json"
    if mp.is_file():
        plugins = json.loads(mp.read_text(encoding="utf-8")).get("plugins", [])
        hit = [p for p in plugins if p.get("name") == x["id"]] or plugins[:1]
        if hit and isinstance(hit[0].get("source"), str):
            root = (cache / hit[0]["source"]).resolve()
    if not (root / ".claude-plugin" / "plugin.json").is_file():
        sys.exit(f"external '{x['id']}': no .claude-plugin/plugin.json at {root}")
    return root


def plugin_parts(root: Path) -> dict:
    """Resolve a plugin's skills, commands, agents, hooks and MCP servers."""
    man = json.loads((root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))

    def dirs(key: str, default: str) -> list[Path]:
        v = man.get(key, default)
        return [root / p for p in (v if isinstance(v, list) else [v]) if isinstance(p, str)]

    def obj(key: str, default: str, inner: str) -> dict:
        v = man.get(key, default)
        if isinstance(v, dict):
            return v.get(inner, v)
        f = root / v
        return json.loads(f.read_text(encoding="utf-8")).get(inner, {}) if f.is_file() else {}

    return {
        "skills": [d for p in dirs("skills", "skills") if p.is_dir()
                   for d in sorted(p.iterdir()) if (d / "SKILL.md").is_file()],
        "commands": [f for p in dirs("commands", "commands") if p.is_dir() for f in sorted(p.glob("*.md"))],
        "agents": [f for p in dirs("agents", "agents") if p.is_dir() for f in sorted(p.glob("*.md"))],
        "hooks": obj("hooks", "hooks/hooks.json", "hooks"),
        "mcp": obj("mcpServers", ".mcp.json", "mcpServers"),
    }


def cmd_embed(a) -> None:
    reg = load()
    proj = Path(a.project).resolve()
    kdir = proj / EMBED_DIR
    meta_f = kdir / "kit.json"
    old = json.loads(meta_f.read_text(encoding="utf-8")) if meta_f.is_file() else {}
    profile = a.profile or old.get("profile")
    if not profile:
        sys.exit("embed needs --profile the first time (" + ", ".join(reg.get("profiles", {})) + ")")
    if profile not in reg.get("profiles", {}):
        sys.exit(f"unknown profile '{profile}'")
    extras = sorted(set(old.get("extras", [])) | set(a.add or []))
    wanted = list(dict.fromkeys(reg["profiles"][profile] + extras))
    local = set(reg.get("plugins", {}))
    ext = {x["id"]: x for x in reg.get("external", [])}
    for pid in wanted:
        if pid not in local and pid not in ext:
            sys.exit(f"unknown plugin '{pid}'")

    # 1. remove everything the previous embed wrote
    for rel in old.get("files", []):
        p = proj / rel
        if p.is_symlink() or p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)
    for sub_ in ("plugins", "hooks"):
        if (kdir / sub_).exists():
            shutil.rmtree(kdir / sub_)
        (kdir / sub_).mkdir(parents=True)

    files: list[str] = []
    hooks: dict[str, list] = {}
    mcp: dict[str, dict] = {}
    seen: dict[str, str] = {}
    installed: dict[str, str] = {}

    def claim(kind: str, name: str, pid: str) -> None:
        key = f"{kind}:{name}"
        if key in seen:
            sys.exit(f"embed: {kind} '{name}' is shipped by both {seen[key]} and {pid}")
        seen[key] = pid

    for pid in wanted:
        if pid in local:
            src, ver = ROOT / "plugins" / pid, json.loads(
                (ROOT / "plugins" / pid / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")).get("version", "")
        else:
            src, ver = fetch_external(ext[pid]), ext[pid]["sha"][:12]
        installed[pid] = ver
        parts = plugin_parts(src)
        dst = kdir / "plugins" / pid
        # plugin root minus its skills; skills/ points at .claude/skills so hook paths still resolve
        shutil.copytree(src, dst, symlinks=True,
                        ignore=shutil.ignore_patterns(*EMBED_SKIP))
        if parts["skills"]:
            rel_skills = parts["skills"][0].parent.relative_to(src)
            link = dst / rel_skills
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(Path("../" * len(link.relative_to(proj / ".claude").parts[:-1])) / "skills")
        for s in parts["skills"]:
            claim("skill", s.name, pid)
            out = proj / ".claude" / "skills" / s.name
            if out.exists():
                sys.exit(f"embed: .claude/skills/{s.name} already exists and is not managed by the kit")
            shutil.copytree(s, out, symlinks=True, ignore=shutil.ignore_patterns(".git"))
            files.append(f".claude/skills/{s.name}")
        for kind, items in (("commands", parts["commands"]), ("agents", parts["agents"])):
            for f in items:
                claim(kind, f.name, pid)
                out = proj / ".claude" / kind / f.name
                if out.exists():
                    sys.exit(f"embed: .claude/{kind}/{f.name} already exists and is not managed by the kit")
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(f, out)
                files.append(f".claude/{kind}/{f.name}")
        # settings.json hooks may not use ${CLAUDE_PLUGIN_ROOT}: each plugin hook runs through a wrapper
        n = 0
        for event, groups in parts["hooks"].items():
            for g in groups:
                g = json.loads(json.dumps(g))
                for h in g.get("hooks", []):
                    if h.get("type") != "command":
                        continue
                    n += 1
                    wrapper = kdir / "hooks" / f"{pid}-{n}.sh"
                    wrapper.write_text(
                        "#!/usr/bin/env bash\n# generated by claude-kit embed\n"
                        f'export CLAUDE_PLUGIN_ROOT="$CLAUDE_PROJECT_DIR/.claude/kit/plugins/{pid}"\n'
                        f"{h['command']}\n", encoding="utf-8")
                    h["command"] = f'bash "$CLAUDE_PROJECT_DIR{EMBED_MARK}{wrapper.name}"'
                    h.pop("shell", None)
                hooks.setdefault(event, []).append(g)
        for name, server in parts["mcp"].items():
            claim("mcp", name, pid)
            mcp[name] = json.loads(json.dumps(server).replace(
                "${CLAUDE_PLUGIN_ROOT}", f"${{CLAUDE_PROJECT_DIR}}/.claude/kit/plugins/{pid}"))

    # 2. settings.json: drop old kit hooks and marketplace entries, add ours, keep the rest
    sf = proj / ".claude" / "settings.json"
    settings = json.loads(sf.read_text(encoding="utf-8")) if sf.is_file() else {}
    settings.get("extraKnownMarketplaces", {}).pop("sufian-kit", None)
    settings["enabledPlugins"] = {k: v for k, v in settings.get("enabledPlugins", {}).items()
                                  if not k.endswith("@sufian-kit")}
    for k in ("extraKnownMarketplaces", "enabledPlugins"):
        if not settings.get(k):
            settings.pop(k, None)
    cur = settings.get("hooks", {})
    for event in list(cur):
        cur[event] = [g for g in cur[event]
                      if not any("/.claude/kit/" in h.get("command", "") for h in g.get("hooks", []))]
    for event, groups in hooks.items():
        cur.setdefault(event, []).extend(groups)
    settings["hooks"] = {k: v for k, v in cur.items() if v}
    if mcp:
        settings["enableAllProjectMcpServers"] = True
    sf.parent.mkdir(parents=True, exist_ok=True)
    sf.write_text(dumps(settings) + "\n", encoding="utf-8")

    # 3. .mcp.json: replace the servers the kit owns, keep the rest
    mf = proj / ".mcp.json"
    mdoc = json.loads(mf.read_text(encoding="utf-8")) if mf.is_file() else {}
    servers = {k: v for k, v in mdoc.get("mcpServers", {}).items() if k not in old.get("mcp", [])}
    servers.update(mcp)
    if servers:
        mdoc["mcpServers"] = servers
        mf.write_text(dumps(mdoc) + "\n", encoding="utf-8")
    elif mf.is_file() and set(mdoc) <= {"mcpServers"}:
        mf.unlink()

    try:
        commit = git("rev-parse", "HEAD", cwd=str(ROOT))
    except Exception:
        commit = "unknown"
    (kdir / "README.md").write_text(
        "# claude-kit (embedded)\n\nManaged by `sufianweb3/claude-kit`. Do not edit anything listed in `kit.json`:\n"
        "it is replaced every time `kit.py embed` runs again. Project-specific skills and commands can live next to it in\n"
        "`.claude/skills/` and `.claude/commands/` under other names.\n", encoding="utf-8")
    meta = {"profile": profile, "extras": extras, "kit_commit": commit, "plugins": installed,
            "mcp": sorted(mcp), "files": sorted(files)}
    meta_f.write_text(dumps(meta) + "\n", encoding="utf-8")
    changed = old.get("kit_commit") != commit or old.get("plugins") != installed
    print(f"✓ embedded kit {commit[:8]} into {proj.name}: profile {profile}"
          + (f" + {', '.join(extras)}" if extras else "")
          + f", {len([f for f in files if '/skills/' in f])} skills, {len(mcp)} MCP servers"
          + ("" if changed or not old else " (no change)"))


def main() -> None:
    ap = argparse.ArgumentParser(description="Kit manager")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build").set_defaults(fn=cmd_build)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    sub.add_parser("drift").set_defaults(fn=cmd_drift)
    au = sub.add_parser("audit")
    au.add_argument("id", nargs="?")
    au.add_argument("--stale", action="store_true", help="only items with no, stale or failing records")
    au.add_argument("--all", action="store_true")
    au.set_defaults(fn=cmd_audit)
    n = sub.add_parser("new-skill")
    n.add_argument("id")
    n.add_argument("-p", "--plugin", required=True)
    n.set_defaults(fn=cmd_new_skill)
    v = sub.add_parser("vendor")
    v.add_argument("id", nargs="?")
    v.add_argument("--all", action="store_true")
    v.set_defaults(fn=cmd_vendor)
    e = sub.add_parser("embed", help="optional: copy the kit into a project's .claude/ (for private add-on repos; marketplace is the default)")
    e.add_argument("project")
    e.add_argument("--profile", help="required the first time, remembered in .claude/kit/kit.json")
    e.add_argument("--add", action="append", help="extra plugin, e.g. --add cloudflare")
    e.set_defaults(fn=cmd_embed)
    a = ap.parse_args()
    if a.cmd == "vendor" and not (a.id or a.all):
        ap.error("vendor needs an id or --all")
    a.fn(a)


if __name__ == "__main__":
    main()
