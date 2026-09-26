---
description: End the session cleanly. Update STATE and HANDOFF, log decisions, commit and push to the working branch
---

Load the `context-keeper` skill and run its **Handoff** procedure. $ARGUMENTS

Push to the current working branch only, never directly to main. If the current branch is main, create a working branch first. Merging to main requires the user's explicit yes.
