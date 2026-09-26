# Importing from an old setup (e.g. <your old repo>)

Items not carried over from `<your old repo>` belong in the Rejected table (`[[rejected]]` in kit.toml, shown in CATALOG.md) with the reason.

Goal: carry over what earned its place, not everything.

1. **Get access.** Try `git clone https://github.com/<owner>/<repo> /tmp/old`. Never write a token into a file, remote URL or commit. If the session cannot reach the private repo, ask the user to upload the folder into `_import/<repo>/` on this branch (GitHub web: Add file, Upload files).
2. **Inventory.** Produce a table: item, type (skill / MCP / context file / script / doc), what it does, overlap with the kit, verdict. Verdicts:
   - **Keep**: unique and still used.
   - **Merge**: fold into an existing kit skill.
   - **Replace**: a better maintained upstream exists; vendor that instead.
   - **Drop**: stale, duplicated or never triggered.
3. **Stop and show the table.** Wait for the user's yes or edits.
4. **Migrate one item per commit** using the Add procedures. Rewrite routing text with the routing guide; old descriptions rarely have `not_when`.
5. **Context files** from the old setup do not become skills. Their structure is already covered by `context-keeper`; only port content that is missing.
6. Delete `_import/` in the final commit.
