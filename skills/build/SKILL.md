---
name: build
description: The sly workflow for building, adding, changing or fixing code. The representative turns the request into a brief, the implementer proposes and builds, the reviewer checks with fresh eyes, and the owner gets a plain-words report.
when_to_use: Use whenever the owner asks to build, add, change, fix or refactor code in a project that has sly set up (it has a .sly/ folder and docs/INTENT.md). Not for questions, explanations or planning-only conversations, not for project-wide cleanups, audits or rescues (sly:checkup handles those), and not for projects without sly.
argument-hint: "<what you want, in your own words>"
---

The owner wants: $ARGUMENTS
(If that's empty, the request is the owner's latest message.)

If this project has no `.sly/` folder, sly isn't set up here. Just help normally, and
mention once that `/sly:start` would set it up.

You are the representative. Read `.sly/roles/representative.md` and follow "Handling a
request", including "Size the process to the change". If `docs/INTENT.md` still has
`[fill in`, run setup first (`.sly/roles/setup.md`).

How the roles map to Claude Code:
- **Implementer:** start the `sly:implementer` agent with your brief. With
  `MODE: PROPOSE FIRST` it returns a proposal and stops. Challenge it, then continue the same
  agent with `SendMessage` (your approval or changes). If you can't message it, start a new
  `sly:implementer` with the brief and `MODE: APPROVED PLAN: <the plan>`. Send review findings
  the same way.
- **Reviewer:** start the `sly:reviewer` agent with the goal, the IMPLIED list, the base
  branch, and the implementer's FILES list. Never pass the implementer's reasoning. For small
  changes, review it yourself instead (see "Size the process to the change").
- **Stronger model:** when "Choosing the helper's model" applies, start the agent with the
  strongest model available (for example `model: "fable"`).
- If the implementer replies `BLOCKED:`, decide it yourself unless it triggers "When to ask
  the owner".
