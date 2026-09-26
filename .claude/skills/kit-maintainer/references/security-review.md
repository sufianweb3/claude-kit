# Security review (run before ANY new skill, MCP, plugin or notable dependency)

Adapted from the old `capability-intake` firewall. This is **your** read; `kit.py audit` (NVIDIA SkillSpector, static) runs alongside it. Neither replaces the other: the scanner catches patterns you skim past, you catch intent the scanner cannot judge.

## Principles
0. Prefer re-implementing a **technique** as a local skill over importing an artifact: same value, no supply-chain risk.
1. **Pin** everything: vendored skills and external plugins carry a full commit sha. No floating "latest" for code that runs hooks.
2. List every capability requested: network, filesystem outside its folder, shell, env/secrets, hooks. Flag loudly.
3. A scan **informs** the user; it can be fooled, so it never replaces their yes. The user approves every new external.
4. MCPs: narrowest scopes, read-only unless write is truly required. A docs server and a server that can move funds are not the same trust level.
5. Updates re-run this review on the diff between the pinned commit and the new one.

## Triage: cheap first pass (before reading any code)

Reviewing artifacts one-by-one at full depth is unaffordable. Triage spends one call on the file tree, sorts
the artifact by SHAPE, and only then decides how much reading it has earned. Derived from real intakes
(2026-07-30: ecc, a 15-repo batch, graphify): the tree alone predicted the verdict almost every time.

### T1. Get the tree, not the files (1 call)

`git clone --depth 1` into /tmp and `find . -type f -printf '%s %p\n'`: paths + sizes. Never start by reading the README:
it describes intent, the tree shows capability.

### T2. Classify the shape: this sets the budget

| Shape                          | Looks like                                            | Budget     | Depth                                                                          |
| ------------------------------ | ----------------------------------------------------- | ---------- | ------------------------------------------------------------------------------ |
| **A · pure-doc skill**         | 1 `SKILL.md`, no scripts                              | ~2 calls   | read it fully: this is genuinely cheap                                        |
| **B · skill + scripts**        | `SKILL.md` + a few small scripts                      | ~4–6 calls | read SKILL.md + every script                                                   |
| **C · tool / package**         | `pyproject.toml`/`package.json`, `bin/`, many modules | ~6–8 calls | read the **capability surface only** (below), then state what you did not read |
| **D · app / bundle / harness** | full application, or dozens of skills/agents          | STOP       | do NOT certify. Say it needs its own session, or decline                       |

**Never let a shape-D artifact be called "safe" because it looked fine.** That is the failure mode this table
exists to prevent.

### T3. Red flags readable from the tree alone (free)

- no `LICENSE` → cannot be vendored, whatever else is true
- `install.sh` / `install.ps1` / `postinstall` / `setup.py` scripts → runs code on install
- a file named for credentials/sessions (`cookie_extract`, `token`, `keychain`, `credentials`)
- `SKILL.md` far outside norms (>50 KB) → not a skill, a program in prose
- the same skill duplicated across platform dirs **at different sizes** → upstream already drifting
- minified/obfuscated blobs, vendored binaries
- package name ≠ repo name → confirm the real package before anyone types `install`

### T4. The capability surface (shape C: read ONLY these)

1. dependency manifest: what it pulls in
2. entry point (`__main__`, `bin/`, `index`): what it can be told to do
3. anything named `serve`/`server`/`api`: does it open a listener, and on what interface
4. anything named `hook`/`install`/`config`: **does it write outside its own folder** (`~/.claude`, global
   config, git hooks)
5. anything doing network I/O: hardcoded endpoints vs user-supplied URLs; telemetry
6. any `security.py`-style module: its presence is a positive signal; read what it defends

Skip the algorithms. Risk concentrates at the edges, not in the maths.

### T5. Verdict: one of four, always with the limit stated

```
PASS      shape A/B fully read, nothing flagged            → proceed to Add
PASS*     shape C, capability surface clean                → proceed, and NAME the files not read
DEFER     needs a dedicated session, or a flag needs an answer → catalog it, do not install
REFUSE    off-allowlist, no license, or a flag that is disqualifying on its own
```

