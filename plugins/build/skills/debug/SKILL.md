---
name: debug
description: "Change protocol (blast radius before the first edit) and bug protocol (failing repro test, root cause, fix). Use when: any bug, error or unexpected behaviour, and any change to existing code ('change X', 'add to X', 'X is broken'). Not for: greenfield code with nothing existing to break."
---

# Debug

## Change protocol (before editing existing code)
Map the blast radius: every file, module and feature touching the area, what could break, whether a module boundary must move (that is an architecture decision → `/decide`). Verify the current schema from the source of truth. Then mini-plan → get a yes if HIGH → build.

## Bug protocol
1. Write a failing test that reproduces the bug. Confirm it fails **for the right reason**. Fix nothing yet.
2. State the root cause in at most 2 lines. "I added a check here" is a symptom patch; keep digging.
3. Fix the cause; the repro test passes.
4. Full suite green. A collateral failure is a coupling bug to fix now, not paper over.
5. The repro test stays forever. Surprising causes get a LEARNINGS line (`learning` skill).
