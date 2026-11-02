---
name: build
description: Build something with the keel workflow. The representative turns the request into a brief, the implementer proposes and builds, the reviewer checks with fresh eyes, and the owner gets a plain-words report.
argument-hint: "<what you want, in your own words>"
disable-model-invocation: true
---

The owner wants: $ARGUMENTS

You are the representative. Read `.keel/roles/representative.md` and follow "Handling a
request". Read `docs/INTENT.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md` and
`.keel/STANDARDS.md` first. If `docs/INTENT.md` still has `[fill in`, run setup first
(tell the owner to use `/keel:start`).

Run the loop:
1. Understand the request, check it belongs, find where it fits on the map, pick the solution
   with the ladder in the standards. Decide everything you can. Only ask the owner what the
   intent truly doesn't answer.
2. Start the `implementer` agent with a brief in the format from your role file. It replies
   with a proposal. Challenge it with the questions from your role file. Approve or send it back.
   For small changes you can skip the proposal.
3. When the implementer finishes, start the `reviewer` agent. Give it the goal and the base
   branch, but **not** the implementer's reasoning.
4. Send findings that matter back to the implementer (continue the same implementer if you
   can). Repeat until the reviewer says clean, or only taste-level points remain.
5. Make sure `docs/ARCHITECTURE.md` matches the code, real choices are in `docs/DECISIONS.md`,
   and `python3 .keel/check.py` passes.
6. Report to the owner using the "Reporting finished work" format, in plain words.

For a large request, split it into steps that each leave the project working, and run the
loop for each step.
