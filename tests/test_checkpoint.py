#!/usr/bin/env python3
"""Regression tests for scripts/checkpoint.py.

These cover two defects that shipped in the template and were only found by
running restore against a real repository:

1. `restore` used `git checkout <sha> -- .`, which restores/overwrites paths
   that existed at the checkpoint but leaves files ADDED afterwards behind.
   Rollback therefore left orphan files in the worktree.
2. `restore` took a "safety" stash of the current worktree but never told the
   user the stash ref and never restored it, so uncommitted work silently
   vanished into an orphan stash.

Both tests build throwaway git repositories in a temp directory and drive the
script exactly as a user would.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "checkpoint.py"


class CheckpointRestoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="checkpoint-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self._git("init", "-q")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "Test")
        (self.tmp / "a.txt").write_text("v1\n", encoding="utf-8")
        self._git("add", "-A")
        self._git("commit", "-qm", "init")

    def _git(self, *args, check=True):
        return subprocess.run(
            ["git", *args],
            cwd=str(self.tmp),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=check,
        )

    def _checkpoint(self, *args, check=True):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=str(self.tmp),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=check,
        )

    def _files(self):
        return sorted(
            p.name for p in self.tmp.iterdir() if p.name not in (".git", "scripts")
        )

    def test_restore_removes_files_added_after_checkpoint(self):
        """Rollback must remove files created after the checkpoint, not orphan them."""
        self._checkpoint("save", "before refactor")

        (self.tmp / "a.txt").write_text("v2\n", encoding="utf-8")
        (self.tmp / "newmodule.py").write_text("added later\n", encoding="utf-8")
        self._git("add", "-A")
        self._git("commit", "-qm", "refactor: add newmodule")

        self._checkpoint("restore")

        self.assertNotIn(
            "newmodule.py",
            self._files(),
            "restore left an orphan file that did not exist at the checkpoint",
        )
        self.assertEqual((self.tmp / "a.txt").read_text(encoding="utf-8"), "v1\n")

    def test_restore_reports_recoverable_safety_stash(self):
        """Uncommitted work must stay recoverable and the stash ref must be printed."""
        self._checkpoint("save", "before refactor")

        (self.tmp / "precious.txt").write_text("PRECIOUS\n", encoding="utf-8")
        (self.tmp / "a.txt").write_text("v2\n", encoding="utf-8")

        result = self._checkpoint("restore")

        # The safety stash must be announced, otherwise it is undiscoverable.
        self.assertIn("git stash apply", result.stdout)

        stashes = self._git("stash", "list", "--format=%gd").stdout.split()
        self.assertTrue(stashes, "pre-restore worktree was not stashed at all")

        self._git("stash", "apply", stashes[0])
        self.assertEqual(
            (self.tmp / "precious.txt").read_text(encoding="utf-8"),
            "PRECIOUS\n",
            "uncommitted work was destroyed by restore",
        )


if __name__ == "__main__":
    unittest.main()
