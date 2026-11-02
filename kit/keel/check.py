#!/usr/bin/env python3
"""keel check: catches drift that is easy to miss.

It checks three things:
  1. Every new outside library is logged in docs/DECISIONS.md.
  2. Every code folder is on the map (docs/ARCHITECTURE.md).
  3. Every folder on the map still exists.

It does not run tests or linters; the project's own tools do that.

Usage:
  python3 .keel/check.py              compare with the main branch
  python3 .keel/check.py --base REF   compare with another branch or commit
  python3 .keel/check.py --hook       Claude Code Stop hook mode (reads hook JSON on stdin)

Exit code: 0 = all good, 1 = something to fix (2 in hook mode, which tells Claude to keep going).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    tomllib = None

ROOT = Path(__file__).resolve().parent.parent
INTENT = "docs/INTENT.md"
MAP = "docs/ARCHITECTURE.md"
DECISIONS = "docs/DECISIONS.md"

# Folders whose subfolders are the real pieces (src/parser/ rather than src/).
CONTAINERS = {"src", "lib", "app", "apps", "packages", "crates", "internal", "cmd",
              "pkg", "services", "modules", "components"}
# Folders that don't need to be on the map.
NOT_PIECES = {"docs", "tests", "test", "spec", "__tests__"}
# Skipped when walking a folder that isn't a git repository.
JUNK = {"node_modules", "target", "dist", "build", "venv", "__pycache__"}


# ---------- small helpers ----------

def git(*args: str) -> str | None:
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    except FileNotFoundError:
        return None
    return r.stdout if r.returncode == 0 else None


def read(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def normalize(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def project_files() -> list[str]:
    """Every file in the project, minus what git ignores."""
    listed = git("ls-files", "--cached", "--others", "--exclude-standard")
    if listed is not None:
        return [f for f in listed.splitlines() if (ROOT / f).exists()]
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in JUNK]
        rel = Path(dirpath).relative_to(ROOT)
        files += [(rel / f).as_posix() for f in filenames]
    return files


def find_base(explicit: str | None) -> tuple[str | None, str]:
    """The commit to compare with, and a label for it. None means 'no history yet'."""
    if explicit:
        sha = git("rev-parse", "--verify", explicit)
        if sha is None:
            sys.exit(f"keel check: can't find '{explicit}' in git.")
        return sha.strip(), explicit
    if git("rev-parse", "--verify", "HEAD") is None:
        return None, "nothing (no commits yet)"
    for branch in ("origin/main", "main", "origin/master", "master"):
        if git("rev-parse", "--verify", "--quiet", branch) is not None:
            merge_base = git("merge-base", "HEAD", branch)
            if merge_base:
                return merge_base.strip(), branch
    return "HEAD", "the last commit"


# ---------- reading dependency files ----------

PEP508_NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def pep508(spec: str) -> set[str]:
    match = PEP508_NAME.match(spec) if isinstance(spec, str) else None
    return {normalize(match.group(1))} if match else set()


def deps_package_json(text: str) -> set[str]:
    data = json.loads(text)
    sections = ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies")
    return {normalize(name) for s in sections for name in data.get(s, {})}


def deps_cargo(text: str) -> set[str]:
    data = tomllib.loads(text)
    found: set[str] = set()

    def take(table: dict) -> None:
        for s in ("dependencies", "dev-dependencies", "build-dependencies"):
            found.update(normalize(name) for name in table.get(s, {}))

    take(data)
    take(data.get("workspace", {}))
    for target in data.get("target", {}).values():
        take(target)
    return found


def deps_pyproject(text: str) -> set[str]:
    data = tomllib.loads(text)
    found: set[str] = set()
    project = data.get("project", {})
    for spec in project.get("dependencies", []):
        found |= pep508(spec)
    for group in project.get("optional-dependencies", {}).values():
        for spec in group:
            found |= pep508(spec)
    for group in data.get("dependency-groups", {}).values():
        for spec in group:
            found |= pep508(spec)
    poetry = data.get("tool", {}).get("poetry", {})
    tables = [poetry.get("dependencies", {}), poetry.get("dev-dependencies", {})]
    tables += [g.get("dependencies", {}) for g in poetry.get("group", {}).values()]
    for table in tables:
        found.update(normalize(name) for name in table if name != "python")
    return found


def deps_requirements(text: str) -> set[str]:
    found: set[str] = set()
    for line in text.splitlines():
        line = line.split("#")[0].strip()
        if line and not line.startswith("-"):
            found |= pep508(line)
    return found


def deps_go_mod(text: str) -> set[str]:
    found: set[str] = set()
    in_block = False
    for line in text.splitlines():
        line = line.split("//")[0].strip()
        if line.startswith("require ("):
            in_block = True
        elif in_block and line == ")":
            in_block = False
        elif in_block and line:
            found.add(normalize(line.split()[0]))
        elif line.startswith("require "):
            found.add(normalize(line.split()[1]))
    return found


def parser_for(path: str):
    name = path.rsplit("/", 1)[-1]
    if name == "package.json":
        return deps_package_json
    if name == "Cargo.toml":
        return deps_cargo
    if name == "pyproject.toml":
        return deps_pyproject
    if name == "go.mod":
        return deps_go_mod
    if name.startswith("requirements") and name.endswith(".txt"):
        return deps_requirements
    return None


# ---------- the checks ----------

class Report:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.problems = 0

    def ok(self, message: str) -> None:
        self.lines.append(f"  ok    {message}")

    def note(self, message: str) -> None:
        self.lines.append(f"  note  {message}")

    def fix(self, message: str, how: str) -> None:
        self.problems += 1
        self.lines.append(f"  FIX   {message}\n        -> {how}")


def check_libraries(report: Report, files: list[str], base: str | None) -> None:
    now: dict[str, str] = {}   # library -> the file that lists it
    before: set[str] = set()
    toml_skipped = False
    for path in files:
        parse = parser_for(path)
        if parse is None:
            continue
        if tomllib is None and path.endswith(".toml"):
            toml_skipped = True
            continue
        try:
            for name in parse(read(path)):
                now.setdefault(name, path)
        except Exception as error:  # a broken file shouldn't stop the other checks
            report.note(f"Couldn't read {path} ({error}).")
            continue
        old = git("show", f"{base}:{path}") if base else None
        if old:
            try:
                before |= parse(old)
            except Exception:
                pass  # the old version was broken; treat everything as new
    if toml_skipped:
        report.note("Skipped .toml files: Python 3.11+ is needed to read them.")

    decisions = normalize(read(DECISIONS))
    new = sorted(set(now) - before)
    unlogged = [name for name in new if name not in decisions]
    for name in unlogged:
        report.fix(f'New library "{name}" (in {now[name]}) isn\'t in {DECISIONS}.',
                   f"If it's worth it, log it there with the reason (the representative decides). Or remove it.")
    if not new:
        report.ok("No new outside libraries.")
    elif not unlogged:
        report.ok(f"New libraries are all logged in {DECISIONS}: {', '.join(new)}.")


def code_folders(files: list[str]) -> set[str]:
    folders: set[str] = set()
    for path in files:
        parts = path.split("/")
        if len(parts) < 2 or parts[0].startswith(".") or parts[0] in NOT_PIECES:
            continue
        top = parts[0]
        if top in CONTAINERS and len(parts) >= 3 and not parts[1].startswith(".") \
                and parts[1] not in NOT_PIECES:
            folders.add(f"{top}/{parts[1]}")
        else:
            folders.add(top)
    return folders


def on_map(folder: str, map_text: str) -> bool:
    return re.search(r"(?<![\w./-])" + re.escape(folder) + r"[/`]", map_text) is not None


def check_map(report: Report, files: list[str]) -> None:
    map_text = read(MAP)
    if not map_text:
        report.fix(f"There's no map at {MAP}.", "Create it (run setup) before building more.")
        return

    ignored = [item.strip().strip("`").rstrip("/")
               for line in re.findall(r"keel-ignore:([^\n>]*)", map_text)
               for item in line.split(",") if item.strip().strip("`")]

    def is_ignored(folder: str) -> bool:
        return any(folder == i or folder.startswith(i + "/") for i in ignored)

    missing = sorted(f for f in code_folders(files) if not is_ignored(f) and not on_map(f, map_text))
    for folder in missing:
        report.fix(f"Folder {folder}/ isn't on the map.",
                   f"Add it to \"The pieces\" in {MAP}, or to keel-ignore if it isn't a piece.")

    # Folders the map mentions (from the first section up to "Planned") must exist.
    body = re.split(r"^##\s", map_text, maxsplit=1, flags=re.M)
    body = body[1] if len(body) > 1 else ""
    body = re.split(r"^##\s+Planned", body, maxsplit=1, flags=re.M | re.I)[0]
    stale = sorted({p.removeprefix("./") for p in re.findall(r"`([^`\s*<>\[\]]+/)`", body)
                    if not (ROOT / p.removeprefix("./")).is_dir()})
    for folder in stale:
        report.fix(f"The map mentions {folder} but that folder doesn't exist.",
                   f"Update {MAP} to match the code (or move it under \"Planned, not built yet\").")

    if not missing and not stale:
        report.ok("The map matches the folders in the project.")


def stage_of(intent_text: str) -> str | None:
    match = re.search(r"\*\*Stage:\*\*\s*(Explore|MVP|Production)\b", intent_text, re.I)
    return match.group(1) if match else None


def run(base_arg: str | None) -> tuple[Report, bool]:
    """Runs every check. Returns the report and whether the project is set up."""
    report = Report()
    intent_text = read(INTENT)
    stage = stage_of(intent_text)
    set_up = bool(stage) and "[fill in" not in intent_text
    base, label = find_base(base_arg)
    files = project_files()

    report.lines.append(f"keel check | stage: {stage or 'not set'} | compared with {label}")
    check_libraries(report, files, base)
    if set_up:
        check_map(report, files)
    else:
        report.note(f"Setup isn't finished ({INTENT} has blanks), so the map wasn't checked. "
                    "Run /keel:start or follow the representative's setup steps.")
    if stage and stage.lower() == "explore":
        report.note("Stage is Explore: this code is throwaway. Don't build on it.")
    return report, set_up


def main() -> int:
    parser = argparse.ArgumentParser(description="keel drift check")
    parser.add_argument("--base", help="branch or commit to compare with (default: main)")
    parser.add_argument("--hook", action="store_true", help="Claude Code Stop hook mode")
    args = parser.parse_args()

    if args.hook:
        try:
            event = json.load(sys.stdin)
        except (json.JSONDecodeError, ValueError):
            event = {}
        if event.get("stop_hook_active"):
            return 0  # already sent back once; don't loop
        if git("status", "--porcelain") == "":
            return 0  # nothing changed, nothing to check

    report, set_up = run(args.base)
    total = "Result: all good." if not report.problems else \
        f"Result: {report.problems} thing{'s' if report.problems > 1 else ''} to fix."
    text = "\n".join(report.lines + [total])

    if args.hook:
        if report.problems and set_up:
            print(text + "\n\nFix these before finishing. If something is intentional, "
                  "record it (DECISIONS.md or the map) instead of hiding it.", file=sys.stderr)
            return 2
        return 0

    print(text)
    return 1 if report.problems else 0


if __name__ == "__main__":
    sys.exit(main())
