# Placement

| If the skill or MCP is about... | Plugin |
|---|---|
| Session memory, learning loop, routing, project setup, output modes, anything every project needs | `core` |
| Code: intake to deploy pipeline, architecture, APIs, databases, auth, security, testing, debugging, extensions, SaaS plumbing | `build` |
| Websites and visuals: creative process, references, layout, typography, motion, 3D/WebGL, components, visual QA | `design` |

Rules
- `core` stays tiny. It is loaded in every project; only add what is genuinely universal.
- Frontend engineering (state, data fetching, forms) is `build`. Frontend **look and feel** is `design`.
- If a new domain (e.g. `web3`, `content`) grows past ~6 skills with its own trigger vocabulary, propose a new plugin: add `[plugins.<name>]`, then add it to the relevant `[profiles]`.
