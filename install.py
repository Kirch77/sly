#!/usr/bin/env python3
"""Install sly into a project, or update it.

  python3 install.py [PROJECT_DIR]            install (default: current folder)
  python3 install.py [PROJECT_DIR] --update   refresh sly's own files to this version
  python3 install.py [PROJECT_DIR] --auto     quiet refresh, only if the project already uses an
                                              older sly (the plugin runs this when a session starts)

Your project's files (docs/INTENT.md, docs/ARCHITECTURE.md, docs/DECISIONS.md, and anything
outside the sly block in AGENTS.md) are never overwritten. --update only refreshes
.sly/ (roles, standards, check), sly's Codex agents in .codex/agents/, and the sly block in
AGENTS.md.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent / "kit"
START = re.compile(r"^<!-- sly:start", re.M)
END = re.compile(r"^<!-- sly:end -->", re.M)
BLOCK = re.compile(r"^<!-- sly:start.*?^<!-- sly:end -->\n?", re.S | re.M)
CLAUDE_IMPORT = "@AGENTS.md"
# sly's own files: kit folder -> where it goes in a project. Refreshed by --update.
OWNED = [("sly", ".sly"), ("codex-agents", ".codex/agents")]
VERSION = json.loads((KIT.parent / ".claude-plugin" / "plugin.json").read_text())["version"]


def version_tuple(text: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in text.strip().split("."))
    except ValueError:
        return (0,)


def imports_agents(text: str) -> bool:
    """True if CLAUDE.md already imports AGENTS.md (outside code blocks)."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.search(r"(?<![\w/])@(\./)?AGENTS\.md\b", text) is not None


def install(project: Path, update: bool, add_project_files: bool = True) -> list[str]:
    """Copies sly into the project. With add_project_files=False, only sly's own files
    (.sly/ and an existing AGENTS.md block) are touched."""
    log: list[str] = []

    for kit_folder, target in OWNED:
        for src in sorted((KIT / kit_folder).rglob("*")):
            rel = src.relative_to(KIT / kit_folder)
            if src.is_dir() or any(p.startswith(".") or p == "__pycache__" for p in rel.parts):
                continue
            dest, shown = project / target / rel, f"{target}/{rel.as_posix()}"
            if not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                log.append(f"added    {shown}")
            elif dest.read_bytes() != src.read_bytes():
                if update:
                    shutil.copy2(src, dest)
                    log.append(f"updated  {shown}")
                else:
                    log.append(f"kept     {shown} (differs; run with --update to refresh)")
    version_file = project / ".sly" / "VERSION"
    if update or not version_file.exists():
        version_file.write_text(VERSION + "\n", encoding="utf-8")

    if not add_project_files:
        return log + refresh_agents_block(project, update=True, create=False)
    return log + add_docs(project) + refresh_agents_block(project, update, create=True) \
        + link_claude_md(project)


def add_docs(project: Path) -> list[str]:
    log: list[str] = []
    # the project's own files: docs/ (only added if missing, never overwritten)
    for src in sorted((KIT / "docs").glob("*.md")):
        dest = project / "docs" / src.name
        if dest.exists():
            log.append(f"kept     docs/{src.name} (yours)")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            log.append(f"added    docs/{src.name}")

    return log


def refresh_agents_block(project: Path, update: bool, create: bool) -> list[str]:
    """AGENTS.md: sly manages only its marked block."""
    log: list[str] = []
    block = (KIT / "AGENTS.block.md").read_text(encoding="utf-8")
    agents = project / "AGENTS.md"
    if not agents.exists():
        if not create:
            return log
        agents.write_text(block, encoding="utf-8")
        log.append("added    AGENTS.md")
    else:
        text = agents.read_text(encoding="utf-8")
        starts, ends = len(START.findall(text)), len(END.findall(text))
        if (starts, ends) not in ((0, 0), (1, 1)):
            log.append("SKIPPED  AGENTS.md: it has broken or repeated sly markers. Fix them by hand "
                       "(one '<!-- sly:start' line and one '<!-- sly:end -->' line), then rerun.")
        elif not BLOCK.search(text):
            if not create:
                return log
            agents.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")
            log.append("updated  AGENTS.md (added the sly block at the end)")
        elif BLOCK.search(text).group(0) != block:
            if update:
                agents.write_text(BLOCK.sub(lambda _: block, text, count=1), encoding="utf-8")
                log.append("updated  AGENTS.md (sly block only)")
            else:
                log.append("kept     AGENTS.md sly block (differs; run with --update to refresh)")
    return log


def link_claude_md(project: Path) -> list[str]:
    """CLAUDE.md: make Claude Code read AGENTS.md."""
    log: list[str] = []
    claude = project / "CLAUDE.md"
    if not claude.exists():
        claude.write_text(CLAUDE_IMPORT + "\n", encoding="utf-8")
        log.append("added    CLAUDE.md (points Claude Code at AGENTS.md)")
    elif not imports_agents(claude.read_text(encoding="utf-8")):
        text = claude.read_text(encoding="utf-8")
        claude.write_text(text.rstrip() + "\n\n" + CLAUDE_IMPORT + "\n", encoding="utf-8")
        log.append("updated  CLAUDE.md (added @AGENTS.md)")

    return log


def auto_refresh(project: Path) -> int:
    """Run by the plugin when a session starts. Never fails loudly: a broken refresh must not
    get in the way of the session."""
    sly_dir = project / ".sly"
    if not sly_dir.is_dir() or project == KIT.parent or KIT.parent in project.parents:
        return 0
    version_file = sly_dir / "VERSION"
    current = version_file.read_text().strip() if version_file.is_file() else "an older version"
    if version_tuple(current) >= version_tuple(VERSION):
        return 0  # up to date, or newer (don't downgrade a project set up elsewhere)
    try:
        changed = [line for line in install(project, update=True, add_project_files=False)
                   if not line.startswith("kept")]
    except Exception as error:
        print(f"sly: couldn't refresh this project's sly files ({error}).")
        return 0
    if changed:
        print(f"sly: refreshed this project's sly files from {current} to {VERSION} "
              "(.sly/ and the sly block in AGENTS.md; intent, map and decisions untouched).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Install or update sly in a project.")
    parser.add_argument("project", nargs="?", default=".", help="project folder (default: here)")
    parser.add_argument("--update", action="store_true", help="refresh sly's own files")
    parser.add_argument("--auto", action="store_true",
                        help="quiet refresh, only for projects on an older sly")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    if args.auto:
        return auto_refresh(project)
    if not project.is_dir():
        print(f"Folder not found: {project}", file=sys.stderr)
        return 1
    if project == KIT.parent or KIT.parent in project.parents:
        print("That's inside the sly folder itself. Point the installer at your project.",
              file=sys.stderr)
        return 1

    log = install(project, args.update)
    print(f"sly -> {project}")
    print("\n".join("  " + line for line in log) or "  already up to date")
    if not args.update:
        print("\nNext: open the project in Claude Code and run /sly:start "
              "(or ask any agent to 'set up the project following AGENTS.md').")
    return 0


if __name__ == "__main__":
    sys.exit(main())
