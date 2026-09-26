---
name: learning
description: "Turns surprising failures into one-line lessons and proposes the general ones for the kit. Use when: a surprising failure gets fixed, a phase or project closes, the user asks 'anything worth remembering?', or the same mistake happens twice. Not for: routine progress notes (use context-keeper) or decisions (use /decide)."
---

# Learning

## During work
Any surprising failure → one line in `docs/context/LEARNINGS.md`: **symptom → cause → rule**.

## Before writing a lesson
Ask: *would a file change make this mistake impossible?* (a test, a lint rule, a CI check, a type, a line in CLAUDE.md). If yes, make that change instead. Memory lines are only for lessons that exist as behaviour and nothing can enforce.

## At phase or project close
1. Read LEARNINGS. For each line that generalises beyond this project, mark it `[kit?]` and write the one-line rule plus why it is general.
2. If three or more lessons cluster on one topic, sketch the skill they imply (name, when, not_when, 5 bullet steps).
3. This session cannot write to the kit repo. Output a block the user pastes into the maintainer session:

```
KIT PROPOSAL from <project>
learning: <symptom → cause → rule>   (why general: ...)
skill idea: <name> | when: ... | not_when: ... | steps: ...
```

Never promote anything without the user's explicit yes.
