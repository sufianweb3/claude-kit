---
name: website-builder
description: "Full creative process before site code: discovery, concept, reference board, UI blueprint and component discovery, each gated. Use when: the user wants a website, landing page, redesign or any human-facing UI, including when a brand, PRD or reference is already supplied. Not for: small tweaks to an already approved design, or backend-only work."
---

# Website builder

**Applies to any project with a human-facing UI** - webapp, app, or site. "It has an admin panel and a
checkout, so it's a webapp not a website" is not a reason to skip this; people still look at it.

**When a brand is already supplied** (a PRD or client guide fixing fonts, palette, sections), do NOT
re-invent it and do NOT skip to code. A brand spec fixes colour and type. It says nothing about **layout
archetype, composition, rhythm, motion character, imagery, or interaction** - and that is precisely where
generic output comes from. Steps 1-2 collapse to confirming the given brand; steps 3-4 still run in full,
on everything the spec left open. A detailed PRD makes this skill _more_ necessary, not less: faithfully
implementing a conventional spec produces a conventional site, every time.

Condensed core, gated in order (never skip to code):

1. Discovery: ≤6 sharp questions → a short brief (business, audience, one verifiable proof point,
   3-5 personality words, constraints, forbidden tone).
2. Reflect the brand back (personality · the one undeniable sentence · forbidden tone) → user confirms.
3. Build the world: anchor keywords → the relatable emotional moment → a cinematic hero flow (environment,
   one subject, one camera move, ending frame with space for H1+CTA) → 2-3 concept variants.
4. Present the concept (world, layout archetype, palette extracted FROM the world, type pairing, motion
   language, copy voice) → user approves before a line of code.

## 4a. DESIGN RESEARCH - find the references, because the user usually cannot

**Do not ask "what look do you want?" and stop there.** Most people know good when they see it and cannot
produce it on demand - _"getting a web design reference is too hard for me"_ is the normal case, not a gap in
the brief. Your job is to **propose a board they react to**, not to receive one.

**Search by visual language, never by product category.** "Modern SaaS website" returns the exact average
that produces generic output. Combine an adjective with a medium instead: _minimal futuristic developer tool
UI · monochrome Swiss web application · dense professional workspace · editorial product page_.

**Then look OUTSIDE the product's own category - this is the highest-leverage move here.** Searching "travel
agency website" returns every travel agency website, and the result is another one. The interesting direction
comes from adjacent mediums that solved a similar _problem_:

| The product needs             | Look at                                                                 |
| ----------------------------- | ----------------------------------------------------------------------- |
| Dense status at a glance      | Financial terminals, aviation software, cybersecurity dashboards        |
| Command and control           | IDEs, developer tools, operating systems, launchers                     |
| Browsing a large catalogue    | Creative tools, 3D applications, media libraries, map interfaces        |
| Guiding someone through steps | Onboarding in consumer apps, game tutorials, checkout in premium retail |
| Editorial trust               | Magazines, documentation sites, annual reports                          |

**Collect ingredients, not one perfect site.** Nobody finds THE design. You find navigation in one place,
type in another, composition in a third, motion in a fourth - and the combination is what makes the result
specific to this product rather than a copy of anything.

**Then reverse-engineer, do not imitate.** For each reference ask what makes it work - information density,
type hierarchy, spacing rhythm, border and shape language, colour strategy, interaction and motion
philosophy, how empty states are handled - and carry the **principle** forward. "Do it like Linear" is not a
direction; "Linear earns density through tight type and near-zero chrome" is.

Present 6–10 candidates with one line each on _why it is here_. The user picks. Selecting is a much easier
job than inventing, and it is the job only they can do.

## 4b. REFERENCE BOARD - gather, show, get approval. This is a STOP point.

Words are not a direction. "Cinematic, warm, editorial" describes a hundred different sites, and the gap
between the words and what gets built is where generic output lives. **Show the target before building it.**

**Gather one to three references per category**, from real sources, each with a one-line note on _what
specifically to take from it_ - that note is the whole point:

| Category                        | What to capture                                                              |
| ------------------------------- | ---------------------------------------------------------------------------- |
| Layout / sections               | Section archetypes, grid, how the page breathes, what the hero actually does |
| Typography                      | Real pairings in use, scale contrast, tracking on display type               |
| Colour                          | Palettes in context, not swatches - how much of each, where the accent lands |
| Components                      | Cards, nav, forms, tables, pricing, footers                                  |
| Animation / motion              | What moves, how far, how fast, its character                                 |
| Imagery / video                 | Treatment, crop, grade, subject; how text sits over media                    |
| Anything else the brief demands | Icon style, illustration, data-viz, empty states                             |

