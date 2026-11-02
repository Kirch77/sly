# Blind review prompt

Run `python3 score.py blind <sly-project> <plain-project> <output-folder>` first. It copies the
code into folders `A` and `B` in a random order (sly's own files removed) and writes the answer
key to a separate file. Open a **fresh** Claude Code session in the output folder and paste:

---

There are two codebases here, `A/` and `B/`. Both are command-line budget trackers in Python
built from the same requirements: add expenses, monthly summaries by category, importing two
bank CSV formats without duplicates, monthly budgets with warnings, Markdown/JSON reports, and
shared expenses between two people with who-owes-whom.

Compare them as a senior engineer who is joining the project and will maintain it. Read the
code; run it if useful.

Score each from 1 to 10 on:
1. Structure: are responsibilities clearly separated? Is it obvious where things live?
2. Duplication: is logic repeated?
3. Simplicity: is there unnecessary code, abstraction or cleverness? Is anything missing?
4. Naming and readability.
5. Error handling: bad input, broken files, edge cases.
6. Correctness: any bugs you can find (money rounding, dates, duplicates, splitting).
7. Ease of change: how much would you have to touch to add "recurring monthly expenses"?
   Name the files.

Give file and line references for your main points. End with: which one would you rather
maintain, and why, in two sentences.
