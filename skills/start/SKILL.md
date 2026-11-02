---
name: start
description: Set up keel in the current project. Installs the files if needed, then the representative has a short conversation with the owner and writes the intent and the architecture map.
argument-hint: "[optional: a sentence about what you're building]"
disable-model-invocation: true
---

Set up keel in this project. Owner's note (may be empty): $ARGUMENTS

1. **Install if needed.** If `.keel/` or `docs/INTENT.md` is missing, run:
   `python3 "${CLAUDE_PLUGIN_ROOT}/install.py" .`
   If the project isn't a git repository, suggest `git init` (the drift check works best with git).

2. **Become the representative.** Read `.keel/roles/representative.md` and follow its
   "Setting up a project" section: the new-project steps if there is little or no code,
   the existing-project steps otherwise. Read `.keel/STANDARDS.md` too.

3. Keep it light for the owner. Ask only what you can't work out yourself, a few questions at
   a time, in plain words. You write `docs/INTENT.md`, `docs/ARCHITECTURE.md` and the first
   entries in `docs/DECISIONS.md`. Every `[fill in` must be replaced.

4. Finish by running `python3 .keel/check.py`, fixing anything it reports, and giving the
   owner a short plain-words summary: what you understood they want, the approach you
   picked and why, and what you plan to build first. Ask "anything wrong or missing?" once.
