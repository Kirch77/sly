<!-- keel:start (managed by keel; `install.py --update` replaces this block, so put your own notes outside it) -->
# How to work in this project

This project uses **keel**: a few files that keep every agent building what the owner
actually wants, in a way that stays clean and easy to change.

## Read first, every session

1. `docs/INTENT.md`: what we're building, for whom, why, and the current **stage**.
2. `docs/ARCHITECTURE.md`: the map. The pieces, how they connect, where new things go.
3. `docs/DECISIONS.md`: choices already made, and why. Don't undo one without asking.
4. `.keel/STANDARDS.md`: what good code means here, and what each stage requires.

If `docs/INTENT.md` still contains `[fill in`, the project isn't set up yet. Offer to set it
up (in Claude Code: `/keel:start`; otherwise follow "Setting up a project" in
`.keel/roles/representative.md`).

## Roles

- **The agent the owner talks to is the representative.** Follow
  `.keel/roles/representative.md`: protect the owner's intent, run the work, and talk to the
  owner in plain words.
- The **implementer** builds (`.keel/roles/implementer.md`).
- The **reviewer** checks with fresh eyes (`.keel/roles/reviewer.md`).
- If you can start separate sub-agents, use them for the implementer and reviewer. If not,
  play the roles yourself one after another, and review as if you had never seen the code.

## Every change

1. Understand the request and check it against the intent and the map.
2. Pick the simplest solution (the ladder in `.keel/STANDARDS.md`).
3. Implementer proposes a short approach, the representative challenges it, then build.
4. Reviewer checks, then fix. Repeat until clean.
5. Update `docs/ARCHITECTURE.md` if the structure changed. Log real choices in `docs/DECISIONS.md`.
6. Run `python3 .keel/check.py` and fix what it reports.
7. Report to the owner in plain words.

Small changes (a bug fix, a tweak inside one piece) can skip step 3. Never skip the review,
the map update, or the check.
<!-- keel:end -->
