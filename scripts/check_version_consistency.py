#!/usr/bin/env python3
"""Version drift guard: every hand-synced copy of the project version must
match the single source of truth.

Humans keep forgetting one of the N places that repeat the version (docs,
badges, protocol constants). This turns "remember to sync" into a gate:
one canonical source plus a list of markers, mismatch = red.

  python scripts/check_version_consistency.py
      --source pyproject.toml:'(?m)^version\\s*=\\s*"([^"]+)"'
      --check README.md:'version-([0-9.]+)-'
      --check docs/CHANGELOG.md:'(?m)^## \\[([^\\]]+)\\]'
      --tag v0.3.1            # additionally require the release tag to match
      --forbid '^1\\.'        # source must NOT match (e.g. pre-1.0 projects)
      --root DIR              # check another tree (fixtures, worktrees)
      --selftest              # prove the guard can actually fail

Rules for each --check pattern: exactly one (?P<version>...) group (or the
first capture group); the extracted value must equal the source version.
In CI, failures print GitHub ::error annotations when GITHUB_ACTIONS is set.

Deliberately NOT gated: anything that reads the version dynamically
(shields.io badges hitting the Releases API, `importlib.metadata`, etc.)
has no hand-synced literal -- only gate what humans copy by hand.

A gate that never went red is a ritual, not a gate: --selftest replays a
consistent tree (pass), a stale tree (fail naming every stale file), a
reworded marker (fail), a mismatched tag (fail) and a forbidden version
(fail) against temp fixtures.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

PASS_COUNT = 0
FAIL_COUNT = 0


def note_ok(label, value):
    global PASS_COUNT
    PASS_COUNT += 1
    print("  [ok]   %-22s %s" % (label, value))


def note_fail(path, message):
    global FAIL_COUNT
    FAIL_COUNT += 1
    if os.environ.get("GITHUB_ACTIONS"):
        print("::error file=%s::%s" % (path, message))
    print("  [FAIL] %-22s %s" % (path, message))


def split_spec(spec):
    """Split FILE:PATTERN on the first colon that leaves an existing file."""
    for i, ch in enumerate(spec):
        if ch == ":" and os.path.exists(spec[:i]):
            return spec[:i], spec[i + 1:]
    # Fall back: first colon (lets the caller get a clean "file not found").
    head, _, tail = spec.partition(":")
    return head, tail


def extract(path, pattern):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return None, "file not found"
    try:
        rx = re.compile(pattern)
    except re.error as e:
        return None, "bad pattern: %s" % e
    m = rx.search(text)
    if not m:
        return None, ("marker missing -- was the line reworded? "
                      "(expected /%s/)" % pattern)
    try:
        return m.group("version"), None
    except IndexError:
        pass
    if m.lastindex:
        return m.group(1), None
    return m.group(0), None


def run_checks(root, source_spec, checks, tag, forbids):
    global PASS_COUNT, FAIL_COUNT
    PASS_COUNT = FAIL_COUNT = 0
    src_file, src_pat = split_spec(source_spec)
    src_path = os.path.join(root, src_file)
    version, err = extract(src_path, src_pat)
    if err:
        note_fail(src_file, "source: %s" % err)
        return 1
    print("version guard - %s = %s" % (src_file, version))
    for spec in checks:
        path, pat = split_spec(spec)
        full = os.path.join(root, path)
        found, err = extract(full, pat)
        if err:
            note_fail(path, "%s" % err)
        elif found != version:
            note_fail(path, "'%s' != '%s' (%s)" % (found, version, src_file))
        else:
            note_ok(path, found)
    for pat in forbids:
        if re.search(pat, version):
            note_fail(src_file, "'%s' matches forbidden /%s/" % (version, pat))
        else:
            note_ok(src_file, "not matching /%s/" % pat)
    if tag:
        if tag == "v" + version:
            note_ok("release tag", tag)
        else:
            note_fail(src_file, "tag '%s' != 'v%s' -- release would ship "
                                "mislabelled artifacts" % (tag, version))
    if FAIL_COUNT:
        print("\nversion guard FAILED - %d issue(s), %d ok"
              % (FAIL_COUNT, PASS_COUNT))
        return 1
    print("\nversion guard passed - %d marker(s) match %s"
          % (PASS_COUNT, src_file))
    return 0


# ---------------------------------------------------------------- selftest


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _fixture(tmp):
    _write(os.path.join(tmp, "pyproject.toml"),
           '[project]\nname = "demo"\nversion = "0.3.1"\n')
    _write(os.path.join(tmp, "README.md"),
           "# Demo\n\n![v](https://img.shields.io/badge/version-0.3.1-blue)\n")
    _write(os.path.join(tmp, "docs.md"), "Current version: `0.3.1`\n")


def _guard(tmp, *extra):
    cmd = [sys.executable, os.path.abspath(__file__), "--root", tmp,
           "--source", 'pyproject.toml:(?m)^version\\s*=\\s*"([^"]+)"',
           "--check", "README.md:version-([0-9.]+)-",
           "--check", "docs.md:Current version: `([^`]+)`"] + list(extra)
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def selftest():
    passed = failed = 0

    def check(name, cond, out=""):
        nonlocal passed, failed
        if cond:
            passed += 1
            print("  [ok]   selftest: %s" % name)
        else:
            failed += 1
            print("  [FAIL] selftest: %s" % name)
            for line in out.splitlines():
                print("           | %s" % line)

    print("version guard selftest")
    tmp = tempfile.mkdtemp(prefix="verguard_st_")
    try:
        _fixture(tmp)
        rc, out = _guard(tmp)
        check("consistent tree passes", rc == 0, out)

        _fixture(tmp)  # source bumped, copies stale
        _write(os.path.join(tmp, "pyproject.toml"),
               '[project]\nname = "demo"\nversion = "0.4.0"\n')
        rc, out = _guard(tmp)
        check("stale copies fail", rc != 0, out)
        check("failure names README.md", "README.md" in out, out)
        check("failure names docs.md", "docs.md" in out, out)

        _fixture(tmp)  # marker reworded
        _write(os.path.join(tmp, "docs.md"), "Project version: `0.3.1`\n")
        rc, out = _guard(tmp)
        check("reworded marker fails", rc != 0 and "marker missing" in out,
              out)

        _fixture(tmp)  # tag gate
        rc, out = _guard(tmp, "--tag", "v0.3.1")
        check("matching tag passes", rc == 0, out)
        rc, out = _guard(tmp, "--tag", "v0.3.0")
        check("mismatched tag fails", rc != 0, out)

        _fixture(tmp)  # forbidden pattern
        rc, out = _guard(tmp, "--forbid", r"^1\.")
        check("allowed version passes forbid", rc == 0, out)
        _write(os.path.join(tmp, "pyproject.toml"),
               '[project]\nname = "demo"\nversion = "1.0.0"\n')
        _write(os.path.join(tmp, "README.md"),
               "# Demo\n\n![v](https://img.shields.io/badge/version-1.0.0-blue)\n")
        _write(os.path.join(tmp, "docs.md"), "Current version: `1.0.0`\n")
        rc, out = _guard(tmp, "--forbid", r"^1\.")
        check("forbidden version fails", rc != 0, out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(("\nPASS" if failed == 0 else "\nFAIL")
          + ": selftest %d passed, %d failed" % (passed, failed))
    return failed == 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Fail when hand-synced version copies drift from source.")
    ap.add_argument("--source", required=False,
                    help='FILE:PATTERN, e.g. pyproject.toml:...version..."')
    ap.add_argument("--check", action="append", default=[],
                    help="FILE:PATTERN to compare (repeatable)")
    ap.add_argument("--tag", default=None, help="require tag == v<source>")
    ap.add_argument("--forbid", action="append", default=[],
                    help="source must NOT match this regex (repeatable)")
    ap.add_argument("--root", default=".",
                    help="repository root to check (default: cwd)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return 0 if selftest() else 1
    if not args.source:
        ap.error("--source is required (or use --selftest)")
    return run_checks(args.root, args.source, args.check, args.tag,
                      args.forbid)


if __name__ == "__main__":
    sys.exit(main())
