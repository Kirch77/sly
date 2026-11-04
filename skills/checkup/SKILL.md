---
name: checkup
description: Look for drift and clean it up. For a healthy project, a checkup that fixes what doesn't change behavior. For a badly drifted one, a rescue with a written, phased plan that continues across sessions.
when_to_use: Use when the owner asks to check, audit, clean up, consolidate, rescue or take over code in a project that has sly set up, or to continue a cleanup (docs/CLEANUP.md exists). Not for building new features.
---

You are the representative. Read `.sly/roles/representative.md`, then follow
`.sly/roles/checkup.md` (it sends you to `.sly/roles/rescue.md` when the drift is large or a
cleanup is already in progress).
Use `sly:reviewer` or `Explore` agents in parallel (one per piece or area if the project is
large) for surveys, telling each one it is reviewing an area, not a change. Make cleanups
with the `sly:implementer` and `sly:reviewer` agents, as in "Handling a request".
