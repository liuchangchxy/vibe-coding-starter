#!/usr/bin/env python3
"""Universal smoke test for Vibe Coding Starter template.

Ensures the testing harness is fully operational right after cloning.
"""
import json
import unittest
from pathlib import Path


class TestSmoke(unittest.TestCase):
    """Smoke test to verify test harness and environment health."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent

    def test_environment_healthy(self):
        """Verify baseline test environment passes."""
        self.assertTrue(True, "Environment is operational.")

    def test_spec_exists(self):
        """Verify SPEC.md exists as the Single Source of Truth."""
        spec_file = self.root / "SPEC.md"
        self.assertTrue(spec_file.exists(), "SPEC.md must exist in project root.")

    def test_agents_rule_exists(self):
        """Verify AGENTS.md exists for AI agents."""
        agents_file = self.root / "AGENTS.md"
        self.assertTrue(agents_file.exists(), "AGENTS.md must exist in project root.")

    def test_checkpoint_script_exists(self):
        """Verify checkpoint manager script exists."""
        cp_file = self.root / "scripts" / "checkpoint.py"
        self.assertTrue(cp_file.exists(), "scripts/checkpoint.py must exist.")

    def test_devcontainer_valid(self):
        """Verify .devcontainer/devcontainer.json exists and is valid JSON."""
        dc_file = self.root / ".devcontainer" / "devcontainer.json"
        self.assertTrue(dc_file.exists(), ".devcontainer/devcontainer.json must exist.")
        data = json.loads(dc_file.read_text(encoding="utf-8"))
        self.assertIn("name", data)

    def test_specs_directory_exists(self):
        """Verify modular specs directory exists for scaling."""
        specs_dir = self.root / "specs"
        self.assertTrue(specs_dir.is_dir(), "specs/ directory must exist.")


if __name__ == "__main__":
    unittest.main()
