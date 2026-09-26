---
name: planning
description: "Turns confirmed requirements and the Context Report into a session-sized, flaw-checked plan with verify steps that can fail. Use when: after intake for any feature or phase, any non-trivial change request, or before touching a CRITICAL area. Not for: trivial edits, or brainstorming open-ended ideas before requirements exist (use superpowers:brainstorming)."
---

# Planning

Inputs: CONFIRMED `docs/context/REQUIREMENTS.md` + Context Report + relevant CODEBASE-INDEX lines. Need more facts? Run `recon`; never guess about unseen code.

1. Split into parts that each fit one session. Per part:
   - observable **acceptance criterion**
   - R-items covered
   - tests to write first
   - approach notes (algorithm + complexity, null and boundary cases)
   - **risk tag**: LOW (may run end to end) · HIGH (plan needs the user's yes) · CRITICAL (auth, payments, user data, secrets, migrations, onchain, production: plan approval AND diff review, always)
2. External APIs: plan only from current docs (`context7` MCP or docs the user pastes). Record base URL, auth and limits in REQUIREMENTS Facts. Never implement an integration from memory.
3. **Every `verify` must be able to FAIL.** Ask of each: would this fail if the task built nothing? `echo`, `true`, `exit 0` or a trailing `|| true` fail that test. Use a test, `tsc --noEmit`, a build, a lint, or a grep asserting the artifact exists with the right content.
4. **Flaw pass (mandatory):** list the 3 most likely failure modes of your own plan, then adjust it.
5. Hard-to-reverse choices (data model, auth provider, framework): present 2-3 approaches with trade-offs and let the user pick. Log it with `/decide`.
6. Put the plan's phases into STATE "Roadmap". On HIGH or CRITICAL, nothing is implemented from an unapproved plan.