**Where to gather from - use the installed capabilities, this is what they are for:**

- `taste-skill` → `imagegen-frontend-web` / `imagegen-frontend-mobile` / `brandkit` generate original comps
  per section. These are **concepts, not evidence** - nobody shipped them, so they prove nothing works.
- `playwright` MCP → open real sites in the brief's world and screenshot them. These are **real evidence**;
  the site exists and someone chose it deliberately. Prefer these where they disagree with a generated comp.
- `ui-mate` and `ui-standards/references/libraries.md` → live demos: shadcn blocks, Motion primitives, React Bits, Magic UI, Cult UI. A reference
  you can install beats one you must rebuild.
- `frontend-design`, `emil-design-eng`, `apple-design`, `animation-vocabulary` → naming the effect precisely
  ("rubber-banding", "pop in") so the build is not guesswork.
- Web search for the niche, plus the user's own competitors or liked sites - **ask for those first**; the
  fastest reference is the one already in their head.

**Material the user supplies is an INPUT to this step, never a replacement for it.** A PDF, a screenshot, a
link, "make it like X" - take it gratefully, put it in the board, and then **fill the remaining categories**.
One reference rarely covers layout AND type AND colour AND components AND motion AND imagery; recording it
and stopping leaves most of the page undirected, which is exactly where the build reverts to the default
template. Say which categories the supplied material covers and which are still open, then close them.

_(This has now failed twice the same way: a supplied PRD was treated as the brand step being done, and a
supplied reference PDF as the board being done. Rich input makes this step **shorter**, never skippable.)_

**Write it to `docs/design/REFERENCES.md`** (template: `templates/REFERENCES.md` in this skill), with screenshots saved in `docs/design/references/`. Not chat - a
board that lives only in a message is gone by the phase that needs it.

**Then STOP and present it.** The user approves, swaps, or rejects per category. Record the decision with `/decide`, including
the rejected directions with the reason, which is the part that stops it drifting back later.

> **Reference, never replicate.** Take the _principle_ - "a hero that stays with one subject and lets type
> breathe", "cards that lean on one strong image, not four icons". Never clone a competitor's layout, copy
> their assets, or lift their copy. Cloning is both a legal problem and a strategic one: a site that looks
> like a competitor's cannot be preferred to it. If a reference can only be described by copying it, it is
> the wrong reference.

5. **UI BLUEPRINT - compose the pages in prose before writing any of them.** Copy
   `templates/UI-BLUEPRINT.md` from this skill to `docs/design/UI-BLUEPRINT.md` and fill one block per page: primary user goal,
   numbered visual hierarchy, an ASCII layout, slot-by-slot component choices, interaction, the four states
   that always get skipped (empty / loading / error / one-item), and the specific defaults ruled out.

   Decide the **product metaphor** here, once - operating system, command center, workspace, instrument,
   storefront. Everything inherits it, and a page built without one defaults to "SaaS dashboard".

   This step exists because component selection has nothing to attach to until composition is decided. Skip
   it and the internal picture of the page is already `card, card, card, card` before any component is
   searched - at which point the best library in the world only supplies nicer cards.

   **A page with no blueprint gets no code.**

6. **COMPONENT DISCOVERY - search before you write. Every time.**

   1. `ui-mate` first: scan `https://ui-mate.pages.dev/llms.txt` for the slot.
   2. Then the libraries in `ui-standards/references/libraries.md` (shadcn blocks, Magic UI, Cult UI, React Bits, Motion Primitives).

   Reuse policy: **70%+ match → use it** (adjust props, not a rewrite) · **50–70% → compose or extend** ·
   **under 50% → build new, and register it.** Never re-implement something already installed because
   writing it fresh felt faster - that is the single most common way a paid-for library never gets used.

   Then install what is chosen rather than hand-rolling it (`ui-standards/references/libraries.md`), pull real docs for anything
   unfamiliar (Context7, never memory), and source the named media. Only then write code.

   Sitemap: only sections that earn their place. Media list with exact generation prompts for assets you
   cannot produce (placeholder + prompt, keep building).

   **Prototype first.** Build each section without heavy 3D, image or video assets for approval, then generate costly assets only for approved sections.

7. Build per skills/design/ui-standards, **against the approved board** - each section names the reference it
   is executing. Then run that skill's generic-output check and a real critique pass (`/impeccable critique` when the impeccable plugin is enabled) plus `review-animations` for motion.
   Final gut check: could this be mistaken for a generic template? If yes, return to the step where it went
   generic - usually 4b, because the board was too vague to build from.
