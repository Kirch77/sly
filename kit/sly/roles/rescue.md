# Rescue: bringing a drifted project back on course

For the representative, when a project has drifted far: much of the code doesn't follow one
structure, logic is duplicated across many places, nobody could draw a clean map of it, or the
owner asks to clean up, rescue or take over the project.

A rescue is a series of small, safe, ordered steps toward a written target. It often spans
several sessions; `docs/CLEANUP.md` is what carries it from one session to the next. Never try
to fix everything in one giant change.

**If `docs/CLEANUP.md` already exists:** read it, continue from the first unchecked step, and
skip to "Working through the plan".

## 1. Recover the intent

Drifted code no longer shows what was meant. Draft `docs/INTENT.md` from the README, the code,
the history and what the app visibly does, then check in with the owner: "This is what I think
it's supposed to be. What's wrong or missing?" Pay special attention to features that look
half-finished or contradictory: ask whether each one is wanted. This is the one step where the
owner's input matters most. Don't skip it.

## 2. Map what exists, honestly

Survey the code. For a big codebase, split it into areas and have several agents survey them in
parallel (read-only), each reporting: what's there, what it does, what it depends on, what's
duplicated, what looks dead, and what's untested. Write `docs/ARCHITECTURE.md` from what
*actually exists*, including the mess (under "Known rough spots").

## 3. Draw the target

Design the structure the project should end up with: the simplest one that serves the intent.
Usually far fewer pieces than today. Write it in `docs/CLEANUP.md` (format below). The map
keeps describing the present; the target lives in the plan until each part is done.

## 4. Write the plan

Break the way from here to the target into phases, in this order, because each one makes the
next easier:
1. **Safety net:** tests that pin down what the app does *now* for the areas about to change.
   Test behavior from the outside (inputs and outputs), not internals, so the tests survive the
   reorganizing. If something can't reasonably be tested, mark that area "careful" in the plan.
2. **Delete dead code:** unused files, functions, flags, options, commented-out code.
3. **Merge duplicates:** one version of each piece of logic, in the right place.
4. **Move things where they belong:** match the target structure.
5. **Simplify:** unneeded layers, abstractions with one user, tangled functions.
6. **Bugs:** only after the owner approves them (see below).

Each step must be small enough to review in one go and leave the project working.

Show the owner a short plain summary of the target and the phases, with your estimate of the
size, and ask once if anything is wrong. Then start, and keep going through the steps.

## Working through the plan

For each step:
1. Brief the implementer with `MODE: APPROVED PLAN` (the step is the plan). The goal is: same
   behavior, cleaner code.
2. The safety-net tests must pass before and after. A step that needs a test changed is changing
   behavior; stop and treat it as a bug or an owner decision.
3. Review it (reviewer for anything beyond trivial deletions).
4. Update the map to match the code. Tick the step in `docs/CLEANUP.md`, with one line on what
   it did. Commit if the owner allows commits.
5. Go straight on to the next step. Report at the end of each **phase**, not each step, unless
   something needs the owner.

**Bugs found along the way:** don't fix them in a cleanup step, because fixing a bug changes
what the app does. List each one under "Bugs found" in `docs/CLEANUP.md` (what happens, what
should happen, where). Bring the list to the owner at the end of a phase, with a recommendation
for each. Fix the approved ones in the Bugs phase, each with a test.

**If a session ends mid-rescue:** the plan is the memory. The next session reads it and goes on.

**When it's done:** remove "Known rough spots" that were fixed, make sure the map matches,
run `python3 .sly/check.py --all`, and give the owner a final plain report: what was deleted,
merged and moved, bugs fixed, how much smaller the code is (lines and files, before and after),
and anything still marked "careful". Then delete `docs/CLEANUP.md` and log the rescue in
`DECISIONS.md` in one or two sentences.

## `docs/CLEANUP.md` format

```
# Cleanup plan

Started: YYYY-MM-DD. Size before: N lines of code in M files.

## Target
[The structure we're heading to, in plain words, and the pieces with their folders.]

## Phases
### 1. Safety net
- [ ] Tests for [area]: [what they pin down]
### 2. Delete dead code
- [ ] [what, where]
### 3. Merge duplicates
- [ ] [what, into where]
### 4. Move things where they belong
- [ ] [what, from where to where]
### 5. Simplify
- [ ] [what]
### 6. Bugs (owner-approved only)
- [ ] [bug]

## Careful areas
- [area]: [why it can't be fully tested]

## Bugs found (need the owner's OK)
- [where]: [what happens] -> [what should happen]. Recommendation: [fix / leave].
```
