# sly

Keeps AI coding agents on course.

Agents are good at finishing the task in front of them, but over many sessions the code
drifts: helpers get duplicated, things land in convenient places instead of the right ones,
and the project slowly stops matching what you set out to build. Each change makes the next
one harder.

sly fixes the root cause, which is lost intent. It writes down what you want, why you want
it, and how the system fits together, and gives one agent the job of protecting all that.

- **A representative** that works for you. It knows your goals and the reasons behind them,
  runs the work, challenges the builder, makes the technical calls itself, and only comes to
  you when something would change what you get. It talks in plain words.
- **An implementer** that proposes before it builds, reuses what exists, and puts code where
  it belongs.
- **A reviewer** that checks each change with fresh eyes. It never sees the builder's reasoning.
- **A living architecture map** of how the pieces fit together right now, kept current with
  every change.
- **A drift check** (`.sly/check.py`) that catches what slips through: new libraries nobody
  logged, folders missing from the map, and map entries that no longer exist.
- **Stages** (Explore, MVP, Production) that set how hardened the code needs to be. How
  clean it is never changes by stage.

It works with any agent. The rules live in plain files (`AGENTS.md`, `docs/`, `.sly/`)
that Claude Code, Codex and others read. The Claude Code plugin adds real sub-agents,
slash commands and an automatic check.

## Install

**1. Get sly** (once):

```bash
git clone https://github.com/<you>/sly ~/tools/sly
```

**2. Add the Claude Code plugin** (once, optional but recommended). In Claude Code:

```
/plugin marketplace add <you>/sly
/plugin install sly@sly
```

**3. Set up a project.** In Claude Code, inside the project:

```
/sly:start a sentence about what you're building
```

This installs the files and has a short conversation with you. The representative writes
the intent and the map; you just answer a few questions.

**In Codex** (same plugin, same repo):

```
codex plugin marketplace add Kirch77/sly
```

Then install **sly** from `/plugins`, and trust its hooks when Codex asks (run `/hooks` to
review them). In a project, type `$sly-start` and a sentence about what you're building. After
that it works like Claude Code: ask normally, or use `$sly-build`, `$sly-checkup` and
`$sly-harden` (Codex uses `$` where Claude Code uses `/sly:`).

**Any other agent:** install the files directly, then ask it to "set up the project following
AGENTS.md":

```bash
python3 ~/tools/sly/install.py ~/path/to/project
```

Needs Python 3.11+ for the check. Your project can be in any language.

## Using it

| Command | What happens |
|---|---|
| `/sly:start` | Set up a project: short chat, then the intent, map and first plan. |
| `/sly:build <what you want>` | The full loop: brief, proposal, challenge, build, review, fix, report. |
| `/sly:harden` | Get ready for the next stage (usually Production): gaps in plain words, then fixes. |
| `/sly:checkup` | Look for drift. Cleans up what doesn't change behavior, asks about the rest. |

You don't have to type `/sly:build`. In a project set up with sly, just ask for what you want
in a normal chat: Claude starts the same flow on its own. For Codex and other agents,
`AGENTS.md` tells them to work the same way.

**Updating:** turn on auto-update once. In Claude Code run `/plugin`, open the
**Marketplaces** tab, select **sly**, and choose **Enable auto-update**. After that, new
versions install by themselves (they load the next time you start Claude Code). Each project's
sly files refresh automatically when you open the project, so there's nothing else to run.
Your intent, map and decisions are never touched.

To update by hand instead: run `/plugin`, open **Marketplaces**, select **sly**, and choose
**Update marketplace**, then restart Claude Code.

Before Claude finishes a turn while the project has uncommitted changes, the plugin runs the
drift check. If the current changes caused a problem, Claude has to fix it (or record why it's
intentional) before stopping. Older problems never block; `/sly:checkup` handles those.

## Taking over a drifted project

Run `/sly:start` in the project. sly maps what's actually there and drafts what the project is
supposed to be for you to confirm. If the code has drifted far, it recommends a rescue. Say
"clean up this project" (or run `/sly:checkup`) and it:

1. writes a target structure and a phased plan to `docs/CLEANUP.md`;
2. adds tests that pin down what the app does now, before changing anything;
3. works through the phases in order (delete dead code, merge duplicates, move things where
   they belong, simplify), each step small, reviewed, and leaving everything working;
4. lists bugs it finds for your OK instead of quietly changing behavior;
5. picks up where it left off in the next session (say "continue the cleanup").

## Pairs well with

**frontend-design** (Anthropic's official plugin) for projects with screens: install it next to
sly and the builder uses it automatically, following the "Look and feel" section that sly writes
into your intent during setup.

## What gets added to a project

```
AGENTS.md              how to work here (sly manages one marked block; the rest is yours)
CLAUDE.md              one line: @AGENTS.md, so Claude Code reads it
docs/
  INTENT.md            what you're building, for whom, why, and the stage      (yours)
  ARCHITECTURE.md      the map: pieces, flows, rules, where new things go       (yours)
  DECISIONS.md         one line per real decision and why                       (yours)
.sly/
  STANDARDS.md         what good code means, the solution ladder, stage lists   (sly's)
  roles/               representative, implementer, reviewer                    (sly's)
  check.py             the drift check                                          (sly's)
```

"Yours" files are never overwritten. With the plugin, sly's own files refresh automatically
when you open the project in Claude Code or Codex. For other agents, refresh them with:

```bash
python3 ~/tools/sly/install.py ~/path/to/project --update
```

## The drift check

```bash
python3 .sly/check.py              # compare with main
python3 .sly/check.py --base dev   # compare with another branch
```

It checks:
- **New outside libraries** (package.json, Cargo.toml, pyproject.toml, requirements*.txt,
  go.mod) must be named in `docs/DECISIONS.md`.
- **Every code folder is on the map.** Top-level folders, plus the folders inside `src/`,
  `lib/`, `packages/`, `crates/` and similar. Folders that aren't pieces can go on the
  `sly-ignore` line in the map.
- **Every folder the map mentions exists** (except under "Planned, not built yet").

Only problems connected to the current changes count as "to fix". Older ones show as notes
(`--all` counts them too). Reading `Cargo.toml` and `pyproject.toml` needs Python 3.11+.

It doesn't run your tests or linters. Keep using your project's own tools for that, and add
`python3 .sly/check.py` to CI next to them.

## Making it yours

- **Your standards:** edit `kit/sly/STANDARDS.md` in this repo, then `--update` your projects.
- **One project's conventions:** they go in that project's `docs/ARCHITECTURE.md` under
  "Patterns we use".
- **What the representative asks you about:** "When to ask the owner" in
  `kit/sly/roles/representative.md`.

After 5 to 10 real changes, look at what the reviewer kept catching and what you had to fix
by hand. Turn repeated problems into rules or checks, and delete rules that never matter.

## Testing how well it works

`bench/budget-tracker/` is a ready-made comparison: build the same small app with sly and with
plain Claude Code, then score both. See its README.

## Developing sly

```bash
python3 -m unittest discover tests
claude plugin validate .
```
