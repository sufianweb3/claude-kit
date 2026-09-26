# UI BLUEPRINT - what each page actually contains, before any code

Written after the reference board is approved, before implementation. One block per page.

**Why this exists.** A model asked to "build the dashboard" is being asked to solve product design, UX,
visual design and frontend engineering at once - so it falls back on the layout it has seen most:
sidebar → title → four metric cards → chart → table. Deciding composition _first_, in prose, is what stops
that. It also gives component search something to search **for**: you cannot look up the right component
until you know what slot it fills.

---

## Design priority - settle conflicts in this order

```
1. user task          6. typography
2. information hierarchy   7. spacing
3. interaction clarity     8. colour
4. product identity        9. components
5. composition            10. decoration
```

**Never sacrifice 1–5 to improve 9–10.** "I found a nice animated card, so the page now has fourteen" is
the failure this ordering prevents.

## The product metaphor - decide it once, here

What mental model is this product? _Operating system · command center · workspace · document · feed ·
instrument · storefront._ Everything downstream inherits it - an operating system does not look like a
brochure, and a command center is not a marketing page with charts.

**Metaphor:** _____________

Then name things in **product language, not template language**. Template language turns every noun into a
card. Product language describes what the thing actually is:

| Template language                              | Product language                                                                                                |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| "Agent Card" - icon, title, blurb, two buttons | Agent = identity + status + activity + capability, shown as live status, running count, throughput, a sparkline |

**Recurring visual concepts for this product:** _____________

---

## Page: `<name>`

**Primary user goal.** One sentence. If it takes two, the page is doing two jobs.

**Visual hierarchy.** What the eye should hit, in order. Number them - the order is the decision.

1.
2.
3.

**Layout.** Sketch it in ASCII. Crude is fine; committing to a shape is the point.

```
┌──────────────────────────────────────────┐
│                                          │
└──────────────────────────────────────────┘
```

**Slots → components.** Fill the right column from `ui-mate` (`https://ui-mate.pages.dev/llms.txt`) and
`ui-standards/references/libraries.md`. "Build new" is a valid answer **only** after searching and
recording that nothing matched.

| Slot | What it must convey | Component | Source         |
| ---- | ------------------- | --------- | -------------- |
|      |                     |           | ui-mate / lib / new |

**Interaction.** What responds to hover, click, keyboard, scroll. What is the primary action, and is it
reachable in one step?

**States.** Empty, loading, error, and the "one item" case - the states that get skipped and then look
broken in the demo.

**Do NOT use on this page.** Name the specific defaults being ruled out, so the ban is checkable rather
than a vibe: _____________

**Reference it executes.** Which entries from `REFERENCES.md` this page is built against. A page matching
no reference is either unplanned or drifting.

---

_Copy the block above per page. A page with no blueprint gets no code._
