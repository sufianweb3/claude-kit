---
name: ui-standards
description: "Era floor for modern UI: banned defaults, current CSS practice, library selection, responsive rules and the generic-output check. Use when: building or reviewing ANY frontend: pages, sections, components, dashboards or mobile views. Not for: picking a creative direction from scratch (website-builder first) or animation-only work (use animate)."
---

# UI standards

## The era floor - why "modern" produces 2015 unless you define it

**"Modern" is not a direction, it is an average.** Asked for modern, a model returns the centre of everything
it has seen, and the centre of the web is roughly 2015. Nothing below is taste; it is the difference between
the statistical default and current practice. **Pick a direction from the installed sets, then clear this
floor.**

**Ban these - each one is a decade-old default the model reaches for first:**

- Centred hero: H1 + subhead + two buttons + a stock photo behind it
- A three-up grid of icon-cards as the feature section
- Alternating text-left / image-right rows down the page
- One radius everywhere (`8px`) and one shadow (`0 2px 4px rgba(0,0,0,.1)`)
- Body 16 / H1 32-40 with default tracking - no real scale contrast
- Every element fading up on scroll at the same duration
- Sections of identical height and rhythm, stacked
- A 3-up testimonial grid and a 4-column link footer

**Reach for these - current practice, all shipping CSS:**

|                 |                                                                                                                                                                                                                                               |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Material**    | Layered depth, not one flat card: `backdrop-filter` blur + tinted translucency + a 1px top inner highlight + optional grain. Multi-layer shadows that carry the surface's own hue, never neutral grey                                         |
| **Type**        | Extreme scale contrast - display `clamp(3rem, 8vw, 9rem)` against 16-18px body. Negative tracking on display sizes, variable-font optical sizing, `text-wrap: balance` on headlines                                                           |
| **Colour**      | OKLCH over hex for perceptually even ramps, `color-mix()` for states, mesh//conic gradients instead of a flat tint                                                                                                                            |
| **Layout**      | Container queries so components respond to their own box, `:has()` for state-driven layout, subgrid for real alignment across cards, `dvh` for mobile viewports                                                                               |
| **Motion**      | Scroll-driven animation (`animation-timeline: view()`), the View Transitions API between states, **spring physics rather than ease curves** for anything the user touches, staggered reveals with per-element delay, magnetic/proximity hover |
| **Interaction** | Interruptible transitions, real focus-visible states, `prefers-reduced-motion` honoured - motion that reacts to the user rather than playing at them                                                                                          |

**Direction sets - load one deliberately, do not blend three:**
`taste-skill:brutalist-skill` (hard shadows, raw borders, no gradients) · `taste-skill:minimalist-skill`
(space is the feature, one accent) · `taste-skill:soft-skill` (agency-grade polish, warmth) ·
`apple-design` (physical, fluid, gesture-led) · `emil-design-eng` (the invisible details) ·
`animation-vocabulary` to name an effect precisely before building it.

Glassmorphism, neo-brutalism, minimalism and claymorphism are **directions, not decorations** - each carries
its own type, depth, colour and motion rules all the way through. Half-applying one to an otherwise default
page reads as a template with a blurred card on it.

**Build against the approved board.** If `docs/design/REFERENCES.md` exists, it is the spec - each section names the
reference it executes, and a section matching no reference is either unplanned or drifting. If it does not
exist and this project has a UI, that is the gap: run `website-builder` 4b before writing more.

Components: `ui-mate` first, then `references/libraries.md` - shadcn + Motion is the default pair; add a third library
only when the pair genuinely cannot do it, and never two animation engines in one project. **Install what a
vetted library already ships**; hand-rolling it is slower and lands closer to the generic default.
Type: one primary sans (Inter / Geist / Manrope class) + one sparing accent serif; bold for major headings
only; tight tracking only on large display type.
Layout: full-width bands with real hierarchy (headline → proof → CTA); no default 3-icon-card grids; no
text-left/image-right on repeat; sections read as chapters, not templates.
Motion: scroll-reveal opacity + 16-32px translate, 700-900ms, cubic-bezier(0.22,1,0.36,1); hover lift 1-8px;
marquees 24-40s; respect prefers-reduced-motion; motion matches the brand's personality, not a universal fade.
Glass only where it carries information: bg alpha .14-.24, border 15-30%, medium-strong blur, radius 18-30
(hero) / 10-16 (compact).
Responsive: check 390 / 768 / 1440; CTA inside the first viewport; clamp() for hero type only; zero
horizontal overflow; mobile is a design, not a squeeze.
Copy: specific and confident; no "revolutionize / seamless / unlock your potential".
Verify before done: no console errors · hero text readable over media · nav opens/closes · images render ·
build passes · screenshot-verify with the `playwright` MCP at 390 / 768 / 1440, else say plainly what wasn't verified.

**Generic-output check - run it before calling any UI done.** `build passes` cannot fail for "this looks like
every other AI site", so nothing else in the pipeline catches it. Answer these honestly; a yes is a defect:

- Could this be any other company's site with the logo and colours swapped?
- Is the page a stack of centred sections, each one headline-then-3-cards?
- Is every reveal the same fade-up, at the same speed, regardless of what is revealing?
- Are all radii, shadows and spacing the framework defaults?
- Is the hero a headline, a subhead, two buttons, and a stock image?
- Does the copy say "seamless", "elevate", "unlock", "revolutionize"?
- **Date it: could this have shipped in 2015?** If nothing on the page needs a browser from the last three
  years - no container query, no `:has()`, no scroll-driven or view transition, no layered material, no real
  scale contrast - then it is a 2015 page with 2026 colours, and that is what "generic" actually means here.
- Is a design direction **carried all the way through** (type, depth, colour, motion), or is it one blurred
  card on an otherwise default page?

Two or more yeses: stop and reshape the page, do not ship it and offer to improve it later. Then run a real
critique with the installed design skills (`/impeccable critique` or `/impeccable audit`, `taste-skill`'s
redesign pass, `review-animations` for motion) - a second opinion from a tool built for it beats your own read of your own work.

**A supplied brand is not a design.** A client palette and font pairing fixes colour and type - it says
nothing about layout archetype, composition, rhythm, motion character, imagery, or interaction. That is
exactly where generic output comes from, and it is exactly the part still left to decide. Following a brand
spec faithfully and producing a template is the normal outcome, not a surprise.
