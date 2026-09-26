# Setting up a project with claude-kit (Claude Code web)

Setup takes **two sessions** because Claude Code only loads plugins when a session starts. In session 1 the project has no `.claude/settings.json` yet, so the kit is not loaded and `/kit-init` does not exist. Session 1 installs the settings and session 2 is where the kit runs.

Web sessions run in a throwaway container. **Anything not committed and pushed is lost when the session ends.**

## Before you start (once)

- `sufianweb3/claude-kit` must be **public** and its default branch must be `main`.
- The new project repo exists on GitHub (it can be empty) and is connected to Claude Code web.
- Pick a profile:

| Profile | For |
|---|---|
| `website` | Marketing or landing site |
| `webapp` | SaaS or web app |
| `app` | Mobile or desktop app |
| `extension` | Browser extension |
| `api` | Backend or API |

## Session 1: install the kit

Open a new Claude Code web session on the **project repo**, attach your PRD file if you have one, and paste this (replace `<profile>`):

```text
Set up this repo to use my claude-kit. Follow these steps exactly and do not build anything yet.

1. Fetch https://raw.githubusercontent.com/sufianweb3/claude-kit/main/install/profiles/<profile>.json
   and save it as .claude/settings.json. If .claude/settings.json already exists, merge the
   "extraKnownMarketplaces" and "enabledPlugins" keys in and keep every existing key.
2. If I attached a PRD, save it unchanged as docs/PRD.md. Do not write REQUIREMENTS yet.
3. Do not create or edit CLAUDE.md. /kit-init adds the kit block in the next session.
4. Commit with "chore(kit): install claude-kit (<profile>)" and push to main
   (the default branch). Confirm the push succeeded with git ls-remote.
5. Tell me: "Kit installed. Start a NEW session on this repo and run /kit-init <profile>."
```

If the fetch fails (404), the kit repo is private or not on `main`. Fix that first.

## Session 2: initialise the project

Open a **new** session on the same project repo. Check that the session start prints the kit's routing tables and that `/kit-init` appears in the `/` menu. Then send:

```text
/kit-init <profile>
```

It creates `docs/context/`, adds the kit block to `CLAUDE.md`, fills STATE and commits. Answer its `[ASK]` questions. Then send:

```text
Run intake using docs/PRD.md as the source. Write docs/context/REQUIREMENTS.md as a DRAFT,
ask only questions that change the build, then stop for my approval.
Commit and push when I approve.
```

Reply "yes" (or your corrections) to confirm REQUIREMENTS. Now describe what to build first.

## Every session after that

| When | Say |
|---|---|
| Start | Nothing special. The kit prints STATE, HANDOFF and open requirements |
| A choice is settled | `/decide <the choice>` |
| Stopping for the day | `/handoff` (saves memory, commits **and pushes**) |
| A milestone is done | `/close` (verifies every requirement, prints a KIT PROPOSAL) |
| Lessons to keep | Paste the KIT PROPOSAL into a session on `claude-kit` |

Never close a session with unpushed work. If unsure, say: *"Commit and push everything to main."*

## If the kit does not load in session 2

No routing tables at session start and no `/kit-init`? Use the fallback. In a session on the project, send:

```text
Fetch https://raw.githubusercontent.com/sufianweb3/claude-kit/main/install/sync-kit.sh into
.claude/sync-kit.sh and add this SessionStart hook to .claude/settings.json (keep existing keys):
{ "hooks": { "SessionStart": [ { "hooks": [ { "type": "command",
  "command": "bash .claude/sync-kit.sh core <plugins for my profile>" } ] } ] } }
Plugins per profile: website = core design, webapp = core build design,
app = core build design, extension = core build, api = core build.
Commit and push to main.
```

Then start a new session and continue with session 2.
