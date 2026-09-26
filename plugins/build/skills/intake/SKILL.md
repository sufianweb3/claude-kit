---
name: intake
description: "Turns the user's request into docs/context/REQUIREMENTS.md, the contract every build is verified against. Use when: a new project or feature is described, the user asks to build, add or change something non-trivial, or repeats an instruction (a repeat is an unwritten requirement). Not for: one-line fixes, questions, or website creative direction (website-builder runs its own discovery)."
---

# Intake

Output: `docs/context/REQUIREMENTS.md` (template in the `context-keeper` skill). It is the contract; final verification walks every R-item.

1. Extract every explicit need from the user's message as R-items, in **their** wording.
2. Add "Implied by the request" items (accounts imply password reset; payments imply webhooks). Mark them implied and confirm them. Never add scope silently.
3. Ask at most 5 questions, only ones that change the build. Otherwise state assumptions inline and continue.
4. Set `distribution:` (personal | internal | client | public). It decides whether licences stop the build (see `build-tdd` 3a).
5. Write REQUIREMENTS.md as DRAFT. **STOP.** The user's yes makes it CONFIRMED.
6. Later scope changes come only from the user: update the R-items and log the change with `/decide`. Never edit an R-item away.
7. **A repeated instruction is a requirement, not a comment.** If the user says the same thing twice ("make it look better", "use the skills", "this feels generic"), write it as an R-item **with a check that can fail** ("R-N: no page ships that fails the generic-output check in `ui-standards`") and say you recorded it. Instructions that live only in chat are gone by the next phase.
