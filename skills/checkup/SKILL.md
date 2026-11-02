---
name: checkup
description: Look for drift. The representative compares the code with the intent, the architecture map and the standards, cleans up what doesn't change behavior, and brings the owner only what does.
disable-model-invocation: true
---

You are the representative. Read `.sly/roles/representative.md` and follow "Checkups".
Use `sly:reviewer` agents (in parallel, one per piece or slice if the project is large), telling
each one it is reviewing an area, not a change. Make cleanups with the implementer and
reviewer, as in "Handling a request".
