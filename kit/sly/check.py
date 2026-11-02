#!/usr/bin/env python3
"""sly check: catches drift that is easy to miss.

It checks three things:
  1. Every new outside library is logged in docs/DECISIONS.md.
  2. Every code folder is on the map (docs/ARCHITECTURE.md).
  3. Every folder on the map still exists.

Only problems connected to the current changes (compared with the main branch) count as
"to fix". Older problems are shown as notes, so nobody is blocked by drift they didn't cause.
It does not run tests or linters; the project's own tools do that.

Usage:
  python3 .sly/check.py              compare with the main branch
  python3 .sly/check.py --base REF   compare with another branch or commit
  python3 .sly/check.py --all        treat older problems as "to fix" too (for checkups)
  python3 .sly/check.py --hook       Claude Code Stop hook mode (reads hook JSON on stdin)

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
# Folders that are never pieces, so they don't need to be on the map.
NOT_PIECES = {"docs", "tests", "test", "spec", "__tests__", "examples", "example",
              "fixtures", "benches", "coverage", "out", "public", "assets"}
# Skipped when walking a folder that isn't a git repository.
JUNK = {"node_modules", "target", "dist", "build", "venv", "__pycache__"}


# ---------- small helpers ----------

def git(*args: str) -> str | None:
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    except FileNotFoundError:
        return None
    return r.stdout if r.returncode == 0 else None


def is_git_repo() -> bool:
    return git("rev-parse", "--is-inside-work-tree") is not None


def read(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def normalize(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def project_files() -> list[str]:
    """Every file in the project (paths relative to it), minus what git ignores."""
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
    """The commit to compare with, and a label for it. None means 'no history to compare with'."""
    if explicit:
        sha = git("rev-parse", "--verify", explicit)
        if sha is None:
            sys.exit(f"sly check: can't find '{explicit}' in git.")
        return sha.strip(), explicit
    head = git("rev-parse", "--verify", "HEAD")
    if head is None:
        return None, "nothing (no commits yet)"
    for branch in ("origin/main", "main", "origin/master", "master"):
        if git("rev-parse", "--verify", "--quiet", branch) is not None:
            merge_base = (git("merge-base", "HEAD", branch) or "").strip()
            if merge_base == head.strip():
                return merge_base, f"{branch} (no new commits, so only uncommitted changes)"
            if merge_base:
                return merge_base, branch
    return head.strip(), "the last commit (only uncommitted changes)"


def changed_files(base: str | None) -> set[str] | None:
    """Files changed since base, including uncommitted and new ones. None means 'everything'."""
    if base is None or not is_git_repo():
        return None
    diff = git("diff", "--name-only", "--relative", base, "--", ".") or ""
    new = git("ls-files", "--others", "--exclude-standard") or ""
    return set(diff.splitlines()) | set(new.splitlines())


def touches(changed: set[str] | None, folder: str) -> bool:
    return changed is None or any(c == folder or c.startswith(folder + "/") for c in changed)


# ---------- reading dependency files ----------
# Each reader returns (outside libraries, the project's own package names).

PEP508_NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")
LOCAL_NPM = ("workspace:", "file:", "link:", "portal:")


def pep508(spec: str) -> set[str]:
    if not isinstance(spec, str) or "@ file:" in spec:
        return set()
    match = PEP508_NAME.match(spec)
    return {normalize(match.group(1))} if match else set()


def deps_package_json(text: str) -> tuple[set[str], set[str]]:
    data = json.loads(text)
    sections = ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies")
    found = {normalize(name) for s in sections for name, spec in data.get(s, {}).items()
             if not (isinstance(spec, str) and spec.startswith(LOCAL_NPM))}
    own = {normalize(data["name"])} if isinstance(data.get("name"), str) else set()
    return found, own


def deps_cargo(text: str) -> tuple[set[str], set[str]]:
    data = tomllib.loads(text)
    found: set[str] = set()

    def take(table: dict) -> None:
        for s in ("dependencies", "dev-dependencies", "build-dependencies"):
            for name, spec in table.get(s, {}).items():
                local = isinstance(spec, dict) and ("path" in spec or spec.get("workspace") is True)
                if not local:
                    found.add(normalize(spec.get("package", name) if isinstance(spec, dict) else name))

    take(data)
    take(data.get("workspace", {}))
    for target in data.get("target", {}).values():
        take(target)
    name = data.get("package", {}).get("name")
    return found, {normalize(name)} if isinstance(name, str) else set()


def deps_pyproject(text: str) -> tuple[set[str], set[str]]:
    data = tomllib.loads(text)
    found: set[str] = set()
    project = data.get("project", {})
    specs = list(project.get("dependencies", []))
    for group in project.get("optional-dependencies", {}).values():
        specs += group
    for group in data.get("dependency-groups", {}).values():
        specs += group
    for spec in specs:
        found |= pep508(spec)
    poetry = data.get("tool", {}).get("poetry", {})
    tables = [poetry.get("dependencies", {}), poetry.get("dev-dependencies", {})]
    tables += [g.get("dependencies", {}) for g in poetry.get("group", {}).values()]
    for table in tables:
        found.update(normalize(name) for name, spec in table.items()
                     if name != "python" and not (isinstance(spec, dict) and "path" in spec))
    own = {normalize(n) for n in (project.get("name"), poetry.get("name")) if isinstance(n, str)}
    return found, own


def deps_requirements(text: str) -> tuple[set[str], set[str]]:
    found: set[str] = set()
    for raw in text.splitlines():
        egg = re.search(r"#egg=([A-Za-z0-9._-]+)", raw)
        line = raw.split(" #")[0].split("#egg")[0].strip()
        if egg:
            found.add(normalize(egg.group(1)))
        elif line and not line.startswith(("-", "#", ".", "/")) and "://" not in line:
            found |= pep508(line)
    return found, set()


def deps_go_mod(text: str) -> tuple[set[str], set[str]]:
    found: set[str] = set()
    own: set[str] = set()
    in_block = False
    for raw in text.splitlines():
        line, _, comment = raw.partition("//")
        line = line.strip()
        indirect = comment.strip() == "indirect"
        if line.startswith("module "):
            own.add(normalize(line.split()[1]))
        elif line.startswith("require ("):
            in_block = True
        elif in_block and line == ")":
            in_block = False
        elif in_block and line and not indirect:
            found.add(normalize(line.split()[0]))
        elif line.startswith("require ") and not indirect:
            found.add(normalize(line.split()[1]))
    return found, own


READERS = {"package.json": deps_package_json, "Cargo.toml": deps_cargo,
           "pyproject.toml": deps_pyproject, "go.mod": deps_go_mod}


def reader_for(path: str):
    parts = path.split("/")
    if any(p.startswith(".") or p in NOT_PIECES or p in JUNK for p in parts[:-1]):
        return None  # test fixtures, examples, vendored copies
    name = parts[-1]
    if name.startswith("requirements") and name.endswith(".txt"):
        return deps_requirements
    return READERS.get(name)


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


def logged(name: str, entries: str) -> bool:
    pattern = r"(?<![\w@/.-])" + re.escape(name) + r"(?![\w/-])"
    return re.search(pattern, entries) is not None


def check_libraries(report: Report, files: list[str], base: str | None) -> None:
    now: dict[str, str] = {}   # library -> the file that lists it
    before: set[str] = set()
    own: set[str] = set()
    skipped: list[str] = []
    for path in files:
        reader = reader_for(path)
        if reader is None:
            continue
        if tomllib is None and path.endswith(".toml"):
            skipped.append(path)
            continue
        try:
            found, names = reader(read(path))
        except Exception as error:  # a broken file shouldn't stop the other checks
            report.note(f"Couldn't read {path} ({error}).")
            continue
        own |= names
        for name in found:
            now.setdefault(name, path)
        old = git("show", f"{base}:./{path}") if base else None
        if old:
            try:
                before |= reader(old)[0]
            except Exception:
                pass  # the old version was broken; treat everything as new
    if skipped:
        report.note(f"Couldn't check {', '.join(skipped)}: reading .toml files needs Python 3.11+.")

    # Only the entries count, not the explanation at the top of the file.
    entries = normalize("\n".join(line for line in read(DECISIONS).splitlines()
                                  if line.lstrip().startswith("- ")))
    new = sorted(set(now) - before - own)
    unlogged = [name for name in new if not logged(name, entries)]
    for name in unlogged:
        report.fix(f'New library "{name}" (in {now[name]}) isn\'t in {DECISIONS}.',
                   f"If it's worth it, log it there with the reason, writing the name exactly "
                   f"as shown (the representative decides). Or remove it.")
    if skipped:
        return
    if not new:
        report.ok("No new outside libraries.")
    elif not unlogged:
        report.ok(f"New libraries are all logged in {DECISIONS}: {', '.join(new)}.")


def code_folders(files: list[str]) -> set[str]:
    containers = set(CONTAINERS)
    if any(re.match(r"app/(page|layout)\.", f) for f in files):
        containers.discard("app")  # a Next.js route tree: app/ itself is the piece
    folders: set[str] = set()
    for path in files:
        parts = path.split("/")
        if len(parts) < 2 or parts[0].startswith(".") or parts[0] in NOT_PIECES:
            continue
        top = parts[0]
        if top in containers and len(parts) >= 3 and not parts[1].startswith(".") \
                and parts[1] not in NOT_PIECES:
            folders.add(f"{top}/{parts[1]}")
        else:
            folders.add(top)
    return folders


def map_body(map_text: str) -> str:
    """The part of the map that describes what exists: from the first section up to
    "Planned", without comments or code blocks."""
    text = re.sub(r"```.*?```", "", map_text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    parts = re.split(r"^##\s", text, maxsplit=1, flags=re.M)
    body = parts[1] if len(parts) > 1 else ""
    body = re.split(r"^##\s+Planned", body, maxsplit=1, flags=re.M | re.I)[0]
    return body.replace("`./", "`")


def on_map(folder: str, body: str) -> bool:
    return re.search(r"(?<![\w./-])" + re.escape(folder) + r"[/`]", body) is not None


def folder_refs(body: str) -> set[str]:
    """Folders the map names, like `src/parser/`. Skips anything that isn't a plain project path."""
    refs = set()
    for ref in re.findall(r"`([^`\s]+/)`", body):
        if ref.startswith(("/", "~", "$", "..")) or "://" in ref or any(c in ref for c in "{}<>[]*"):
            continue
        refs.add(ref)
    return refs


