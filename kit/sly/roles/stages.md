# Moving to the next stage (hardening)

For the representative. The stage in `docs/INTENT.md` sets the quality bar (see
`.sly/STANDARDS.md`). When the owner wants to move up a stage, usually MVP to Production:

1. **Compare the whole project** against the target stage's list in `STANDARDS.md`, with
   reviewers on slices of the project if it is large. Tell each reviewer it is reviewing an
   area against the target stage, not a change.
2. **Check what lives outside the code:** hosting, backups, monitoring, where secrets are
   kept, how it gets deployed, how someone new would set it up.
3. **Give the owner a short list of gaps,** most important first: what's missing in plain
   words, why it matters to them, about how much work, and which ones must happen before the
   move versus which can wait. Recommend.
4. **After they approve,** fix the code gaps with the normal loop ("Handling a request" in
   `representative.md`), and give simple steps for gaps outside the code.
5. **Update the stage** in `INTENT.md` and log it as an owner decision.
