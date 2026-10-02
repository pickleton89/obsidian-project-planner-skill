# Obsidian Project Planner skill

Local installation uses links to `SKILL.md`, `scripts/`, and `references/` in the source repository, with a Codex directory link to the inspected source root. The source must contain exactly one skill entrypoint. Claude's adapter exposes only the three runtime members; Codex uses the source root because the verified local loader skips SKILL.md file links. The shared installer is maintained in the sibling `obsidian-vault-tools` project; set `OBSIDIAN_VAULT_TOOLS_PATH` if it is elsewhere. Re-running install verifies or adds links and refuses existing copies or conflicting links. Back up and reconcile older copies before migration. These local links are not a cross-computer sync deployment. Source edits are immediately visible; no reinstall is needed after an update.

See `SKILL.md` for workflow usage. Existing task-data defects documented in the vault audit remain outside this installation cleanup.
