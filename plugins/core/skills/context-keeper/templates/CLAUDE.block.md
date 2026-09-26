<!-- kit:start (managed by claude-kit, edit outside this block) -->
## Working in this repo

- Project memory lives in `docs/context/`: STATE (current truth), REQUIREMENTS (the contract), DECISIONS (why), HANDOFF (where the last session stopped), LEARNINGS (what bit us).
- Never contradict an active decision. If one looks wrong, propose superseding it with `/decide`.
- Scope changes only from the user, recorded in REQUIREMENTS and DECISIONS.
- Record decisions with `/decide` as they happen. End sessions with `/handoff`.
- Web sessions run in a throwaway container: anything not committed **and pushed** is lost when the session ends. Push `.claude/settings.json`, `docs/context/` and code to the default branch before stopping. Never end a session with unpushed work.
- `.claude/settings.json` loads the kit. It must stay committed; plugin changes take effect in the next session.
- Kit skills and MCPs are routed by the tables printed at session start. Follow them.
<!-- kit:end -->
