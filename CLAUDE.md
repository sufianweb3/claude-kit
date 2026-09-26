# claude-kit (maintainer session)

This repo is a Claude Code **plugin marketplace**. Every project the user builds pulls its skills, MCPs and routing from here.

**For any change to skills, MCPs, plugins, profiles or routing: load the `kit-maintainer` skill first and follow it.**

## Layout

| Path | What | Edit? |
|---|---|---|
| `kit.toml` | Registry: placement, routing, MCPs, externals, profiles | ✅ source of truth |
| `plugins/<p>/skills/<id>/` | Skill bodies and their references/scripts | ✅ body only (frontmatter is generated) |
| `plugins/core/hooks/session-start.sh`, `plugins/core/commands/`, `plugins/core/LEARNINGS.md` | Core behaviour + global learnings | ✅ |
| `plugins/*/skills/<vendored>/` (has `.upstream.json`) | Third-party skills | ❌ only via `kit.py vendor` |
| `audits/*.json` | Scan records | ❌ written by `kit.py audit` |
| `audits/*.triage.json` | Reviewed false positives | ✅ `reason` fields only |
| `plugins/<p>/agents/` | Subagents | ✅ body + model/tools |
| `scripts/kit.py` | Build, check, vendor, scaffold | ✅ carefully |
| `.claude-plugin/`, `plugins/*/.claude-plugin/`, `plugins/*/.mcp.json`, `plugins/*/INDEX.md`, `plugins/*/hooks/hooks.json`, `install/profiles/`, `CATALOG.md`, `kit.lock.json` | Generated | ❌ never |

## Commands

```bash
python scripts/kit.py list                 # what's in the kit
python scripts/kit.py new-skill <id> -p <plugin>
python scripts/kit.py vendor <id> | --all  # fetch/refresh github-sourced skills
python scripts/kit.py build                # regenerate + auto-bump versions
python scripts/kit.py check                # must pass before every commit (CI enforces)
                                           # also fails on any term in .kit-private-terms (local, gitignored)
                                           # or, if absent, the PRIVATE_TERMS env var (CI secret); whole word, case-sensitive if the term has a capital
python scripts/kit.py drift                # pinned upstreams vs their latest commit
python scripts/kit.py audit <id> | --stale # SkillSpector scan + triage gate (see kit-maintainer)
```

## Style
- Reply short: what changed, plugin + version, env vars needed, projects affected.
- No em dashes. No comma before "and" in lists.
