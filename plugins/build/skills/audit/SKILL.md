---
name: audit
description: "Independent fresh-eyes review of a diff against the plan and requirements, ending in PASS or a numbered FIX list. Use when: after each build step, before anything merges, or whenever correctness or code quality is in doubt. Not for: visual design critique (use review-animations, or /impeccable critique if that plugin is enabled)."
---

# Audit (fresh eyes)

Review as if someone else wrote it. For a big or CRITICAL diff, run the review in a subagent so it starts without the builder's context.

1. Read the diff, the plan and the R-items it claims. Confirm it does what was promised **and nothing extra**.
2. Hunt the silent errors CI misses: off-by-one and boundaries, null/undefined paths, races, O(n²) on growing data, missing authz, injection, secret leaks, swallowed errors.
3. Test quality: would each test fail if its feature broke? Flag trivially-green and tautological tests. On CRITICAL paths the code's author is never the only author of the tests that bless it.
4. Boundaries: module boundaries respected; every DB change reversible with a tested down.
5. Verdict: **PASS**, or a numbered **FIX** list (file, line, what, why). Max 2 fix loops, then the user decides.
