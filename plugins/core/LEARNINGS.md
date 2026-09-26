<!-- Global learnings. Printed at every session start. Append only, one line each, maintained in the kit repo. -->
## Global learnings
- **Cross-artifact drift:** when one artifact introduces a new required output, immediately check every sibling that produces, consumes or lists it. Specs that reference each other drift silently.
- **Verify, don't infer:** an artifact's claim about itself is not evidence. A header is not a path, a config folder is not an installed binary, a checked box is not a built feature. Unverifiable means UNVERIFIED.
- **Rich input is not a finished step:** a supplied PRD, brand guide or reference PDF shortens the design steps; it has twice been wrongly treated as the step being done.
