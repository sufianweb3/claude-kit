---
name: kit-maintainer
description: Maintains this kit repo safely. Use for ANY request to add, change, move, update, remove, import or audit a skill, MCP server, external plugin, profile, routing rule or global learning in claude-kit, including casual phrasing like "add this skill", "here's a repo I found", "stop using X for Y", "Claude keeps picking the wrong skill", "update everything", a pasted GitHub link or a pasted KIT PROPOSAL block. Not for editing projects that use the kit.
---

# Kit maintainer

You are working **inside the kit repo**. Every project pulls from it, so a broken commit breaks every project. Follow the procedure for the request type and always finish with **Ship**.

## Mental model

```
kit.toml ──(scripts/kit.py build)──► generated files ──► projects
  ▲ you edit                          never edit by hand
  └─ skill folders plugins/<plugin>/skills/<id>/   you edit the BODY of local skills only
```

- `kit.toml` owns placement, routing text (summary / when / not_when / overrides), MCP config, external plugins with pinned sha, profiles and the rejected list.
- `SKILL.md` owns the instructions body. `name` and `description` frontmatter are **overwritten** by build.
- Vendored skills (`source = "github:..."`) are **never hand-edited**. Change their routing in kit.toml; replace them via `vendor`.
- Generated (never edit): `.claude-plugin/marketplace.json`, `plugins/*/.claude-plugin/plugin.json`, `plugins/*/.mcp.json`, `plugins/*/INDEX.md`, `plugins/*/hooks/hooks.json`, `install/profiles/*.json`, `CATALOG.md`, `kit.lock.json`.
- Plugin versions bump automatically when content changes.

## Procedures

### Add anything external (skill, plugin, MCP)
1. **Rejected?** If the id or repo is in `[[rejected]]`, stop and quote the reason. Re-adding needs a new reason and the user's yes.
2. **Security review**, two layers, both required:
   - **Your read** with `references/security-review.md` (triage by shape, capability surface, hooks, egress). Verdict PASS / PASS* / DEFER / REFUSE with its limit.
   - **SkillSpector scan** after the entry exists (step 6): `python scripts/kit.py audit <id>`. See **Audit protocol** below.
3. **Overlap:** `python scripts/kit.py list` + `CATALOG.md`. If an existing entry covers 70%+, propose merge or replace instead. Same job as a local skill → the local skill stays authoritative; add `overrides` on it.
4. **Placement** with `references/placement.md`. **Cost:** every plugin skill description and every MCP loads into every session where its plugin is on. Say the added cost in one line.
5. Pin: `git ls-remote https://github.com/<repo> HEAD` → full sha.
6. Write the entry, then:
   - skill: `[[skill]]` with `source = "github:owner/repo@<sha>:path"` → `python scripts/kit.py vendor <id>`
   - plugin (repo has `.claude-plugin/plugin.json` at root): `[[external]]` with `sha`, `attach`, then add to `[profiles]`
   - MCP: `[[mcp]]`, secrets as `"${VAR}"`; tell the user which env vars to set. One plugin per MCP.
7. Routing text with `references/routing-guide.md`.
8. Get the user's **yes** for anything with hooks, network egress, secrets or shell. Then Ship.

### Add a local skill (from scratch, pasted content or a KIT PROPOSAL)
`python scripts/kit.py new-skill <id> -p <plugin>`, write the body (under 300 lines; long material in `references/` inside the skill), replace the TODOs in kit.toml, Ship. Local skills are scanned too.

### Add a subagent
Only when isolation pays (independent review, bulk reading, screenshot-heavy work). Add `[[agent]]` in kit.toml and `plugins/<plugin>/agents/<id>.md` with `model` and a minimal `tools` list in its frontmatter. Ship.

## Audit protocol (SkillSpector)
Every skill, agent, external plugin and MCP has a record in `audits/`. `kit.py check` fails if a record is missing, stale (content or pin changed) or failing.
1. `python scripts/kit.py audit <id>` (or `--stale` for everything that changed). The scanner installs itself at the pinned version on first use.
2. ✓ means no open HIGH/CRITICAL findings. ✗ writes `audits/<kind>-<id>.triage.json`.
3. For **each** triage entry, open the file at the evidence line and read the context:
   - **False positive** → write a specific `reason` (what the text really does, what you checked). Generic reasons ("fp", "ok", "accepted") are rejected by check.
   - **Real risk** (hidden instructions, exfiltration, unexplained network calls, credential reads, hooks that write outside the plugin) → **REFUSE**: remove the entry, add `[[rejected]]` with the finding, tell the user.
   - **Unsure** → DEFER and ask the user. Never suppress to make the gate pass.
4. Re-run `kit.py audit <id>`. Entries with `as_rule: true` cover repeats of an already reviewed finding in the same file; give them a reason too.
5. The raw score stays in the record for honesty; the gate is "no un-reviewed HIGH/CRITICAL".
6. Scans are static (`--no-llm`); your read is the semantic layer. Big plugins can take minutes: run long scans in the background (`nohup ... &`) and poll.

### Global learning (from a KIT PROPOSAL)
Ask first: would a change to a skill or check make the mistake impossible? If yes, change that instead. Otherwise append one line to `plugins/core/LEARNINGS.md` (keep it under 15 lines total; merge old ones rather than grow).

### Routing problem ("it picks the wrong skill")
Find the two colliding entries. Sharpen **both**: concrete `when`, the other's territory in `not_when`, and `overrides` when one should always win. Global behaviour goes in `[router].rules`.

### Update upstreams
1. `python scripts/kit.py drift` lists what is behind.
2. For each item the user wants updated: review the upstream diff between the pinned sha and HEAD (hooks, scripts, network changes first).
3. Bump the sha in kit.toml, `vendor <id>` for skills, Ship (the audit re-runs because the pin changed; old triage reasons carry over only for identical findings).

### Move / rename / remove
- Move: change `plugin`, `git mv` the folder. Rename: change `id`, `git mv`.
- Remove: delete the block and folder (and profile entries for externals). Offer to add a `[[rejected]]` entry with the reason so it is not re-added later.

### Import from an old setup
`references/import.md`.

### Audit
`list` + `drift` + read every when / not_when. Report overlaps, vague triggers, unpinned externals, skills over 300 lines and plugins whose always-on cost grew. Propose fixes; apply only after a yes.

## Ship (every change)
1. `python scripts/kit.py build`, fix every error.
2. `python scripts/kit.py audit --stale`, triage until everything is ✓.
3. `python scripts/kit.py build` again (refreshes CATALOG audit table).
4. `python scripts/kit.py check` must print `✓ check ok`.
5. Conventional commit: `feat(design): add <id>`, `fix(routing): separate x from y`, `chore(pin): update <id> to <sha8>`.
6. Reply: **What changed** · **Plugin + version** · **Env vars needed** · **Projects affected** (from profiles) · **Audit** (raw score, suppressed count, anything deferred).

## Never
- Edit generated files, vendored skill folders or audit records by hand (triage reasons are the only hand-edited audit field).
- Suppress a finding you did not open and read.
- Put secrets anywhere in the repo.
- Add a skill without `not_when`, or an external without a sha.
- Bulk import. One item per commit.
