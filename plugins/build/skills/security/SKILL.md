---
name: security
description: "Secrets, input validation, authorization, auth/payment/data checklists and onchain minimums. Use when: auditing auth, payments or user-data code, before any ship, or whenever secrets, keys, external input, wallets or contracts are involved. Not for: UI-only changes with no data, auth or input surface."
---

# Security

1. **Secrets** only from env vars or a secrets manager. Never in code, files, logs or chat. A committed secret is compromised: rotate it, don't just delete the line. Secret scan in CI.
2. **Input:** validate and encode at every boundary (injection, XSS, path traversal). Authorization is checked on every endpoint, not hidden in the UI.
3. **Auth / payments / data checklist:** token expiry + rotation · rate limiting · least-privilege DB access · no PII in logs · idempotent payment webhooks · data export and delete paths exist.
4. **Onchain minimum:** reentrancy, overflow/underflow, access control, gas griefing, signature replay. The implementing agent never audits its own contract; anything holding real value gets a third-party audit.
5. **Keys and wallets:** never generate, store or log private keys or seed phrases in the repo; non-custodial flows sign client-side only.
