# Standards

What good code means in this project. Every role follows this. The goal is the best
solution to the problem, not the most code. Clean, fitting, easy to change. Smaller code
usually follows, but it is a result, never the target.

## 1. Pick the solution before writing code

Go down this ladder and stop at the first step that works:

1. **Does this need to exist?** Maybe the requirement can be simpler, or a setting already covers it.
2. **Can existing code do it?** Search first. Reuse it, or extend it a little.
3. **Is there a well-maintained library or tool for it?** Use it for solved, generic problems
   (parsing, dates, crypto, HTTP). Build it yourself when it is the core of what this project does.
   A new library always needs a reason logged in `docs/DECISIONS.md`. The representative
   decides ordinary ones; big ones that shape the whole project go to the owner.
4. **Write the smallest clean code that fully solves it.**

## 2. Core rules (every stage)

**Fit the system**
- Read `docs/ARCHITECTURE.md` and the code you are about to touch before changing anything.
- Put code where the map's "Where new things go" says. If nothing fits, raise it with the
  representative, who decides and updates the map. Do not invent a new place quietly.
- Do it the way the map's "Patterns we use" says, even if you would personally do it another way.
  Consistency beats local cleverness. Never copy what the map lists under "Known rough spots".
- Respect the rules about which piece may use which. Never reach into another piece's insides;
  use what it offers to the outside.

**Shape**
- One job per piece. A function does one thing, a file holds one idea, a module owns one area.
- Keep each fact in one place. A rule, a setting, a piece of logic exists once.
  If you copy it, you now have two things to keep in sync.
- Pull out shared code when something repeats for the second or third time, not the first.
  Wrong sharing is worse than a little repetition.
- Keep the connections between pieces small and simple: few inputs, clear outputs.
- Keep the outside world at the edges. Reading files, network calls, databases, the clock
  and randomness belong in a few clear places. The logic in the middle should be plain
  functions that are easy to understand and test.

**Build only what is needed now**
- Every abstraction (interface, base class, wrapper, plugin system, config option, generic
  helper) must point to a need that exists today. "We might need it later" does not count.
- No unused parameters, options, or branches "just in case".
- Prefer plain functions and plain data until something proves it needs more.

**Readable**
- Names say what a thing is or does. If it needs a comment to explain *what* it is, rename it.
  Comments explain *why* when the why is not obvious.
- Short functions, shallow nesting, early returns. No clever tricks. Code is read far more
  than it is written.
- Make data flow visible. It should be obvious where a value comes from and what changes it.
  Avoid hidden shared state.

**Honest**
- Handle errors on purpose. Never swallow them silently. Either deal with it, or pass it up
  with a clear message about what failed and why.
- Delete dead code, unused imports and leftover experiments. Version control remembers.
- Leave code you touch a little cleaner (a better name, a removed duplicate). Bigger cleanups
  go to the representative first, so a change stays focused.

## 3. What each stage adds

The stage is set in `docs/INTENT.md`. Section 2 applies to every stage except Explore.
A stage changes how *hardened* the code is, never how *clean* it is.

**Explore**: answering a question ("can this work?", "which approach is faster?")
- Speed over polish. Keep it in a folder or branch clearly marked as throwaway.
- Never build on explore code. When the question is answered, write down what was learned in
  `docs/DECISIONS.md` and delete the code.

**MVP**: proving the idea with real users
- All core rules.
- The main ways things can fail are handled with clear messages.
- Inputs from outside (users, files, network) are checked before use.
- No secrets in code or in the repository.
- Tests for the core logic, the part that would hurt most if it were wrong.
- A README that says what it is and how to run it.

**Production**: people depend on it
- Everything in MVP.
- Every failure is handled: nothing crashes without a clear message, and nothing fails silently.
- Tests cover core logic, important edge cases, and the main flows from start to finish.
- Security reviewed: inputs, logins and permissions, secrets, dependencies with known problems.
- Logging that is enough to figure out what went wrong, without leaking private data.
- Performance checked where it matters, measured rather than guessed.
- Settings come from configuration, not hard-coded values.
- Changes to stored data (database changes, file format changes) are safe and can be undone.
- Docs explain how to set it up, run it, and fix common problems.

## 4. Signs of trouble

The reviewer looks for these. Everyone should avoid them.
- A new helper that does what an existing one already does.
- An interface or abstraction with exactly one user.
- A file placed somewhere because it was convenient, not because the map says so.
- A new pattern for something the project already has a pattern for.
- A function that needs "and" to describe what it does.
- Settings, magic numbers, or logic copied into a second place.
- Code that handles cases that cannot happen today.
- A change much bigger than the request needed.
- Anything you would have to explain twice to a new teammate.
