#!/usr/bin/env python3
"""Install sly into a project, or update it.

  python3 install.py [PROJECT_DIR]            install (default: current folder)
  python3 install.py [PROJECT_DIR] --update   refresh sly's own files to this version

Your project's files (docs/INTENT.md, docs/ARCHITECTURE.md, docs/DECISIONS.md, and anything
outside the sly block in AGENTS.md) are never overwritten. --update only refreshes
.sly/ (roles, standards, check) and the sly block in AGENTS.md.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent / "kit"
START = re.compile(r"^<!-- sly:start", re.M)
END = re.compile(r"^<!-- sly:end -->", re.M)
BLOCK = re.compile(r"^<!-- sly:start.*?^<!-- sly:end -->\n?", re.S | re.M)
CLAUDE_IMPORT = "@AGENTS.md"


def imports_agents(text: str) -> bool:
    """True if CLAUDE.md already imports AGENTS.md (outside code blocks)."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.search(r"(?<![\w/])@(\./)?AGENTS\.md\b", text) is not None


def install(project: Path, update: bool) -> list[str]:
    log: list[str] = []

    # sly's own files: .sly/ (refreshed by --update)
    for src in sorted((KIT / "sly").rglob("*")):
        rel = src.relative_to(KIT / "sly")
        if src.is_dir() or any(p.startswith(".") or p == "__pycache__" for p in rel.parts):
            continue
        dest = project / ".sly" / rel
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            log.append(f"added    .sly/{rel}")
        elif dest.read_bytes() != src.read_bytes():
            if update:
                shutil.copy2(src, dest)
                log.append(f"updated  .sly/{rel}")
            else:
                log.append(f"kept     .sly/{rel} (differs; run with --update to refresh)")

    # the project's own files: docs/ (only added if missing, never overwritten)
    for src in sorted((KIT / "docs").glob("*.md")):
        dest = project / "docs" / src.name
        if dest.exists():
            log.append(f"kept     docs/{src.name} (yours)")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            log.append(f"added    docs/{src.name}")

    # AGENTS.md: sly manages only its marked block
    block = (KIT / "AGENTS.block.md").read_text(encoding="utf-8")
    agents = project / "AGENTS.md"
    if not agents.exists():
        agents.write_text(block, encoding="utf-8")
        log.append("added    AGENTS.md")
    else:
        text = agents.read_text(encoding="utf-8")
        starts, ends = len(START.findall(text)), len(END.findall(text))
        if (starts, ends) not in ((0, 0), (1, 1)):
            log.append("SKIPPED  AGENTS.md: it has broken or repeated sly markers. Fix them by hand "
                       "(one '<!-- sly:start' line and one '<!-- sly:end -->' line), then rerun.")
        elif not BLOCK.search(text):
            agents.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")
            log.append("updated  AGENTS.md (added the sly block at the end)")
        elif BLOCK.search(text).group(0) != block:
            if update:
                agents.write_text(BLOCK.sub(lambda _: block, text, count=1), encoding="utf-8")
                log.append("updated  AGENTS.md (sly block only)")
            else:
                log.append("kept     AGENTS.md sly block (differs; run with --update to refresh)")

    # CLAUDE.md: make Claude Code read AGENTS.md
    claude = project / "CLAUDE.md"
    if not claude.exists():
        claude.write_text(CLAUDE_IMPORT + "\n", encoding="utf-8")
        log.append("added    CLAUDE.md (points Claude Code at AGENTS.md)")
    elif not imports_agents(claude.read_text(encoding="utf-8")):
        text = claude.read_text(encoding="utf-8")
        claude.write_text(text.rstrip() + "\n\n" + CLAUDE_IMPORT + "\n", encoding="utf-8")
        log.append("updated  CLAUDE.md (added @AGENTS.md)")

    return log


def main() -> int:
    parser = argparse.ArgumentParser(description="Install or update sly in a project.")
    parser.add_argument("project", nargs="?", default=".", help="project folder (default: here)")
    parser.add_argument("--update", action="store_true", help="refresh sly's own files")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
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
