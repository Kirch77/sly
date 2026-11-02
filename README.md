# keel

Keeps AI coding agents on course.

Agents are good at finishing the task in front of them, but over many sessions the code
drifts: helpers get duplicated, things land in convenient places instead of the right ones,
and the project slowly stops matching what you set out to build. Each change makes the next
one harder.

keel fixes the root cause, which is lost intent. It writes down what you want, why you want
it, and how the system fits together, and gives one agent the job of protecting all that.

- **A representative** that works for you. It knows your goals and the reasons behind them,
  runs the work, challenges the builder, makes the technical calls itself, and only comes to
  you when something would change what you get. It talks in plain words.
- **An implementer** that proposes before it builds, reuses what exists, and puts code where
  it belongs.
- **A reviewer** that checks each change with fresh eyes. It never sees the builder's reasoning.
- **A living architecture map** of how the pieces fit together right now, kept current with
  every change.
- **A drift check** (`.keel/check.py`) that catches what slips through: new libraries nobody
  logged, folders missing from the map, and map entries that no longer exist.
- **Stages** (Explore, MVP, Production) that set how hardened the code needs to be. How
  clean it is never changes by stage.

It works with any agent. The rules live in plain files (`AGENTS.md`, `docs/`, `.keel/`)
that Claude Code, Codex and others read. The Claude Code plugin adds real sub-agents,
slash commands and an automatic check.

## Install

**1. Get keel** (once):

```bash
git clone https://github.com/<you>/keel ~/tools/keel
```

**2. Add the Claude Code plugin** (once, optional but recommended). In Claude Code:

```
/plugin marketplace add <you>/keel
/plugin install keel@keel
```

**3. Set up a project.** In Claude Code, inside the project:

```
/keel:start a sentence about what you're building
```

This installs the files and has a short conversation with you. The representative writes
the intent and the map; you just answer a few questions.

Without the plugin (or for Codex), install the files directly, then ask the agent to "set up
the project following AGENTS.md":

```bash
python3 ~/tools/keel/install.py ~/path/to/project
```

Needs Python 3.11+ for the check. Your project can be in any language.

## Using it

| Command | What happens |
|---|---|
| `/keel:start` | Set up a project: short chat, then the intent, map and first plan. |
| `/keel:build <what you want>` | The full loop: brief, proposal, challenge, build, review, fix, report. |
| `/keel:harden` | Get ready for the next stage (usually Production): gaps in plain words, then fixes. |
| `/keel:checkup` | Look for drift. Cleans up what doesn't change behavior, asks about the rest. |

You don't have to use the commands. `AGENTS.md` tells any agent to work this way, so in a
normal conversation the agent still acts as your representative.

Before Claude finishes a turn while the project has uncommitted changes, the plugin runs the
drift check. If the current changes caused a problem, Claude has to fix it (or record why it's
intentional) before stopping. Older problems never block; `/keel:checkup` handles those.

## What gets added to a project

```
AGENTS.md              how to work here (keel manages one marked block; the rest is yours)
CLAUDE.md              one line: @AGENTS.md, so Claude Code reads it
docs/
  INTENT.md            what you're building, for whom, why, and the stage      (yours)
  ARCHITECTURE.md      the map: pieces, flows, rules, where new things go       (yours)
  DECISIONS.md         one line per real decision and why                       (yours)
.keel/
  STANDARDS.md         what good code means, the solution ladder, stage lists   (keel's)
  roles/               representative, implementer, reviewer                    (keel's)
  check.py             the drift check                                          (keel's)
```

"Yours" files are never overwritten. To get a newer version of keel's files:

```bash
python3 ~/tools/keel/install.py ~/path/to/project --update
```

## The drift check

```bash
python3 .keel/check.py              # compare with main
python3 .keel/check.py --base dev   # compare with another branch
```

It checks:
- **New outside libraries** (package.json, Cargo.toml, pyproject.toml, requirements*.txt,
  go.mod) must be named in `docs/DECISIONS.md`.
- **Every code folder is on the map.** Top-level folders, plus the folders inside `src/`,
  `lib/`, `packages/`, `crates/` and similar. Folders that aren't pieces can go on the
  `keel-ignore` line in the map.
- **Every folder the map mentions exists** (except under "Planned, not built yet").

Only problems connected to the current changes count as "to fix". Older ones show as notes
(`--all` counts them too). Reading `Cargo.toml` and `pyproject.toml` needs Python 3.11+.

It doesn't run your tests or linters. Keep using your project's own tools for that, and add
`python3 .keel/check.py` to CI next to them.

## Making it yours

- **Your standards:** edit `kit/keel/STANDARDS.md` in this repo, then `--update` your projects.
- **One project's conventions:** they go in that project's `docs/ARCHITECTURE.md` under
  "Patterns we use".
- **What the representative asks you about:** "When to ask the owner" in
  `kit/keel/roles/representative.md`.

After 5 to 10 real changes, look at what the reviewer kept catching and what you had to fix
by hand. Turn repeated problems into rules or checks, and delete rules that never matter.

## Developing keel

```bash
python3 -m unittest discover tests
claude plugin validate .
```
