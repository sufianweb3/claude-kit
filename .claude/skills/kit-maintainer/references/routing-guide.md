# Writing routing text

Build composes each skill's description as:
`<summary> Use when: <when> Not for: <not_when>`
That string is what Claude sees when choosing skills, and it is also printed in the session router table. Max 1024 chars total.

## summary
One sentence: the outcome, not the mechanism. "Turns a sitemap into section-by-section build specs", not "A skill for specs".

## when
Concrete situations and the words the user actually says. Lean slightly pushy; under-triggering is the common failure.
- Good: "the user shares a reference site URL, says 'I like this', or asks to capture a site's layout, motion or type for the library."
- Bad: "design tasks."

## not_when
Name the neighbours. Every overlap with another skill gets resolved here.
- Good: "building the actual section (use section-build) or one-off styling tweaks."
- Bad: "unrelated tasks."

## Checklist
- [ ] Would two different skills both claim this request? Fix with not_when on both.
- [ ] Does `when` include at least one phrase the user would literally type?
- [ ] Is it clear which **phase** this belongs to (concept, plan, build, QA)?
