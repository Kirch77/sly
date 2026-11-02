---
name: start
description: Set up keel in the current project. Installs the files if needed, then the representative has a short conversation with the owner and writes the intent and the architecture map.
argument-hint: "[optional: a sentence about what you're building]"
disable-model-invocation: true
---

Set up keel in this project. Owner's note (may be empty): $ARGUMENTS

1. If `.keel/` or `docs/INTENT.md` is missing, run `python3 "${CLAUDE_PLUGIN_ROOT}/install.py" .`
   If the project isn't a git repository, suggest `git init` (the drift check needs git to
   compare changes).
2. You are the representative. Read `.keel/roles/representative.md` and follow
   "Setting up a project" (new or existing, whichever fits). For an existing project, you can
   use the `Explore` agent to map the code.
3. Before your check-in with the owner, run `python3 .keel/check.py` and fix what it reports.