Every PASS* carries its limit in the commit message and the reply. "I read the parts where risk lives, not every line" is an
honest verdict; "scanned, looks safe" is not.

---

## Adversarial pass (only when it earns its cost)

TRIAGE and the triage read are a **reviewer reading code**. A reviewer looking for problems finds the problems they
thought to look for. This pass adds someone whose job is to find what the reviewer missed.

**It costs tokens, not money beyond that**: same API, three extra calls, no new service or subscription. So
it is gated, not skipped.

**Run it ONLY when one of these is true:**

- the artifact ships **hooks** or anything that executes without being invoked (session start, on every edit)
- it wants **network egress**, **secret/credential access**, or **arbitrary shell**
- it is being promoted to **`default:all`**: a capability every future project inherits
- it is a **CRITICAL-risk** plan or change (auth, payments, user data, keys, migrations, onchain, production)
- shape C or larger where the triage read returned **PASS\***: an admitted partial read on a big surface

**Skip it for everything else.** A pure-documentation skill or a small readable script does not need three
passes; running it everywhere is how a security step becomes a rubber stamp people learn to ignore.

**The three roles: each a FRESH context, never the same pass wearing three hats:**

| Role        | Job                                                                                                                                                                            | Must produce                                                                          |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| **RED**     | Attack it. Assume it is hostile and well-written. How would this exfiltrate a token, persist, or reach the network without anyone noticing? What executes that nobody invoked? | Concrete attack paths with `path:line`, or "no path found and here is where I looked" |
| **BLUE**    | Defend. For each RED finding: is it reachable in how we would actually use this? What contains it: narrowed `allowed_tools`, no secrets in env, the CRITICAL floor?           | Reachable / contained / not-applicable per finding, with the reason                   |
| **AUDITOR** | Judge, having read both and the artifact. RED overclaims to look useful; BLUE rationalises to close the ticket. Discount both.                                                 | A verdict, plus **what neither of them checked**                                      |

The AUDITOR's last column is the point of the exercise. Two adversaries can agree and still both be wrong
about the same blind spot.

**Output:** the verdict, the residual risk in one line, and what was NOT examined. Append to
the commit history. It **informs** the user's yes; it never replaces it: a human still says yes.

**Honest limit, state it every time:** a reviewer that cannot run the code is reasoning about what the code
appears to do. A sufficiently careful backdoor survives all three roles. This lowers the odds; it does not
make an artifact safe, and nothing in this file does.

---

## LICENSE: private use vs shipped code (two different questions)

Obligations attach to **distribution**, not private use. Ask which situation you are in:

**In the kit (private notes/pointers):** low risk. Our posture is _point, don't copy_: a link carries no
obligation. When something IS vendored, copy its LICENSE beside it and never hand-edit the vendored file.
Treat the kit as if it may become public one day; that assumption costs nothing and removes the whole class.

**In project code you ship: this is where it bites.** Any component, snippet or dependency copied into
something a client receives, or a SaaS users reach, is distribution:

| License                        | Copying into shipped project code                   |
| ------------------------------ | --------------------------------------------------- |
| MIT · Apache-2.0 · BSD · ISC   | fine: retain the copyright notice                  |
| **GPL / LGPL**                 | copyleft: can oblige you to release your own source |
| **AGPL**                       | triggers over a network too: SaaS is enough        |
| **No LICENSE file**            | all rights reserved. Readable, NOT redistributable  |
| CC-BY-NC / "personal use only" | no commercial use: rules out client work           |

Rules:

1. **No LICENSE → never vendor it.** Reimplement the technique in our own words (principle 0) or skip it.
2. **Record the license** in `PROVENANCE.md` (vendored) or the DECISIONS entry (project dependency). An
   unrecorded license is one nobody can check later.
3. **Check at the point of USE, not at catalog time.** Cataloguing a link is free; pulling a component into
   shippable code is the moment that matters.
4. Copyleft in a client project is a **human decision**, not an agent's. Surface it, do not resolve it.
