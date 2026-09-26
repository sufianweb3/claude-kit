---
description: Bootstrap this repo for the kit (context layer, CLAUDE.md, profile settings)
argument-hint: "[website|webapp|app|extension|api]"
---

Set up this repository for the kit. Profile: **$ARGUMENTS** (if empty, infer from the repo: framework, package.json, a manifest.json for extensions; ask only if truly unclear).

1. Check the project repo's visibility (GitHub repo settings or API; if you cannot tell, ask). If it is **public**, warn before writing anything:
   "This repo is public, so docs/context/ (STATE, REQUIREMENTS, DECISIONS, HANDOFF, LEARNINGS) will be public too. Never put credentials, client personal data or contract terms in it." Continue only after the user acknowledges.
2. Load `context-keeper` and run **Init** with this profile.
3. Ensure `.claude/settings.json` enables the profile: fetch
   `https://raw.githubusercontent.com/sufianweb3/claude-kit/main/install/profiles/<profile>.json`
   and merge it in. Never delete existing keys.
4. Ask one question only if unknown: does it deploy to Cloudflare? If yes, also enable `cloudflare@sufian-kit`.
   Do not mention `impeccable` unless the user asks for design critique. If they do, offer `impeccable@sufian-kit` as an opt-in and state its risk (it downloads and runs a native binary on first use); enable it only on their yes.
5. Fill STATE from the repo; unknowns become `[ASK]`.
6. Commit `chore(kit): init context layer (<profile>)` and push. Confirm with `git ls-remote`; unpushed work is lost when a web session ends. Push to the current working branch only, never directly to main. If the current branch is main, create a working branch first. Merging to main requires the user's explicit yes.
7. Reply with a 3-line summary, the `[ASK]` list and "Next: describe what to build (intake runs automatically)". If `.claude/settings.json` was created or changed in this session, add: "The kit plugins load in new sessions only after this branch is merged into main. Merge it? (needs your explicit yes)".
