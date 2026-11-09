---
name: harden
description: Get the project ready to move up a stage (usually MVP to Production). The representative compares the project against the next stage's bar, explains the gaps in plain words, and gets the approved ones fixed.
argument-hint: "[optional: target stage, default is the next one]"
disable-model-invocation: true
---

Target stage: $ARGUMENTS (if empty, the stage after the current one in `docs/INTENT.md`).

You are the representative. Read `.sly/roles/representative.md`, then follow
`.sly/roles/stages.md`. Use `sly:reviewer` agents (in parallel, one per slice of the project if it's large)
for the comparison, telling each one it is reviewing an area against the target stage, not a
change. Fix approved gaps with the implementer and reviewer, as in "Handling a request".
Choose each agent's model as in "Choosing the helper's model" in `representative.md`.
