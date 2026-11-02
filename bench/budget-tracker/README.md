# Test: sly vs plain Claude Code

Build the same small app twice, once with sly and once without, then compare. The app is a
command-line budget tracker in Python, built in 5 rounds. Each round puts pressure on the
earlier design. Round 4 forces a change to the core data, which shows how well the first
design holds up. Round 5 tests whether sly's representative notices a request that stretches
your original goals.

Plan for an afternoon.

## What's here

| File | What it's for |
|---|---|
| `prompts/round-1.md` to `round-5.md` | The exact text to paste, one per round |
| `facts.md` | How to answer sly's setup questions, so both setups get the same information |
| `data/` | Bank CSV files with tricky cases built in |
| `checklist.md` | Score sheet: numbers, bug checks with expected answers, round 5, blind review |
| `blind-review.md` | Prompt for an unbiased comparison by a fresh Claude session |
| `score.py` | Counts lines, files, libraries and files changed per round, and makes the blind copies |

## Steps

**1. Make two empty project folders.** Copy the sample data into both.

```bash
mkdir -p ~/bench/with-sly ~/bench/plain
```

```bash
cp -r data ~/bench/with-sly/ && cp -r data ~/bench/plain/
```

```bash
cd ~/bench/with-sly && git init && git add -A && git commit -m "start"
```

```bash
cd ~/bench/plain && git init && git add -A && git commit -m "start"
```

**2. Keep it fair.**
- Same model in both. Check with `/model`.
- In the plain folder, sly must be off: run `/plugin`, find **sly** and disable it while you
  work there (or start Claude Code with plugins disabled). Turn it back on afterward.
- Paste the prompts word for word. Don't add hints or fix things by hand.
- When sly asks you something, answer only from `facts.md`, and count the questions.
- Plain Claude Code may ask questions too. Answer them from `facts.md` as well.

**3. Run the rounds.**

| Round | With sly (`~/bench/with-sly`) | Plain (`~/bench/plain`) |
|---|---|---|
| 1 | `/sly:start` then paste round 1 | Paste round 1 |
| 2 to 5 | Paste the round (sly runs its flow on its own) | Paste the round |

After **every** round, in both folders, check that it runs, then commit:

```bash
git add -A && git commit -m "round 1"
```

Change the number each time. `score.py` uses these commits to count what each round changed.

**4. Run the bug checks** in `checklist.md` after round 2 and after round 4.

**5. Count the numbers.**

```bash
python3 score.py compare ~/bench/with-sly ~/bench/plain
```

**6. Do the blind review.**

```bash
python3 score.py blind ~/bench/with-sly ~/bench/plain ~/bench/blind
```

Then follow `blind-review.md`. Open the answer key only after the review is done.

## Reading the results

sly is doing its job if it:
- changes fewer files in round 4, with a design that absorbed the change;
- uses less code and fewer libraries for the same working features;
- fails fewer bug checks;
- asks you about the dashboard in round 5, with a recommendation, instead of just building it;
- scores higher in the blind review, especially on structure and ease of change;
- gives you reports you understand without reading the code.

If plain Claude Code wins on something, note which round and what happened. That's exactly
what tells us which sly rules to tighten.
