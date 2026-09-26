# claude-kit

**What this is:** a Claude Code plugin marketplace that gives every project auto-routed skills, MCP servers and subagents plus a per-project memory layer.

## Who it is for

Anyone who builds several projects with Claude Code (mainly Claude Code on the web) and wants the same skills, rules and memory in each of them.
You install it once per project with one settings file; after that it loads itself at the start of every session.

## What you get

| Part | What it adds | Enabled by |
|---|---|---|
| `core` plugin | Router tables at session start, project memory in `docs/context/`, learning loop, `/kit-init`, `/decide`, `/handoff`, `/close` | Every profile |
| `build` plugin | Intake to deploy pipeline: requirements, recon, planning, tests-first build, audit, debug, deploy, security; `context7` MCP for library docs | `webapp`, `app`, `extension`, `api` |
| `design` plugin | Website and UI process: discovery, reference boards, UI standards, components, motion; `playwright` MCP for visual QA | `website`, `webapp`, `app` |
| Companion plugins | Pinned third-party plugins: `superpowers`, `ponytail`, `taste-skill`; `cloudflare` and `impeccable` are opt-in | Per profile or on request |
| Subagents | `auditor` (independent code review), `scout` (cheap code reader), `visual-qa` (screenshots and motion review) | Come with `build` and `design` |

The full list of skills, versions and profiles is in [CATALOG.md](CATALOG.md).

## Quick start (Claude Code on the web)

1. Copy [`install/profiles/<profile>.json`](install/profiles) into your project as `.claude/settings.json` (profiles: `website`, `webapp`, `app`, `extension`, `api`). Commit it and merge it into `main`.
2. Start a new Claude Code session on the project. The kit's routing tables print at session start.
3. Run `/kit-init <profile>`. It creates `docs/context/`, adds the kit block to `CLAUDE.md` and fills `STATE.md` from the repo.

Step by step, with copy-paste prompts: [SETUP.md](SETUP.md).

## How Claude picks skills

- At session start each enabled plugin prints a router table: every skill, MCP and subagent with a **Use when** and a **Not for** line.
- Claude matches the task against those tables and loads the most specific skill before writing code; MCPs are called only when their row matches.
- **Precedence:** for the same job a kit skill beats a companion plugin skill (for example `planning` over `superpowers:writing-plans`).
- Project files (`CLAUDE.md`, `docs/context/`) override kit defaults when they conflict.

## Daily commands

| Command | What it does |
|---|---|
| `/kit-init <profile>` | One-time setup: memory layer, `CLAUDE.md` block, profile settings |
| `/decide <choice>` | Records a settled decision in `docs/context/DECISIONS.md` so later sessions respect it |
| `/handoff` | Ends a session: updates STATE and HANDOFF, commits and pushes to the working branch |
| `/close` | Ends a milestone: verifies every requirement with evidence and collects lessons as a KIT PROPOSAL |

## Security model

- **Pinned sources:** vendored skills and companion plugins are pinned to a full 40-char commit sha; MCP packages to an exact npm version, run with install scripts disabled. `check` fails otherwise.
- **SkillSpector audits:** every skill, subagent, plugin and MCP is scanned by a pinned NVIDIA SkillSpector; each HIGH or CRITICAL finding needs a written review. Records live in `audits/`.
- **gitleaks:** CI scans the full history and the working tree for secrets on every push, with a pinned and checksum-verified binary.
- **Branch-only pushes:** project sessions push to their working branch only; nothing reaches `main` without your explicit yes.
- **Opt-in risky plugins:** plugins with extra risk (such as `impeccable`, which downloads a native binary) are left out of every default profile.

Accepted risks, audit status and the rejected list are in [CATALOG.md](CATALOG.md).

## Maintaining the kit

Changes to skills, MCPs, plugins, profiles or routing happen in a Claude Code session on this repo. Start with [CLAUDE.md](CLAUDE.md), which points to the `kit-maintainer` skill and the build and check commands. Coding agents: see [AGENTS.md](AGENTS.md).

Questions: [docs/FAQ.md](docs/FAQ.md). For AI assistants: [llms.txt](llms.txt).

## Repo map

| Folder | Contents |
|---|---|
| `.claude/` | The `kit-maintainer` skill used when editing this repo |
| `.claude-plugin/` | Generated marketplace manifest that Claude Code reads |
| `.github/` | CI: `kit.py check`, gitleaks and a weekly audit rescan |
| `audits/` | SkillSpector scan records and reviewed false positives |
| `docs/` | FAQ |
| `install/` | Generated settings profiles to copy into projects |
| `plugins/` | The `core`, `build` and `design` plugins: skills, subagents, commands, hooks and router tables |
| `scripts/` | `kit.py`: build, check, vendor, audit and scaffold |
