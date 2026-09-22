#!/usr/bin/env python3
"""Universal smoke test for Vibe Coding Starter template.

Ensures the testing harness is fully operational right after cloning.
"""
import unittest


class TestSmoke(unittest.TestCase):
    """Smoke test to verify test harness and environment health."""

    def test_environment_healthy(self):
        """Verify baseline test environment passes."""
        self.assertTrue(True, "Environment is operational.")

    def test_spec_exists(self):
        """Verify SPEC.md exists as the Single Source of Truth."""
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent
        spec_file = root / "SPEC.md"
        self.assertTrue(spec_file.exists(), "SPEC.md must exist in project root.")

    def test_agents_rule_exists(self):
        """Verify AGENTS.md exists for AI agents."""
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent
        agents_file = root / "AGENTS.md"
        self.assertTrue(agents_file.exists(), "AGENTS.md must exist in project root.")


if __name__ == "__main__":
    unittest.main()
