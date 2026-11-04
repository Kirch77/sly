"""End-to-end tests: install sly into throwaway projects and run the check.

Run: python3 -m unittest discover tests
"""
import json
import re
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SLY = Path(__file__).resolve().parent.parent
INSTALL = SLY / "install.py"

INTENT = """# Intent
**Stage:** MVP
## What it is
A tiny calculator.
"""

MAP = """# Architecture
Rules mention `path/` here, before the first section, which the check ignores.
<!-- sly-ignore: vendor/ -->
## The pieces
| Piece | Folder |
|---|---|
| Parser | `src/parser/` |
## Planned, not built yet
- A cache in `src/cache/`.
"""


def sh(cwd, *cmd, stdin=None):
    return subprocess.run(cmd, cwd=cwd, input=stdin, capture_output=True, text=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class Project:
    """A throwaway git project with sly installed."""

    def __init__(self, commit=True):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        sh(self.root, "git", "init", "-q", "-b", "main")
        sh(self.root, "git", "config", "user.email", "t@t")
        sh(self.root, "git", "config", "user.name", "t")
        assert sh(self.root, sys.executable, str(INSTALL), ".").returncode == 0
        if commit:
            self.commit("install sly")

    def set_up(self):
        write(self.root / "docs/INTENT.md", INTENT)
        write(self.root / "docs/ARCHITECTURE.md", MAP)
        write(self.root / "src/parser/mod.rs", "// parser\n")
        write(self.root / "src/lib.rs", "// lib\n")
        self.commit("set up")

    def commit(self, message):
        sh(self.root, "git", "add", "-A")
        sh(self.root, "git", "commit", "-qm", message)

    def check(self, *args, stdin=None):
        return sh(self.root, sys.executable, ".sly/check.py", *args, stdin=stdin)

    def close(self):
        self._tmp.cleanup()


class InstallTests(unittest.TestCase):
    def test_fresh_install_without_commits(self):
        p = Project(commit=False)
        self.addCleanup(p.close)
        for rel in ["AGENTS.md", "CLAUDE.md", "docs/INTENT.md", "docs/ARCHITECTURE.md",
                    "docs/DECISIONS.md", ".sly/STANDARDS.md", ".sly/check.py",
                    ".sly/roles/representative.md", ".sly/roles/setup.md",
                    ".sly/roles/stages.md", ".sly/roles/checkup.md", ".sly/roles/rescue.md",
                    ".sly/VERSION", ".codex/agents/sly-implementer.toml",
                    ".codex/agents/sly-reviewer.toml"]:
            self.assertTrue((p.root / rel).is_file(), rel)
        self.assertEqual((p.root / "CLAUDE.md").read_text(), "@AGENTS.md\n")
        result = p.check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Setup isn't finished", result.stdout)

    def test_keeps_existing_files_and_updates_only_sly_parts(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        write(root / "AGENTS.md", "# My own rules\nUse tabs.\n")
        write(root / "CLAUDE.md", "# Claude notes\n")
        write(root / "docs/INTENT.md", "my intent")
        sh(root, sys.executable, str(INSTALL), ".")

        agents = (root / "AGENTS.md").read_text()
        self.assertTrue(agents.startswith("# My own rules\nUse tabs.\n"))
        self.assertIn("<!-- sly:start", agents)
        self.assertIn("@AGENTS.md", (root / "CLAUDE.md").read_text())
        self.assertEqual((root / "docs/INTENT.md").read_text(), "my intent")

        # Local edits to sly's files survive a plain re-install, and --update refreshes them.
        (root / ".sly/STANDARDS.md").write_text("old")
        write(root / "AGENTS.md", agents.replace("# How to work in this project", "# stale"))
        sh(root, sys.executable, str(INSTALL), ".")
        self.assertEqual((root / ".sly/STANDARDS.md").read_text(), "old")
        out = sh(root, sys.executable, str(INSTALL), ".", "--update").stdout
        self.assertIn("updated  .sly/STANDARDS.md", out)
        agents = (root / "AGENTS.md").read_text()
        self.assertIn("# How to work in this project", agents)
        self.assertTrue(agents.startswith("# My own rules"))
        self.assertEqual(agents.count("<!-- sly:start"), 1)
        self.assertEqual((root / "docs/INTENT.md").read_text(), "my intent")
        self.assertEqual((root / "CLAUDE.md").read_text().count("@AGENTS.md"), 1)


class MapTests(unittest.TestCase):
    def setUp(self):
        self.p = Project()
        self.addCleanup(self.p.close)
        self.p.set_up()

    def test_matching_map_passes(self):
        write(self.p.root / "vendor/thing/x.c", "")  # ignored via sly-ignore
        write(self.p.root / "tests/t.rs", "")         # tests don't need to be on the map
        result = self.p.check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("The map matches", result.stdout)

    def test_folder_missing_from_map(self):
        write(self.p.root / "src/eval/mod.rs", "")
        result = self.p.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("src/eval/ isn't on the map", result.stdout)

    def test_map_mentions_folder_that_is_gone(self):
        text = MAP.replace("| Parser | `src/parser/` |", "| Parser | `src/parser/` |\n| Old | `src/old/` |")
        write(self.p.root / "docs/ARCHITECTURE.md", text)
        result = self.p.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("mentions src/old/", result.stdout)
        self.assertNotIn("src/cache/", result.stdout)  # under Planned: fine
        self.assertNotIn("path/", result.stdout)       # before first section: fine


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.p = Project()
        self.addCleanup(self.p.close)
        self.p.set_up()
        write(self.p.root / "Cargo.toml", '[package]\nname="x"\n[dependencies]\nserde = "1"\n')
        self.p.commit("add serde")
        sh(self.p.root, "git", "checkout", "-qb", "feature")

    def test_new_library_must_be_logged(self):
        write(self.p.root / "Cargo.toml",
              '[package]\nname="x"\n[dependencies]\nserde = "1"\n[dev-dependencies]\nsome_lib = "2"\n')
        result = self.p.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn('New library "some-lib"', result.stdout)
        self.assertNotIn('"serde"', result.stdout)  # already on main

        with open(self.p.root / "docs/DECISIONS.md", "a") as f:
            f.write("- 2026-11-02: **Use some_lib for X.** Because Y.\n")
        result = self.p.check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_library_already_used_elsewhere_is_not_new(self):
        write(self.p.root / "crates/b/Cargo.toml", '[package]\nname="b"\n[dependencies]\nserde="1"\n')
        write(self.p.root / "docs/ARCHITECTURE.md", MAP.replace("## Planned", "| B | `crates/b/` |\n## Planned"))
        self.assertEqual(self.p.check().returncode, 0, self.p.check().stdout)

    def test_other_ecosystems(self):
        write(self.p.root / "package.json", json.dumps({"dependencies": {"left-pad": "1"}}))
        write(self.p.root / "requirements.txt", "# c\nRequests>=2\n-r other.txt\n")
        write(self.p.root / "pyproject.toml",
              '[project]\ndependencies = ["httpx[http2]>=0.27"]\n[dependency-groups]\ndev = ["pytest"]\n')
        write(self.p.root / "go.mod", "module m\nrequire (\n\tgithub.com/a/b v1\n)\nrequire c.io/d v2\n")
        out = self.p.check().stdout
        for name in ["left-pad", "requests", "httpx", "pytest", "github.com/a/b", "c.io/d"]:
            self.assertIn(f'"{name}"', out)


class HookTests(unittest.TestCase):
    def setUp(self):
        self.p = Project()
        self.addCleanup(self.p.close)

    def test_not_set_up_never_blocks(self):
        write(self.p.root / "src/x/a.rs", "")
        self.assertEqual(self.p.check("--hook", stdin="{}").returncode, 0)

    def test_blocks_on_problems_once(self):
        self.p.set_up()
        self.assertEqual(self.p.check("--hook", stdin="{}").returncode, 0)  # clean tree
        write(self.p.root / "src/eval/mod.rs", "")
        result = self.p.check("--hook", stdin="{}")
        self.assertEqual(result.returncode, 2)
        self.assertIn("src/eval/", result.stderr)
        again = self.p.check("--hook", stdin=json.dumps({"stop_hook_active": True}))
        self.assertEqual(again.returncode, 0)



class AuditRegressionTests(unittest.TestCase):
    """Bugs found in the audit. Each test is one bug that must stay fixed."""

    def setUp(self):
        self.p = Project()
        self.addCleanup(self.p.close)
        self.p.set_up()

    def log(self, line):
        with open(self.p.root / "docs/DECISIONS.md", "a") as f:
            f.write(line + "\n")

    def test_older_drift_is_a_note_not_a_block(self):
        write(self.p.root / "legacy/x.py", "")
        self.p.commit("old unmapped folder")
        write(self.p.root / "NOTES.txt", "unrelated edit")
        self.assertEqual(self.p.check("--hook", stdin="{}").returncode, 0)
        result = self.p.check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("1 older map problem", result.stdout)
        self.assertEqual(self.p.check("--all").returncode, 1)
        write(self.p.root / "legacy/y.py", "")  # touching it makes it this change's problem
        self.assertEqual(self.p.check().returncode, 1)

    def test_logging_needs_the_whole_name_in_an_entry(self):
        write(self.p.root / "package.json", json.dumps({"dependencies": {"log": "1", "react": "1"}}))
        self.log("- 2026-11-02 (representative): **Use `preact`.** Small.")
        out = self.p.check().stdout
        self.assertIn('"log"', out)    # "log" appears in the template text, but not in an entry
        self.assertIn('"react"', out)  # "preact" is not "react"

    def test_internal_packages_are_not_outside_libraries(self):
        write(self.p.root / "package.json", json.dumps({"name": "@acme/web", "dependencies": {
            "@acme/core": "workspace:*", "@acme/ui": "file:../ui"}}))
        write(self.p.root / "Cargo.toml", '[package]\nname="app"\n[dependencies]\n'
              'util = { path = "../util" }\nshared = { workspace = true }\n')
        write(self.p.root / "pyproject.toml", '[project]\nname="myproj"\ndependencies=["myproj[x]"]\n')
        write(self.p.root / "requirements.txt", "git+https://github.com/a/b.git\nfoo @ file:///x\n")
        write(self.p.root / "go.mod", "module m\nrequire (\n\tgithub.com/x/dep v1 // indirect\n)\n")
        write(self.p.root / "tests/fixtures/p/package.json", json.dumps({"dependencies": {"zzz": "1"}}))
        result = self.p.check()
        self.assertIn("No new outside libraries", result.stdout)

    def test_sly_ignore_in_template_format(self):
        text = MAP.replace("<!-- sly-ignore: vendor/ -->", "<!-- sly-ignore: vendor/, gen/ -->")
        write(self.p.root / "docs/ARCHITECTURE.md", text)
        write(self.p.root / "gen/out.rs", "")
        result = self.p.check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_map_ignores_paths_that_are_not_project_folders(self):
        text = MAP.replace("## Planned", "Config lives in `~/.config/app/`, docs at "
                           "`https://x.io/docs/`, shared code in `../shared/`, or `/usr/`.\n"
                           "```\n`src/fake/`\n```\n| Lib | `./src/parser/` |\n## Planned")
        write(self.p.root / "docs/ARCHITECTURE.md", text)
        result = self.p.check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_project_in_a_subfolder_of_a_repo(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = Path(tmp.name)
        sh(repo, "git", "init", "-q", "-b", "main")
        sh(repo, "git", "config", "user.email", "t@t")
        sh(repo, "git", "config", "user.name", "t")
        proj = repo / "proj"
        proj.mkdir()
        sh(proj, sys.executable, str(INSTALL), ".")
        write(proj / "package.json", json.dumps({"dependencies": {"lodash": "1"}}))
        sh(repo, "git", "add", "-A")
        sh(repo, "git", "commit", "-qm", "init")
        sh(repo, "git", "checkout", "-qb", "feat")
        write(repo / "elsewhere.txt", "outside the project")
        result = sh(repo, sys.executable, "proj/.sly/check.py")
        self.assertIn("No new outside libraries", result.stdout)
        hook = sh(repo, sys.executable, "proj/.sly/check.py", "--hook", stdin="{}")
        self.assertEqual(hook.returncode, 0)

    def test_hook_handles_odd_input(self):
        write(self.p.root / "src/eval/mod.rs", "")
        for stdin in ["[]", "null", '"x"', ""]:
            self.assertEqual(self.p.check("--hook", stdin=stdin).returncode, 2, stdin)

    def test_nextjs_app_folder_is_one_piece(self):
        write(self.p.root / "app/page.tsx", "")
        write(self.p.root / "app/dashboard/page.tsx", "")
        write(self.p.root / "docs/ARCHITECTURE.md", MAP.replace("## Planned", "| Web | `app/` |\n## Planned"))
        result = self.p.check()
        self.assertEqual(result.returncode, 0, result.stdout)


class InstallerRegressionTests(unittest.TestCase):
    def test_broken_markers_are_left_alone(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        original = "<!-- sly:start\nUSER NOTES\n"
        write(root / "AGENTS.md", original)
        out = sh(root, sys.executable, str(INSTALL), ".").stdout
        self.assertIn("SKIPPED  AGENTS.md", out)
        self.assertEqual((root / "AGENTS.md").read_text(), original)

    def test_existing_import_forms_are_recognized(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        write(root / "CLAUDE.md", "Read @./AGENTS.md first.\n")
        sh(root, sys.executable, str(INSTALL), ".")
        self.assertEqual((root / "CLAUDE.md").read_text(), "Read @./AGENTS.md first.\n")

    def test_refuses_to_install_inside_sly(self):
        result = sh(SLY, sys.executable, str(INSTALL), str(SLY / "kit" / "sly"))
        self.assertEqual(result.returncode, 1)
        self.assertFalse((SLY / "kit" / "sly" / ".sly").exists())


class AutoRefreshTests(unittest.TestCase):
    """The plugin runs `install.py --auto` when a session starts."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def auto(self):
        return sh(self.root, sys.executable, str(INSTALL), str(self.root), "--auto")

    def test_ignores_projects_without_sly(self):
        result = self.auto()
        self.assertEqual((result.returncode, result.stdout), (0, ""))
        self.assertEqual(list(self.root.iterdir()), [])

    def test_refreshes_older_projects_without_touching_owner_files(self):
        sh(self.root, sys.executable, str(INSTALL), ".")
        (self.root / ".sly/VERSION").write_text("0.0.1\n")
        (self.root / ".sly/STANDARDS.md").write_text("old")
        (self.root / ".sly/roles/reviewer.md").unlink()       # a file new in this version
        (self.root / "docs/DECISIONS.md").unlink()            # owner deleted it on purpose
        (self.root / "CLAUDE.md").write_text("# mine\n")      # owner removed the import
        result = self.auto()
        self.assertIn("refreshed this project's sly files from 0.0.1", result.stdout)
        self.assertNotEqual((self.root / ".sly/STANDARDS.md").read_text(), "old")
        self.assertTrue((self.root / ".sly/roles/reviewer.md").exists())
        self.assertFalse((self.root / "docs/DECISIONS.md").exists())
        self.assertEqual((self.root / "CLAUDE.md").read_text(), "# mine\n")
        self.assertEqual(self.auto().stdout, "")  # now current: nothing to do

    def test_never_downgrades(self):
        sh(self.root, sys.executable, str(INSTALL), ".")
        (self.root / ".sly/VERSION").write_text("99.0.0\n")
        (self.root / ".sly/STANDARDS.md").write_text("from a newer sly")
        self.assertEqual(self.auto().stdout, "")
        self.assertEqual((self.root / ".sly/STANDARDS.md").read_text(), "from a newer sly")

    def test_hook_command_runs_from_the_plugin(self):
        sh(self.root, sys.executable, str(INSTALL), ".")
        (self.root / ".sly/VERSION").write_text("0.0.1\n")
        (self.root / ".sly/STANDARDS.md").write_text("old")
        hooks = json.loads((SLY / "hooks/hooks.json").read_text())
        command = hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(self.root), CLAUDE_PLUGIN_ROOT=str(SLY))
        result = subprocess.run(["sh", "-c", command], env=env, cwd=tempfile.gettempdir(),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("refreshed", result.stdout)


class LongFileTests(unittest.TestCase):
    def setUp(self):
        self.p = Project()
        self.addCleanup(self.p.close)
        self.p.set_up()

    def test_notes_long_files_this_change_touched_without_failing(self):
        write(self.p.root / "src/parser/old.rs", "x\n" * 500)
        self.p.commit("an old long file")
        write(self.p.root / "src/parser/new.rs", "x\n" * 450)
        write(self.p.root / "tests/test_big.rs", "x\n" * 900)  # tests don't count
        result = self.p.check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("src/parser/new.rs (450 lines)", result.stdout)
        self.assertNotIn("old.rs", result.stdout)
        self.assertNotIn("test_big", result.stdout)
        self.assertIn("old.rs (500 lines)", self.p.check("--all").stdout)


class CleanupProgressTests(unittest.TestCase):
    def test_shows_how_far_a_cleanup_has_got(self):
        p = Project()
        self.addCleanup(p.close)
        p.set_up()
        self.assertNotIn("Cleanup in progress", p.check().stdout)
        write(p.root / "docs/CLEANUP.md", "# Cleanup plan\n## Phases\n- [x] Tests for import\n"
              "- [X] Delete old report code\n- [ ] Merge the two date parsers\n")
        result = p.check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Cleanup in progress: 2 of 3 steps done", result.stdout)


class CodexPluginTests(unittest.TestCase):
    """Codex can't be run here, so these check the files Codex reads."""

    def test_manifests_agree(self):
        claude = json.loads((SLY / ".claude-plugin/plugin.json").read_text())
        codex = json.loads((SLY / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(claude["version"], codex["version"])
        self.assertEqual(codex["name"], "sly")
        self.assertTrue((SLY / codex["skills"]).is_dir())
        market = json.loads((SLY / ".agents/plugins/marketplace.json").read_text())
        self.assertEqual(market["plugins"][0]["source"]["path"], "./")

    def test_skills_are_well_formed_and_point_at_real_files(self):
        import tomllib
        skills = sorted((SLY / "codex/skills").glob("*/SKILL.md"))
        self.assertEqual([s.parent.name for s in skills],
                         ["sly-build", "sly-checkup", "sly-harden", "sly-start"])
        for skill in skills:
            text = skill.read_text()
            front = text.split("---")[1]
            self.assertIn(f"name: {skill.parent.name}", front)
            self.assertIn("description: ", front)
            for ref in re.findall(r"`\.sly/roles/([a-z]+\.md)`", text):
                self.assertTrue((SLY / "kit/sly/roles" / ref).is_file(), ref)
        for agent in (SLY / "kit/codex-agents").glob("*.toml"):
            data = tomllib.loads(agent.read_text())
            self.assertEqual(data["name"], agent.stem)
            self.assertTrue(data["description"] and data["developer_instructions"])

    def test_hooks_work_without_claude_project_dir(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        sh(root, sys.executable, str(INSTALL), ".")
        (root / ".sly/VERSION").write_text("0.0.1\n")
        (root / ".sly/STANDARDS.md").write_text("old")
        hooks = json.loads((SLY / "hooks/hooks.json").read_text())
        command = hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        env["CLAUDE_PLUGIN_ROOT"] = str(SLY)  # Codex sets this for compatibility
        result = subprocess.run(["sh", "-c", command], cwd=root, env=env,
                                capture_output=True, text=True)
        self.assertIn("refreshed", result.stdout, result.stderr)

if __name__ == "__main__":
    unittest.main()