def check_map(report: Report, files: list[str], changed: set[str] | None, strict: bool) -> None:
    map_text = read(MAP)
    if not map_text:
        report.fix(f"There's no map at {MAP}.", "Create it (run setup) before building more.")
        return
    body = map_body(map_text)

    ignored = [item.strip().strip("`").strip().rstrip("/")
               for line in re.findall(r"^\s*<!--\s*sly-ignore:(.*?)(?:-->|$)", map_text, re.M)
               for item in line.split(",")]
    ignored = [i for i in ignored if i]

    def is_ignored(folder: str) -> bool:
        return any(folder == i or folder.startswith(i + "/") for i in ignored)

    older = 0
    missing = sorted(f for f in code_folders(files) if not is_ignored(f) and not on_map(f, body))
    for folder in missing:
        if strict or touches(changed, folder):
            report.fix(f"Folder {folder}/ isn't on the map.",
                       f"Add it to \"The pieces\" in {MAP}, or to sly-ignore if it isn't a piece.")
        else:
            older += 1

    map_changed = changed is None or MAP in changed
    stale = sorted(r for r in folder_refs(body) if not (ROOT / r).is_dir())
    for folder in stale:
        if strict or map_changed or touches(changed, folder.rstrip("/")):
            report.fix(f"The map mentions {folder} but that folder doesn't exist.",
                       f"Update {MAP} to match the code (or move it under \"Planned, not built yet\").")
        else:
            older += 1

    if older:
        report.note(f"{older} older map problem{'s' if older > 1 else ''} not caused by these "
                    "changes. Run with --all to see them, or use /sly:checkup.")
    elif not missing and not stale:
        report.ok("The map matches the folders in the project.")


