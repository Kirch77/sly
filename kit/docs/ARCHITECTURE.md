# Architecture

The map of how this project fits together **right now**. Anyone, person or agent, should be
able to read this and know where things are, how they connect, and where new things go.
The representative maintains it. The owner never has to.

Rules for this file:
- Describe what exists, not what might exist. Plans go in the last section.
- Update it in the same change as the code.
- Write folders as `path/` (in backticks, ending in `/`). `.keel/check.py` uses that to
  check the map against the real folders.
- Keep it short. If it gets long, the design may be getting too complicated.

<!-- Folders that aren't pieces (vendored code, fixtures) can be listed after keel-ignore below, comma separated, like vendor/, fixtures/ -->
<!-- keel-ignore: -->

## In one paragraph

[fill in: what the system does and how, in plain words. Someone new should get the big
picture from this alone.]

## The pieces

| Piece | Folder | What it does | Uses | Used by |
|---|---|---|---|---|
| [fill in] | `src/example/` | [one sentence] | [other pieces] | [other pieces] |

## How things flow

Step by step, what happens for the main things the system does.

**[fill in: e.g. "A user runs a command"]**
1. [piece] does ...
2. [piece] does ...

## The rules

Which pieces may use which, and things that must always stay true.

- [fill in: e.g. "The parser never touches the file system; it only gets text."]

## Where new things go

The most important section for keeping the project tidy. When adding something, look here first.

| To add... | Put it in... | Follow the example of... |
|---|---|---|
| [fill in: e.g. a new command] | `src/commands/` | `src/commands/run.rs` |

## Patterns we use

How common things are done here, so every part looks like it was written by one person.

- **Errors:** [fill in]
- **Naming:** [fill in]
- **Settings:** [fill in]
- **Tests:** [fill in]

## Word list

Words that mean something specific in this project.

- **[fill in]**: [plain explanation]

## Planned, not built yet

Ideas for later. Nothing here exists in the code yet.

- [fill in, or "none"]
