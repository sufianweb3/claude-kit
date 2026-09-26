---
name: deploy
description: "Staging to production flow, CI gates, reversible migrations, releases, revert and monitoring. Use when: shipping, deploying, releasing, rolling back, setting up CI/CD or environments, or writing migrations. Not for: local dev server setup or Cloudflare platform specifics (use the cloudflare plugin alongside)."
---

# Deploy

1. Two modes: **staging** (private; everything lands here first; the user clicks the real thing) → **production** (reachable only via staging). Branches: feature → staging → main, both protected.
2. CI on every PR: lint · typecheck · tests · build · dependency audit (fail on high) · secret scan (fail on any hit). UI projects add screenshot diffs against approved baselines.
3. Migrations: every migration ships a tested `down`; risky changes go expand → contract; production deploy snapshots the DB first; a schema-linked bug reverts snapshot + matching code tag together.
4. Releases: tag vMAJOR.MINOR.PATCH with notes from commit messages. Revert = redeploy the last good tag or `git revert` the merge. Decide code-only vs schema-linked BEFORE touching anything.
5. Monitoring: error tracker · /health + uptime monitor · structured logs with zero secrets · alerts on 3-4 signals (p95 latency, error rate, cost, one business counter). Incident → `debug` + a LEARNINGS line.
6. **The user signs every production deploy.** Immutable or onchain: testnet first, independent audit, user signs. No exceptions; there is no revert.

Cloudflare targets: also load the `cloudflare` plugin skills when enabled.