def stage_of(intent_text: str) -> str | None:
    match = re.search(r"\*\*Stage:\*\*\s*(Explore|MVP|Production)\b", intent_text, re.I)
    return match.group(1) if match else None


def run(base_arg: str | None, strict: bool) -> tuple[Report, bool]:
    """Runs every check. Returns the report and whether the project is set up."""
    report = Report()
    intent_text = read(INTENT)
    stage = stage_of(intent_text)
    set_up = bool(stage) and "[fill in" not in intent_text
    base, label = find_base(base_arg) if is_git_repo() else (None, "nothing (not a git repository)")
    files = project_files()
    changed = changed_files(base)

    report.lines.append(f"sly check | stage: {stage or 'not set'} | compared with {label}")
    check_libraries(report, files, base)
    if set_up:
        check_map(report, files, changed, strict)
    else:
        report.note(f"Setup isn't finished ({INTENT} has blanks), so the map wasn't checked. "
                    "Run /sly:start or follow the representative's setup steps.")
    if stage and stage.lower() == "explore":
        report.note("Stage is Explore: this code is throwaway. Don't build on it.")
    return report, set_up


def main() -> int:
    parser = argparse.ArgumentParser(description="sly drift check")
    parser.add_argument("--base", help="branch or commit to compare with (default: main)")
    parser.add_argument("--all", action="store_true", help="count older problems too")
    parser.add_argument("--hook", action="store_true", help="Claude Code Stop hook mode")
    args = parser.parse_args()

    if args.hook:
        try:
            event = json.load(sys.stdin)
        except ValueError:
            event = {}
        if isinstance(event, dict) and event.get("stop_hook_active"):
            return 0  # already sent back once; don't loop
        if not is_git_repo():
            return 0  # without git there's no way to tell what this session changed
        if git("status", "--porcelain", "--", ".") == "":
            return 0  # nothing changed, nothing to check

    report, set_up = run(args.base, args.all)
    total = "Result: all good." if not report.problems else \
        f"Result: {report.problems} thing{'s' if report.problems > 1 else ''} to fix."
    text = "\n".join(report.lines + [total])

    if args.hook:
        if report.problems and set_up:
            print(text + "\n\nFix these before finishing. If something is intentional, record it "
                  "(DECISIONS.md or the map) instead of hiding it. If you're stopping to ask the "
                  "owner something first, say so and stop.", file=sys.stderr)
            return 2
        return 0

    print(text)
    return 1 if report.problems else 0


if __name__ == "__main__":
    sys.exit(main())
