---
name: build-tdd
description: "Tests-first implementation with surgical diffs, convention matching, licence checks and component reuse before writing new UI. Use when: implementing any feature, fix or refactor in code. Not for: visual design exploration before a board is approved, or copy-only edits."
---

# Build (tests first)

1. Per part: failing test → minimal implementation → green → refactor → self-check the acceptance criterion.
2. Match the codebase's conventions (CODEBASE-INDEX + golden example). A new pattern is a decision: `/decide`, never a silent fork.
3. **Hard bans:** weakening or deleting a test to pass · loosening types · lint-disables · hardcoded secrets · a heavy new dependency without a decision entry.
   - **3a. Licence at the point of use.** Record the licence in the decision entry either way. Whether it stops you depends on REQUIREMENTS `distribution:` (default `personal`):
     - `personal` / `internal`: no stop. Note it and continue.
     - `client` / `public`: GPL/AGPL, no licence or non-commercial terms → **STOP and ask**. Never resolve a licence question yourself at this tier.
   - **3b. Surgical changes.** Every changed line traces to the request. No "improving" adjacent code, comments or formatting. Clean up only orphans YOUR change created; mention pre-existing dead code, do not delete it.
   - **3c. Reuse before writing UI.** Check `ui-mate` and `ui-standards/references/libraries.md` first. 70%+ match → use it and adjust props · 50-70% → compose or extend · under 50% → build new and flag it as a ui-mate candidate.
4. Stuck twice on the same failure → stop and report: what failed, what you tried, best hypothesis.
5. Commit per part: what and why. Update STATE when a roadmap item completes.
