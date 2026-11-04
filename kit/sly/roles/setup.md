# Setting up a project

For the representative, when `docs/INTENT.md` still has `[fill in` placeholders. Keep it light
for the owner: they describe the idea, you do the rest.

## New project (little or no code)

1. **Have a short conversation, not a questionnaire.** Ask only what you can't reasonably work
   out yourself, usually:
   - What are we building, and who is it for?
   - Why does it matter to you? What would make it a success?
   - Anything it must or must not be (language, platform, things to avoid)?
   - **Only if people will look at screens** (web, app, dashboard): how should it feel? Ask for
     a few words (calm, playful, serious, premium...) and any apps or sites they like the look
     of. If they have no opinion, propose a direction yourself.
   Ask follow-ups only if an answer leaves something important open. For everything else (what
   matters most, non-goals, stage), propose sensible answers yourself.
2. **Write `docs/INTENT.md`** yourself, in their words where you can, including the *why*
   behind each goal. Replace every `[fill in`; write "none yet" where nothing is known, and
   "no screens" under Look and feel for projects without a visual interface.
3. **Choose the solution and the architecture yourself.** Weigh two or three realistic
   approaches (including "use an existing tool") and pick the one that best serves the intent.
   Only make it a question if the options would lead to a noticeably different product for
   them. Log it in `DECISIONS.md`.
4. **Draw the first map** in `docs/ARCHITECTURE.md`: only the pieces needed for the first
   working version. Later ideas go under "Planned, not built yet". The owner does not need to
   approve or edit the map.
5. **Plan the build order,** starting with the thinnest working version: one real feature
   working from start to finish through every piece. It proves the shape early, while
   changing it is cheap. No empty folders or layers "for later". The thin version is the
   first step of the build, not something to deliver on its own.
6. **Check in once** with a short plain summary: what you understood they want and why, the
   approach you picked, and the order you'll build it in. Ask "anything wrong or missing?".
   When they say go, build **everything** from their first request with the normal loop.
   Steps are how you build, not checkpoints for the owner: run them back to back without
   stopping or asking to continue, and report once at the end. Stop mid-way only if a step
   needs an owner decision (see "When to ask the owner" in `representative.md`).

## Existing project

1. **Map what exists.** Explore the code (or have a sub-agent do it) and write
   `docs/ARCHITECTURE.md` from what *actually exists*, not what would be nice.
2. **Pick the good patterns.** Where the code does the same thing several ways, pick the best
   existing one for "Patterns we use" and list the others under "Known rough spots" as "old
   way, replace when touched", so new code follows the good pattern instead of copying the mess.
3. **Draft `docs/INTENT.md`** from what you see (README, code, history, existing screens).
4. **Check in once:** ask the owner to confirm the intent and fill gaps (especially the *why*),
   and tell them the biggest rough spots in plain words, with a recommendation: clean up now,
   or as you go. If the drift is heavy, recommend a rescue (`.sly/roles/rescue.md`): a written
   plan that brings the code back in safe, ordered steps.

Before the check-in, run `python3 .sly/check.py` and fix what it reports.
