# AGENTS.md

This repo is **claude-kit itself**: a Claude Code plugin marketplace that other projects install. It is not an app, and changes here reach every project that uses the kit at its next session.

- Read [CLAUDE.md](CLAUDE.md) first. For any change to skills, MCPs, plugins, profiles or routing, load the `kit-maintainer` skill in `.claude/skills/kit-maintainer/SKILL.md` and follow it.
- `kit.toml` is the source of truth. `scripts/kit.py` (Python 3.11+) generates everything listed below from it.
- Work on a branch and open a pull request. Do not push to `main`.

## Never edit by hand (generated)

- `.claude-plugin/marketplace.json`
- `plugins/*/.claude-plugin/plugin.json`
- `plugins/*/.mcp.json`
- `plugins/*/INDEX.md`
- `plugins/*/hooks/hooks.json`
- `install/profiles/*.json`
- `CATALOG.md`
- `kit.lock.json`

Also hands off: vendored skill folders (they contain `.upstream.json`; change them only with `kit.py vendor`) and `audits/*.json` (only the `reason` fields in `audits/*.triage.json` are hand-edited). The `name` and `description` frontmatter of every `SKILL.md` is generated too; edit the body only.

## Ship steps (every change)

```bash
python scripts/kit.py build          # regenerate files and bump changed plugin versions
python scripts/kit.py audit --stale  # SkillSpector scan of anything changed; triage every HIGH/CRITICAL finding
python scripts/kit.py build          # refresh the audit table in CATALOG.md
python scripts/kit.py check          # must print "check ok"; CI runs the same check plus gitleaks
```

The scanner needs Python 3.12 or newer. Never suppress a finding you have not read, and never put secrets anywhere in the repo.
