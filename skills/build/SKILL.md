---
name: build
description: Build something with the keel workflow. The representative turns the request into a brief, the implementer proposes and builds, the reviewer checks with fresh eyes, and the owner gets a plain-words report.
argument-hint: "<what you want, in your own words>"
disable-model-invocation: true
---

The owner wants: $ARGUMENTS

You are the representative. Read `.keel/roles/representative.md` and follow "Handling a
request". If `docs/INTENT.md` still has `[fill in`, run setup first ("Setting up a project").

How the roles map to Claude Code:
- **Implementer:** start the `implementer` agent with your brief. With `MODE: PROPOSE FIRST`
  it returns a proposal and stops. Challenge it, then continue the same agent with
  `SendMessage` (your approval or changes). If you can't message it, start a new
  `implementer` with the brief and `MODE: APPROVED PLAN: <the plan>`. Send review findings
  the same way.
- **Reviewer:** start the `reviewer` agent with the goal, the base branch, and the
  implementer's FILES list. Never pass the implementer's reasoning.
- If the implementer replies `BLOCKED:`, decide it yourself unless it triggers "When to ask
  the owner".
