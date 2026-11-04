---
name: sly-start
description: Set up sly in the current project. Installs the sly files if needed, then the representative has a short conversation with the owner and writes the intent and the architecture map. Use when the owner asks to set up sly or start a project with sly.
---

Set up sly in this project.

1. If `.sly/` or `docs/INTENT.md` is missing, run the installer that comes with this plugin:
   `python3 <plugin folder>/install.py .`
   This skill file is at `<plugin folder>/codex/skills/sly-start/SKILL.md`, so the plugin folder
   is three folders up from it. If the project isn't a git repository, suggest `git init`
   (the drift check needs git to compare changes).
2. You are the representative. Read `.sly/roles/representative.md`, then follow
   `.sly/roles/setup.md` (new or existing project, whichever fits). For a large existing
   project, use subagents to survey areas in parallel.
