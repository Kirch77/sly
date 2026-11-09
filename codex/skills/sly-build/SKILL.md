---
name: sly-build
description: The sly workflow for building, adding, changing or fixing code in a project that has sly set up (it has a .sly/ folder and docs/INTENT.md). The representative turns the request into a brief, the implementer builds, the reviewer checks with fresh eyes, and the owner gets a plain-words report. Not for questions, project-wide cleanups, or projects without sly.
---

If this project has no `.sly/` folder, sly isn't set up here. Just help normally, and mention
once that `$sly-start` would set it up.

You are the representative. Read `.sly/roles/representative.md` and follow "Handling a
request", including "Size the process to the change". If `docs/INTENT.md` still has
`[fill in`, run setup first (`.sly/roles/setup.md`).

How the roles map to Codex:
- **Implementer:** spawn the `sly-implementer` agent with your brief and
  `MODE: PROPOSE FIRST`. It returns a proposal and stops. Challenge it, then spawn
  `sly-implementer` again with the same brief and `MODE: APPROVED PLAN: <the proposal plus
  your changes>` (or continue the same agent if you can). Send review findings the same way.
- **Reviewer:** spawn the `sly-reviewer` agent with the goal, the IMPLIED list, the base branch,
  and the implementer's FILES list. Never pass the implementer's reasoning. For small changes,
  review it yourself instead.
- **Models:** follow "Choosing the helper's model". Spawn each agent with the model for its
  kind of task if you can choose; otherwise say so in your report.
- If the implementer replies `BLOCKED:`, decide it yourself unless it triggers "When to ask
  the owner".
- If the `sly-implementer` or `sly-reviewer` agents aren't available, play those roles
  yourself following `.sly/roles/implementer.md` and `.sly/roles/reviewer.md`.
