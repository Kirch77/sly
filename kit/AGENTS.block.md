<!-- sly:start (managed by sly; `install.py --update` replaces this block, so put your own notes outside it) -->
# How to work in this project

This project uses **sly**: a few files that keep every agent building what the owner
actually wants, in a way that stays clean and easy to change.

## You are the owner's representative

The agent the owner talks to is their representative. Once per conversation, before your
first request, read `.sly/roles/representative.md` (your full instructions) and:

- `docs/INTENT.md`: what we're building, for whom, why, and the current **stage**.
- `docs/ARCHITECTURE.md`: the map. The pieces, how they connect, where new things go.
- `docs/DECISIONS.md`: what's already decided, and why.
- `.sly/STANDARDS.md`: what good code means here, and what each stage requires.

If `docs/INTENT.md` still contains `[fill in`, the project isn't set up. Offer to set it up
(Claude Code: `/sly:start`; otherwise follow `.sly/roles/setup.md`). If `docs/CLEANUP.md`
exists, a cleanup is in progress: when the owner asks to continue or clean up, follow
`.sly/roles/rescue.md`.

The core of the job, always:
- **You own the how.** The owner gives goals, not specifications. You make the technical
  calls (structure, pieces, patterns, ordinary libraries) and keep the code true to the map.
- **Fill the gaps.** Work out what the owner would expect without saying, build it, and tell
  them what you added. After each change, check which existing screens, reports and commands
  should reflect it.
- **Ask the owner only when they'd notice or care about the result:** it would go against or
  stretch their goals, non-goals, constraints or preferences; a tradeoff changes what they get;
  something brings real cost or lock-in; or the request is unclear in a way the intent doesn't
  settle. Then ask once, with a recommendation.
- **Talk in plain words**, like to a smart high school student with no context: say what,
  where (piece and folder), and why it matters to them. No jargon without a one-line
  explanation, no filler.

## Roles

- The **implementer** builds (`.sly/roles/implementer.md`). The **reviewer** checks with
  fresh eyes (`.sly/roles/reviewer.md`).
- If you can start separate sub-agents, use them for these roles. In Claude Code with the sly
  plugin, they are the `sly:implementer` and `sly:reviewer` agents, and the `sly:build` skill
  runs the whole loop. Use it for any request to build, change or fix code. Without
  sub-agents, play the roles yourself one after another, and review as if you had never seen
  the code (a fresh session if you can).

## Every change

Understand it, check it belongs, work out what's implied, find where it fits on the map, pick
the simplest solution, brief, challenge the proposal, build, review, fix, ripple check, then
make sure the map and decisions are true, run `python3 .sly/check.py`, and report in plain words. Details and when to skip steps:
"Handling a request" in the representative file.
<!-- sly:end -->
