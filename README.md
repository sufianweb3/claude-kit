# claude-kit

One repo that feeds every project: skills, MCP servers, external plugins, routing rules and the project memory layer. Push here, every project picks it up next session.

## How it works

| Piece | What it does |
|---|---|
| `kit.toml` | Single registry. Where each skill/MCP lives, **when** to use it and **when not to** |
| `scripts/kit.py build` | Generates the marketplace, plugin manifests, MCP configs, router tables and profiles from `kit.toml`. Auto-bumps versions so projects actually update |
| **Plugins** | `core` (always), `build` (intake → deploy pipeline), `design` (creative process, standards, motion). Projects switch on only what they need |
| **Router** | Each enabled plugin prints its "Use when / Not for" table at session start, so Claude picks the right skill or MCP on its own |
| **Project memory** | `docs/context/`: STATE, REQUIREMENTS, DECISIONS, HANDOFF, LEARNINGS. Printed at session start; `/decide`, `/handoff`, `/close` |
| **Supply chain** | Third-party skills vendored and external plugins pinned to a commit sha. `kit.py drift` shows what is behind; updates are reviewed diffs |
| **Memory of no** | `[[rejected]]` in kit.toml blocks re-adding things already turned down, with the reason |
| **Audit gate** | Every skill, subagent, plugin and MCP is scanned by NVIDIA SkillSpector (pinned) and every HIGH/CRITICAL finding needs a written review. Records in `audits/`, summary in `CATALOG.md` |
| **Subagents** | `auditor` (opus, read-only), `scout` (haiku, read-only), `visual-qa` (sonnet + playwright). Used only where a fresh context pays |
| **Guardrails** | `kit.py check` + GitHub Action block broken registries, stale generated files, vague routing, orphan folders, inline secrets, unpinned MCPs and missing or stale audits. CI also runs a pinned gitleaks scan over the full history. Locally, `check` fails on any term listed in `.kit-private-terms` (gitignored). Weekly full rescan |

## Setup (once)

1. Create an empty **public** repo `sufianweb3/claude-kit` on GitHub (no README).
2. Unzip, then from Git Bash inside the folder:
   ```bash
   git init && git add . && git commit -m "init kit"
   git branch -M main
   git remote add origin https://github.com/sufianweb3/claude-kit.git
   git push -u origin main
   ```
   Do not use the GitHub web uploader: it caps at 100 files and the kit has more.
3. Open Claude Code web on `claude-kit`. That session is your **maintainer**. First message: *"Run kit.py check and confirm the kit is healthy."*

## New project

1. Copy `install/profiles/<profile>.json` into the project as `.claude/settings.json`
   Profiles: `website`, `webapp`, `app`, `extension`, `api`. Cloudflare projects also enable `cloudflare@sufian-kit` (`/kit-init` asks).
2. Start a session and run `/kit-init`. It creates `docs/context/`, the CLAUDE.md block and fills STATE from the repo.

## Daily use

| You | Where |
|---|---|
| "Add this skill: <github link>" / "add an MCP for X" / "Claude keeps using X for Y" (audited automatically) | Maintainer session |
| `/decide <choice>` when something is settled | Project session |
| `/handoff` when stopping | Project session |
| `/close` at a milestone: verifies every requirement, collects lessons as a KIT PROPOSAL | Project session |
| Paste the KIT PROPOSAL / "check for updates" | Maintainer session |

## Fallback (if a web session does not load marketplace plugins)

Copy `install/sync-kit.sh` to the project's `.claude/` and add to `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "bash .claude/sync-kit.sh core design" }] }
    ]
  }
}
```
