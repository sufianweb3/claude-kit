# FAQ

## 1. What is claude-kit?

A Claude Code plugin marketplace. A project turns it on with one `.claude/settings.json` file and then gets skills, MCP servers and subagents that Claude picks automatically from router tables, plus a memory layer in `docs/context/` that carries state, requirements, decisions and handoff notes between sessions. See the [README](../README.md) for what each plugin adds.

## 2. Do I need Claude Code?

Yes. The kit is made of Claude Code plugins: the router tables print from a SessionStart hook, the commands are Claude Code slash commands and the subagents run on Claude Code's Task tool. Other tools can read the `SKILL.md` files as plain Markdown, but nothing is routed or loaded for them.

## 3. Claude Code on the web or the CLI?

Both work, because the kit uses standard plugins. It is written for the web: each web session runs in a throwaway container, so the kit pushes work to the session's working branch before it ends, and [SETUP.md](../SETUP.md) walks through the web flow. In the CLI you can add the marketplace with `/plugin marketplace add sufianweb3/claude-kit` or use the same profile file. The hooks run `bash`, so on Windows use Git Bash or WSL.

## 4. How do I add a skill?

Open a Claude Code session on this repo and say what you want, for example "Add this skill: <github link>" or "add an MCP for X". The `kit-maintainer` skill then checks overlap and the rejected list, reviews the source, pins it to a full commit sha, vendors it, runs the SkillSpector audit, rebuilds and runs `kit.py check`. For a skill written from scratch it uses `python scripts/kit.py new-skill <id> -p <plugin>`. Either way the change lands as a pull request.

## 5. How do updates reach projects?

`kit.py build` bumps the version of every plugin whose content changed. Once the change is merged into `main`, projects pick it up at their next session start: a web session installs the plugins fresh from the marketplace each time, and in the CLI you run `/plugin marketplace update sufian-kit`. Nothing changes inside a session that is already running.

## 6. How do audits work?

Every skill, subagent, companion plugin and MCP is scanned by NVIDIA SkillSpector at a pinned version (static mode). Each HIGH or CRITICAL finding must be reviewed: a false positive gets a specific written reason, and a real risk means the item is refused and added to the rejected list. Records live in `audits/`. `kit.py check` fails when a record is missing, failing or stale because the content or pin changed, and CI rescans everything weekly. Current status is in [CATALOG.md](../CATALOG.md).

## 7. What data does it store?

The kit runs no service of its own. In a project it writes `.claude/settings.json`, a marked block in `CLAUDE.md` and the files in `docs/context/`, all committed to the project's own repo. If that repo is public, `docs/context/` is public too, and the kit is told never to store credentials, client personal data or contract terms there. MCP servers can reach the network when used: `context7` queries its documentation service and `playwright` drives a local browser.

## 8. How do I remove it from a project?

On a working branch:
1. Remove `sufian-kit` from `extraKnownMarketplaces` and every `*@sufian-kit` entry from `enabledPlugins` in `.claude/settings.json`.
2. Delete the block between `<!-- kit:start` and `<!-- kit:end -->` in `CLAUDE.md`.
3. Delete `docs/context/` if you no longer want the notes.

Merge the branch and start a new session. If the kit was copied in with `kit.py embed`, also delete `.claude/kit/`, every path listed in `.claude/kit/kit.json` under `files`, the hooks whose command contains `/.claude/kit/` and the kit's servers in `.mcp.json` and `enabledMcpjsonServers`.
