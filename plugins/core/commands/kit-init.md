---
description: Bootstrap this repo for the kit (context layer, CLAUDE.md, profile settings)
argument-hint: "[website|webapp|app|extension|api]"
---

Set up this repository for the kit. Profile: **$ARGUMENTS** (if empty, infer from the repo: framework, package.json, a manifest.json for extensions; ask only if truly unclear).

1. Load `context-keeper` and run **Init** with this profile.
2. Ensure `.claude/settings.json` enables the profile: fetch
   `https://raw.githubusercontent.com/sufianweb3/claude-kit/main/install/profiles/<profile>.json`
   and merge it in. Never delete existing keys.
3. Ask one question only if unknown: does it deploy to Cloudflare? If yes, also enable `cloudflare@sufian-kit`.
4. Fill STATE from the repo; unknowns become `[ASK]`.
5. Commit `chore(kit): init context layer (<profile>)` and push to the default branch. Confirm with `git ls-remote`; unpushed work is lost when a web session ends.
6. Reply with a 3-line summary, the `[ASK]` list and "Next: describe what to build (intake runs automatically)". If `.claude/settings.json` was created or changed in this session, add: "Start a new session so the kit plugins load".
