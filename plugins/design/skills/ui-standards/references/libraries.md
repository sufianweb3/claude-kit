# Libraries

npm packages, component sets and animation engines. Not skills or MCPs: they are installed per project with its package manager.

Licence is information, not a gate, unless REQUIREMENTS says `distribution: client | public` (see `build-tdd` 3a).

---

## Selection rule - read this before picking

**shadcn/ui + Motion is the default pair.** It covers the large majority of UI work. Add a third library
only when the pair genuinely cannot do the thing you need - a specific landing-page effect, a committed
aesthetic, a non-React context.

**Never two animation engines in one project.** Motion _or_ GSAP _or_ Anime.js. Pick one and stay in it;
mixing them fights over the same transform properties and doubles the bundle.

---

## UI component libraries

**Check `ui-mate` first** (`https://ui-mate.pages.dev/llms.txt`). It is the user's own numbered library and is tuned for their work.

| Library               | Install                                                   | Licence     | Reach for it when                                                                                       |
| --------------------- | --------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------- |
| **Shadcn UI**         | `npx shadcn@latest init`                                  | MIT         | **Default base.** Accessible React + Tailwind primitives you own and edit. Start every UI project here. |
| **Magic UI**          | `npx shadcn@latest add "https://magicui.design/r/<name>"` | MIT         | Marketing and landing-page effects on top of shadcn. Same install mechanism, drops straight in.         |
| **Cult UI**           | `npx shadcn@latest add "https://cult-ui.com/r/<name>"`    | MIT         | Richer interactive/animated components when Magic UI is too marketing-flavoured.                        |
| **React Bits**        | `npx jsrepo add <name>`                                   | NOASSERTION | Distinctive visual effects and animated text. Large catalogue, high visual impact.                      |
| **Motion Primitives** | copy-paste                                                | MIT         | Small, tasteful animated components built on Motion. Good when you want restraint.                      |
| **Smooth UI**         | copy-paste                                                | MIT         | Animated components with a softer, modern feel.                                                         |
| **Retro UI**          | `npm i pixel-retroui`                                     | MIT         | Only when the brand is deliberately retro / neo-brutalist. Not a general base.                          |
| **VengeanceUI**       | copy-paste                                                | MIT         | Pre-built animated landing-page sections. Fast for a one-page site.                                     |
| **Componentry**       | copy-paste                                                | MIT         | React + Tailwind + Motion components. Small library, check it has what you need before committing.      |
| **UIverse (galaxy)**  | copy-paste                                                | MIT         | Single elements - a button, a loader, a toggle. Grab one element, never a system.                       |
| **Monet registry**    | registry                                                  | none        | 600+ searchable React components. Use as a **search index** when you don't know what exists.            |

## Animation

| Library                       | Install         | Licence                              | Reach for it when                                                                                                                                       |
| ----------------------------- | --------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Motion** (ex Framer Motion) | `npm i motion`  | MIT                                  | **Default for React.** Layout animation, gestures, enter/exit, scroll. Covers most needs.                                                               |
| **GSAP**                      | `npm i gsap`    | none in repo (GreenSock's own terms) | Complex sequenced timelines, ScrollTrigger, SVG morphing - things Motion cannot express cleanly. Free for commercial use since the Webflow acquisition. |
| **Anime.js**                  | `npm i animejs` | MIT                                  | Lightweight, non-React contexts. Vanilla JS, small footprint.                                                                                           |
| **lenis**                     | `npm i lenis`   | MIT                                  | Smooth scroll. Pairs with any of the above; not an alternative to them.                                                                                 |

## 3D / WebGL

| Library | Install | Licence | Reach for it when |
| --- | --- | --- | --- |
| **three** | `npm i three` | MIT | Any WebGL scene. Non-React or full control. |
| **@react-three/fiber** + **@react-three/drei** | `npm i @react-three/fiber @react-three/drei` | MIT | 3D inside React. drei supplies cameras, controls, loaders and text. |

Rule: 3D is a section-level decision recorded with `/decide`. Prototype the section without the scene first, then add it; always ship a static fallback for `prefers-reduced-motion` and low-power devices.

## Utility

| Library         | Install  | Licence    | Reach for it when                                          |
| --------------- | -------- | ---------- | ---------------------------------------------------------- |
| **hyperframes** | see repo | Apache-2.0 | Write HTML, render video. Narrow but nothing else does it. |

---
