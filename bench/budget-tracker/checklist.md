# Score sheet

Fill in one column per setup. Commit after every round in both projects
(`git add -A && git commit -m "round N"`), so `score.py` can count what each round changed.

## Numbers (from `python3 score.py compare <sly-project> <plain-project>`)

| | sly | Plain |
|---|---|---|
| Lines of code (not tests) | | |
| Code files | | |
| Lines of tests | | |
| Outside libraries | | |
| Files changed in round 2 | | |
| Files changed in round 3 | | |
| **Files changed in round 4** (lower usually means a better design) | | |
| Questions it asked you (count them) | | |

## Bug checks (after round 2)

Copy `data/` into the project first. Use the tool's own commands. Mark each one pass or fail.

| # | Do this | Expected | sly | Plain |
|---|---|---|---|---|
| 1 | Import `bank_a.csv` and `bank_b.csv`, then show March | March spending **339.56** | | |
| 2 | Show April | April spending **38.90** (the 31 March items stay in March) | | |
| 3 | Import both files **again** | Nothing new is added; totals unchanged | | |
| 4 | Check the two `STREAMFLIX 12.10` rows on 12 March | Both kept: they're two real charges in one file (bonus point, it's a judgment call) | | |
| 5 | Check `Refund Online Shop` (19.99, Credit only) | Treated as money in, not spending | | |
| 6 | Check `Cinema` on `12/03/2026` | 12 **March**, not 3 December | | |
| 7 | Check `HARDWARE STORE, MAIN ST` | The comma inside the quotes doesn't break the row | | |
| 8 | Totals with cents (12.10, 45.99, 50.10) | Exact to the cent, no 339.5600000001 | | |
| 9 | Import `bank_b_broken.csv` | Clear message about the bad rows (impossible date, missing columns, bad amount), good rows handled sensibly, no crash | | |
| 10 | Add an expense with a negative or non-number amount, or a bad date | Clear error, nothing saved | | |
| 11 | Delete or empty the data file, then run any command | Works (starts fresh) or explains, no crash | | |

## After round 4

| # | Do this | Expected | sly | Plain |
|---|---|---|---|---|
| 12 | Expense 100.00 paid by you, split 50/50 | Partner owes you 50.00 | | |
| 13 | Then: expense 10.00 paid by partner, your share 70% | You owe 7.00 for this one, so overall partner owes you **43.00** | | |
| 14 | Old expenses from rounds 1 to 3 | Still work and show up sensibly | | |

## Round 5 (the intent test)

| | sly | Plain |
|---|---|---|
| Did it notice the dashboard conflicts with "offline, simple, command-line"? | | |
| Did it ask you, with a recommendation, before building? | | |
| If it built it: did it keep it offline and separate from the core? | | |

## Blind review (see `blind-review.md`)

| | A | B |
|---|---|---|
| Structure | | |
| Duplication | | |
| Simplicity | | |
| Naming | | |
| Error handling | | |
| Correctness | | |
| Ease of change | | |
| Reviewer would rather maintain | | |

Answer key (which was sly): see the file `score.py blind` wrote.

## Your own judgment

- Which reports were clearer to you?
- Which would you rather keep building on?
