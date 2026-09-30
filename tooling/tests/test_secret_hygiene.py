#!/usr/bin/env python3
"""Secret hygiene guard — a style-as-test source scanner (TESTING.md gate 5).

Scans tracked text files for credential-shaped literals so the "credentials never
enter the repository" rule (AGENTS.md lesson 19) is enforced by a gate rather than
by memory.

Design notes per gate 5's three requirements:
  * scans source TEXT, not runtime behaviour;
  * ships its own violating/compliant samples as an executable self-proof, so the
    guard proves it can go red before its repo-wide verdict is trusted;
  * exemptions go through an allowlist that must state WHY, and match on content
    signature rather than line number (line numbers drift).
"""
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Credential-shaped assignments: key = "long-ish literal"
CREDENTIAL_RE = re.compile(
    r"""(?ix)
    \b(?:password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|
         private[_-]?key|admin[_-]?password)\b
    \s*[:=]\s*
    ["']([^"']{6,})["']
    """
)

# Values that are obviously not real credentials. Matched by content signature
# (NOT line number), each with the reason it is exempt.
BENIGN_SIGNATURES = {
    "placeholder": ("placeholder", "example", "changeme", "your-", "xxxx", "<", "replace-with"),
    "env-var-read": ("os.environ", "process.env", "getenv", "SystemExit"),
}

# Files whose job is to be scanned as injection targets, not to hold real secrets.
SKIP_PATH_FRAGMENTS = ("/test_secret_hygiene.py",)


def is_benign(value: str) -> bool:
    low = value.lower()
    if any(sig in low for sig in BENIGN_SIGNATURES["placeholder"]):
        return True
    if value.startswith("$") or value.startswith("{"):
        return True
    return False


def tracked_text_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=str(ROOT), capture_output=True,
        encoding="utf-8", errors="replace", check=True,
    ).stdout
    files = []
    for name in out.split("\0"):
        if not name:
            continue
        p = ROOT / name
        if any(frag in "/" + name.replace("\\", "/") for frag in SKIP_PATH_FRAGMENTS):
            continue
        try:
            if p.is_file() and b"\x00" not in p.read_bytes()[:4096]:
                files.append(p)
        except OSError:
            continue
    return files


def scan(text: str) -> list[str]:
    """Return offending credential literals found in text."""
    found = []
    for m in CREDENTIAL_RE.finditer(text):
        value = m.group(1)
        if not is_benign(value):
            found.append(value)
    return found


class GuardSelfProof(unittest.TestCase):
    """Prove the scanner can go red and green before trusting its repo verdict."""

    def test_detects_a_real_credential(self):
        """VIOLATING sample: must be flagged (this is the guard's red proof)."""
        sample = 'ADMIN_PASSWORD = "hunter2secret"\n'
        self.assertTrue(scan(sample), "guard failed to flag an obvious credential")

    def test_accepts_placeholders_and_env_reads(self):
        """COMPLIANT samples: must not be flagged."""
        for sample in (
            'PASSWORD = "changeme-your-real-value-here"',
            'PASSWORD = os.environ.get("APP_PASSWORD")',
            'api_key: "xxxx-placeholder"',
            'token = "${APP_TOKEN}"',
        ):
            self.assertEqual(scan(sample), [], f"false positive on: {sample}")


class RepoIsClean(unittest.TestCase):
    def test_no_credential_literals_in_tracked_files(self):
        offenders = []
        for p in tracked_text_files():
            try:
                text = p.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for value in scan(text):
                offenders.append(f"{p.relative_to(ROOT)}: {value!r}")
        self.assertEqual(
            offenders, [],
            "credential-shaped literals found in tracked files:\n  "
            + "\n  ".join(offenders),
        )


if __name__ == "__main__":
    unittest.main()
