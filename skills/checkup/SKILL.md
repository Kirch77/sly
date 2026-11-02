---
name: checkup
description: Look for drift. The representative compares the code with the intent, the architecture map and the standards, cleans up what doesn't change behavior, and brings the owner only what does.
disable-model-invocation: true
---

You are the representative. Read `.keel/roles/representative.md` ("Checkups") and
`.keel/STANDARDS.md` ("Signs of trouble").

1. Run `python3 .keel/check.py` for the mechanical part.
2. Have the `reviewer` agent review the whole project, not a diff (split it across a few
   reviewers by piece if it's large). Look for: code not matching the map, duplicated logic,
   abstractions with one user, dead code, code in the wrong place, inconsistent patterns,
   things above or below the stage's bar, and places that drift from `docs/INTENT.md`.
3. Sort the findings:
   - **Behavior stays the same** (moves, merges, deletions, renames): fix them through the
     implementer and reviewer, in small steps that each keep the project working.
   - **Would change what the owner gets**: bring these to the owner.
4. Update the map and decisions log, run the check again, then report in plain words: what
   you cleaned up (short), and any questions, each with a recommendation.
