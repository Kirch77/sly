# Checkups: looking for drift

For the representative, every so often or when the owner asks.

1. Run `python3 .sly/check.py --all` for the mechanical part, including older problems and
   oversized files.
2. Review the whole project, with reviewers on slices if it is large (tell each one it is
   reviewing an area, not a change). Look for:
   - code that doesn't match the map, or a map that doesn't match the code;
   - duplicated logic, abstractions with one user, dead code, code in the wrong place;
   - inconsistent patterns, and "Known rough spots" worth fixing now;
   - files that have grown to do several jobs;
   - gaps: features that never reached the screens, reports or commands that should show them;
   - things above or below the stage's bar;
   - drift from `docs/INTENT.md`, including look and feel;
   - a decisions log that needs archiving (see "The decisions log" in `representative.md`).
3. Sort what you found:
   - **Cleanups that keep behavior the same, and gaps the owner would obviously expect
     closed:** fix them yourself through the normal loop, in small steps that each keep the
     project working.
   - **Anything that would change what the owner gets:** bring it to them with a recommendation.
4. Report in plain words: a short summary of what you fixed, then any questions.
