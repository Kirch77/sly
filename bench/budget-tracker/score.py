#!/usr/bin/env python3
"""Count the numbers for the sly vs plain Claude Code comparison.

  python3 score.py compare <sly-project> <plain-project>   side-by-side numbers
  python3 score.py blind <sly-project> <plain-project> <out>  anonymous copies for a blind review

Round counts need a commit per round whose message contains "round N".
"""
from __future__ import annotations

import json
import random
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

CODE = {".py", ".ts", ".js", ".tsx", ".jsx", ".rs", ".go"}
SKIP_DIRS = {".git", ".sly", "node_modules", "__pycache__", ".venv", "venv", "data", ".pytest_cache"}
SLY_FILES = {"AGENTS.md", "CLAUDE.md", "docs/INTENT.md", "docs/ARCHITECTURE.md", "docs/DECISIONS.md"}


def files(project: Path) -> list[Path]:
    return [p for p in project.rglob("*")
            if p.is_file() and not SKIP_DIRS.intersection(p.relative_to(project).parts)]


def is_test(path: Path) -> bool:
    name = path.name
    return any(part in {"tests", "test"} for part in path.parts) \
        or name.startswith("test_") or name.endswith(("_test.py", ".test.ts", ".spec.ts"))


def lines(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    return sum(1 for line in text.splitlines() if line.strip() and not line.strip().startswith("#"))


def libraries(project: Path) -> set[str]:
    found: set[str] = set()
    for path in files(project):
        if path.name == "pyproject.toml":
            data = tomllib.loads(path.read_text())
            specs = data.get("project", {}).get("dependencies", [])
            found |= {re.split(r"[\s<>=!~\[;]", s, maxsplit=1)[0].lower() for s in specs}
        elif path.name.startswith("requirements") and path.suffix == ".txt":
            for line in path.read_text().splitlines():
                line = line.split("#")[0].strip()
                if line and not line.startswith("-"):
                    found.add(re.split(r"[\s<>=!~\[;]", line, maxsplit=1)[0].lower())
        elif path.name == "package.json":
            data = json.loads(path.read_text())
            found |= set(data.get("dependencies", {})) | set(data.get("devDependencies", {}))
    return found


def round_changes(project: Path, n: int) -> str:
    log = subprocess.run(["git", "log", "--format=%H %s"], cwd=project,
                         capture_output=True, text=True).stdout
    commits = [line.split()[0] for line in log.splitlines()
               if re.search(rf"\bround[\s-]*{n}\b", line, re.I)]
    if not commits:
        return "no commit"
    out = subprocess.run(["git", "show", "--name-only", "--format=", commits[0]], cwd=project,
                         capture_output=True, text=True).stdout
    changed = [f for f in out.splitlines()
               if f and f not in SLY_FILES and not f.startswith(".sly/")]
    code = [f for f in changed if Path(f).suffix in CODE]
    return f"{len(code)} code / {len(changed)} total"


def stats(project: Path) -> dict[str, str]:
    code = [p for p in files(project) if p.suffix in CODE]
    source = [p for p in code if not is_test(p.relative_to(project))]
    tests = [p for p in code if is_test(p.relative_to(project))]
    libs = libraries(project)
    result = {
        "Lines of code (not tests)": str(sum(map(lines, source))),
        "Code files (not tests)": str(len(source)),
        "Lines of tests": str(sum(map(lines, tests))),
        "Outside libraries": f"{len(libs)} {sorted(libs) if libs else ''}".strip(),
    }
    for n in (2, 3, 4, 5):
        result[f"Files changed in round {n}"] = round_changes(project, n)
    return result


def compare(sly: Path, plain: Path) -> None:
    a, b = stats(sly), stats(plain)
    width = max(map(len, a)) + 2
    print(f"{'':{width}}{'sly':<24}plain")
    for key in a:
        print(f"{key:{width}}{a[key]:<24}{b[key]}")


def blind(sly: Path, plain: Path, out: Path) -> None:
    if out.exists():
        sys.exit(f"{out} already exists. Pick a new folder.")
    pair = [("sly", sly), ("plain", plain)]
    random.shuffle(pair)
    for letter, (_, src) in zip("AB", pair):
        def ignore(folder, names, src=src):
            rel = Path(folder).relative_to(src)
            return [n for n in names if n in SKIP_DIRS - {"data"} or (rel / n).as_posix() in SLY_FILES]
        shutil.copytree(src, out / letter, ignore=ignore)
        for folder in sorted((out / letter).rglob("*"), reverse=True):  # empty leftovers give it away
            if folder.is_dir() and not any(folder.iterdir()):
                folder.rmdir()
    key = out.with_name(out.name + "-ANSWER-KEY.txt")
    key.write_text("".join(f"{letter} = {name}\n" for letter, (name, _) in zip("AB", pair)))
    print(f"Copies are in {out}/A and {out}/B. The answer key is in {key} (don't open it yet).")


def main() -> None:
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == "compare":
        compare(Path(args[1]).resolve(), Path(args[2]).resolve())
    elif len(args) == 4 and args[0] == "blind":
        blind(Path(args[1]).resolve(), Path(args[2]).resolve(), Path(args[3]).resolve())
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
