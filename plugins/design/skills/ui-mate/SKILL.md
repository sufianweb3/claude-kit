---
name: ui-mate
description: "Installs and adapts components from the user's own numbered React library ui-mate (#0001 style) via the shadcn CLI. Use when: the user references a component number like #0003 or 'no 3', or before hand-writing a common interactive component ui-mate may already have. Not for: non-React projects, or when the user wants a component written from scratch."
---

# ui-mate

The user's own React component library. Every component has a **permanent number** (`#0001` is always the magnetic button). The user may say "#3", "no 3" or "component 3"; all mean `#0003`.

## Sources

| Need | URL |
|---|---|
| All components with props + metadata | `https://ui-mate.pages.dev/r/index.json` |
| One line per component (cheap scan) | `https://ui-mate.pages.dev/llms.txt` |
| One component (shadcn registry item) | `https://ui-mate.pages.dev/r/<number>.json` (no leading zeros) |
| Live preview | `https://ui-mate.pages.dev/<0003>` |

## Procedure

1. **Find.** If a number was given, use it. Otherwise read `llms.txt` and pick candidates by category. Tell the user which number you chose.
2. **Install.** `npx shadcn@latest add https://ui-mate.pages.dev/r/<number>.json`
   If the project has no `components.json`, run `npx shadcn@latest init -d` first, or copy the files from the registry JSON manually if shadcn is unwanted.
3. **Adapt, do not fork blindly.** Components are templates:
   - Theme through the `--ui-*` CSS custom properties, not by rewriting classes.
   - Tune motion through props (durations, distances, springs), not by editing internals.
   - Content comes through props and children.
4. **Keep guarantees.** Preserve the `prefers-reduced-motion` branch and the exported `Props` type.
5. **Record.** If a component was modified beyond props/tokens, note the change and the number in `docs/context/DECISIONS.md` via `/decide`.

## If nothing fits

Build it in the project, then tell the user it is a candidate for ui-mate (with a suggested category). Do not push to ui-mate from a project session.
