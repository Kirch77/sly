---
name: sly-harden
description: Get a sly project ready to move up a stage (usually MVP to Production). The representative compares the project against the next stage's bar, explains the gaps in plain words, and gets the approved ones fixed. Use when the owner asks to harden, get production-ready, or move to the next stage.
---

You are the representative. Read `.sly/roles/representative.md`, then follow
`.sly/roles/stages.md`. The target is the stage the owner named, or the one after the current
stage in `docs/INTENT.md`.

Use `sly-reviewer` agents in parallel (one per slice of the project if it's large) for the
comparison, telling each one it is reviewing an area against the target stage, not a change.
Fix approved gaps with the `sly-implementer` and `sly-reviewer` agents, as in "Handling a request".
