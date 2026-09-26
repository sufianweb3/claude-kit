---
name: context-keeper
description: "Maintains the project's memory in docs/context/: STATE, REQUIREMENTS, DECISIONS, HANDOFF and LEARNINGS. Use when: starting or resuming work in a repo, the user says wrap up / done for today / handoff, a decision is made that later sessions must respect, scope changes, or docs/context/ is missing or stale. Not for: writing product docs, READMEs or code comments."
---

# Context keeper

A project's memory lives in `docs/context/`. Each file has **one job**, so nothing is duplicated and nothing goes stale silently.

| File | Job | Write mode | Cap |
|---|---|---|---|
| `STATE.md` | Current truth: what, stack, how to run, roadmap, status, next up | **Overwrite** sections | 80 lines |
| `REQUIREMENTS.md` | The contract: R-items the build is verified against | Edit only on user-approved scope change | none |
| `DECISIONS.md` | Why things are the way they are | **Append only**, supersede instead of editing | none |
| `HANDOFF.md` | What the last session left mid-flight | **Overwrite** every handoff | 40 lines |
| `LEARNINGS.md` | Surprising failures: symptom → cause → rule | Append only (`learning` skill) | none |
| `CODEBASE-INDEX.md` | Map of the code (written by `recon`) | Patch after each phase | 200 lines |

Design projects also get `docs/design/REFERENCES.md` and `docs/design/UI-BLUEPRINT.md` from `website-builder`.

The core SessionStart hook already prints STATE, HANDOFF, open R-items and active decision titles. Do not re-read them unless you need more detail.

## Init
1. Create `docs/context/` with STATE, DECISIONS, HANDOFF and LEARNINGS from `templates/`. REQUIREMENTS is created by the `intake` skill (template in `templates/REQUIREMENTS.md`).
2. Seed STATE "Roadmap" from `templates/roadmaps/<profile>.md`.
3. Add `templates/CLAUDE.block.md` to the project `CLAUDE.md` (create if missing). If a `<!-- kit:start -->` block exists, replace only that block.
4. Fill STATE from the repo. Unknowns become `[ASK]`, never guesses.

## Resume (start of a session)
1. Compare the HANDOFF branch and last commit with `git branch --show-current` and `git log -1 --oneline`. If they differ, say so in one line; the handoff may be stale.
2. Continue from **Next step** unless the user asks for something else.

## Decide
Run when a choice is made that a future session could otherwise undo: library or service, architecture or data model, a rejected approach, a design direction, a client constraint, a scope change.
1. Next id = highest `D-NNN` + 1. Append in the format shown in `templates/DECISIONS.md`.
2. Replacing an older one: edit **only** its heading to add `(superseded by D-NNN)`.
3. Scope change: update the R-items in REQUIREMENTS too. Stack or structure change: update STATE.

Do not log trivia. Test: *would a fresh session plausibly redo this differently?*

## Handoff (end of a session)
Trigger: `/handoff`, or the user says wrap up, done for today, stopping here, switching tasks. Also do it before the context window gets tight.
1. Log unrecorded decisions (Decide) and surprising failures (`learning`).
2. Update STATE: roadmap ticks, status, next up. Delete lines that are no longer true.
3. Overwrite HANDOFF from `templates/HANDOFF.md`. **Next step** must be startable without asking: file path + action.
4. Commit: `chore(context): handoff <short summary>` and push. Web sessions are discarded; unpushed work is lost.

## Verify & close (end of a milestone or project)
Walk every R-item. Tick only with evidence (`R3 ✓ src/auth/login.ts + tests/auth.test.ts`). Anything unbuilt is reported explicitly, never silently dropped. Then run `learning` close.

## Rules
- Facts only. Plans the user has not agreed to are not state.
- Never store secrets, tokens, client credentials or personal data.
- Keep the caps. History lives in git and DECISIONS.
- Paths over prose: `src/lib/auth.ts` beats "the auth file".
