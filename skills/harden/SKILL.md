---
name: harden
description: Get the project ready to move up a stage (usually MVP to Production). The representative compares the project against the next stage's bar, explains the gaps in plain words, and gets the approved ones fixed.
argument-hint: "[optional: target stage, default Production]"
disable-model-invocation: true
---

Target stage: $ARGUMENTS (if empty, the next stage after the current one in `docs/INTENT.md`).

You are the representative. Read `.keel/roles/representative.md` ("Stages and hardening")
and the target stage's list in `.keel/STANDARDS.md`.

1. Have the `reviewer` agent (or a few in parallel, each on a slice of the project) compare the
   whole project against the target stage's list. Ask for concrete findings with file paths.
2. Also check what lives outside the code: hosting, backups, monitoring, where secrets are
   kept, how it gets deployed. Note what is missing or unknown.
3. Give the owner a short list of gaps, most important first. For each: what's missing in
   plain words, why it matters to them, and rough size. Include your recommendation of which
   ones must happen before the move and which can wait.
4. After the owner approves, fix the code gaps through the normal `/keel:build` loop
   (implementer, then reviewer). For gaps outside the code, give the owner simple steps.
5. When the approved gaps are done, update the stage in `docs/INTENT.md`, log it in
   `docs/DECISIONS.md`, and run `python3 .keel/check.py`.
