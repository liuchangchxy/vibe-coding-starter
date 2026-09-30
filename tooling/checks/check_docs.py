#!/usr/bin/env python3
"""check_docs.py - bilingual document and rule-index gate.

Three things are enforced, all of them physically rather than by discipline:

  1. Bilingual parity  - every Markdown document has a mirrored counterpart
                         (NAME.md <-> NAME.zh-CN.md), in both directions.
  2. Structure parity  - a mirrored pair has the same heading skeleton, so a
                         section deleted in one language cannot pass unnoticed.
  3. Rule index        - standards/RULES.md and standards/RULES.zh-CN.md carry
                         the same rule IDs, each pointing at the same home file,
                         and every home file exists.

Design follows the style-as-test triad in standards/TESTING.md 1.6:
  * it scans source TEXT, not runtime behaviour;
  * it ships its own violating and compliant samples and proves it can go red
    before its repo-wide verdict is trusted (run with --selftest, or every run);
  * exemptions go through an allowlist that must state WHY, matched by content
    signature rather than line number.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MID = ".zh-CN.md"

# Files that intentionally have no mirror. Each entry states WHY.
# Matched by path suffix (a content signature), never by line number.
NO_MIRROR: dict[str, str] = {
    ".agents/skills/sdd-implementation/SKILL.md": (
        "Frontmatter-driven agent skill read by the host tool; a translated copy "
        "would be dead weight, not a document anyone reads in two languages."
    ),
}

RULE_ROW = re.compile(r"^\|\s*([ATRCEL]-[0-9L]+)\s*\|(.+?)\|\s*`([^`]+)`\s*\|\s*([^|]*)\|")


def tracked_markdown() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-z", "*.md"],
        cwd=str(ROOT), capture_output=True, encoding="utf-8", errors="replace", check=True,
    ).stdout
    return [ROOT / n for n in out.split("\0") if n]


def heading_skeleton(path: Path) -> list[str]:
    """The sequence of heading levels, e.g. ['#','##','###','###','##'].

    Fenced code blocks are skipped: a leading '#' inside a fence is a shell
    comment, not a heading, and counting it makes the gate cry wolf.
    """
    skeleton = []
    in_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if re.match(r"^#{1,6} ", line):
            skeleton.append(line.split(" ")[0])
    return skeleton


def check_bilingual(files: list[Path]) -> list[str]:
    problems = []
    for f in files:
        try:
            rel = f.relative_to(ROOT).as_posix()
        except ValueError:      # self-proof samples live in a temp directory
            rel = f.name
        if rel in NO_MIRROR:
            continue
        if rel.endswith(MID):
            base = f.with_name(f.name[: -len(MID)] + ".md")
            if not base.exists():
                problems.append(f"{rel}: Chinese mirror has no English original ({base.name} missing)")
            continue
        # The rule index and the visual-smoke README are ordinary documents too.
        mirror = f.with_name(f.name[:-3] + MID)
        if not mirror.exists():
            problems.append(f"{rel}: no Chinese mirror ({mirror.name} missing)")
            continue
        en, zh = heading_skeleton(f), heading_skeleton(mirror)
        if len(en) != len(zh):
            problems.append(
                f"{rel}: heading count differs between languages "
                f"(en={len(en)}, zh={len(zh)}) - a section exists on only one side"
            )
        elif en != zh:
            problems.append(f"{rel}: heading level skeleton differs between languages")
    return problems


def parse_rule_index(path: Path) -> dict[str, str]:
    rules = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = RULE_ROW.match(line)
        if m:
            rules[m.group(1)] = m.group(3)
    return rules


def check_rule_index() -> list[str]:
    problems = []
    en_path = ROOT / "standards" / "RULES.md"
    zh_path = ROOT / "standards" / "RULES.zh-CN.md"
    for p in (en_path, zh_path):
        if not p.exists():
            return [f"rule index missing: {p.relative_to(ROOT)}"]
    en, zh = parse_rule_index(en_path), parse_rule_index(zh_path)
    if not en:
        return ["standards/RULES.md parsed to zero rules - the row format drifted"]
    for rid in sorted(set(en) - set(zh)):
        problems.append(f"rule {rid} exists in RULES.md but not in RULES.zh-CN.md")
    for rid in sorted(set(zh) - set(en)):
        problems.append(f"rule {rid} exists in RULES.zh-CN.md but not in RULES.md")
    for rid in sorted(set(en) & set(zh)):
        if en[rid] != zh[rid]:
            problems.append(f"rule {rid}: home differs between languages ({en[rid]} vs {zh[rid]})")
        if not (ROOT / en[rid]).exists():
            problems.append(f"rule {rid}: declared home does not exist -> {en[rid]}")
    return problems


# --------------------------------------------------------------------------
# Self-proof: the guard must demonstrably be able to go red.
# --------------------------------------------------------------------------

def _selftest() -> int:
    import tempfile

    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        # VIOLATING: an English doc with no Chinese mirror -> must be flagged.
        (d / "lonely.md").write_text("# Title\n\n## A\n", encoding="utf-8")
        got = check_bilingual([d / "lonely.md"])
        if not got:
            failures.append("failed to flag a document with no mirror")

        # VIOLATING: mirrors whose heading skeletons differ -> must be flagged.
        (d / "drift.md").write_text("# T\n\n## A\n\n## B\n", encoding="utf-8")
        (d / "drift.zh-CN.md").write_text("# T\n\n## A\n", encoding="utf-8")
        got = check_bilingual([d / "drift.md"])
        if not any("heading count differs" in p for p in got):
            failures.append("failed to flag a heading-count mismatch between mirrors")

        # COMPLIANT: a '#' inside a fenced block is a shell comment, not a heading.
        (d / "fence.md").write_text("# T\n\n```bash\n# a comment\n```\n\n## A\n", encoding="utf-8")
        (d / "fence.zh-CN.md").write_text("# T\n\n```bash\n# 注释\n```\n\n## A\n", encoding="utf-8")
        if check_bilingual([d / "fence.md"]):
            failures.append("false positive on a shell comment inside a fenced block")

        # COMPLIANT: matching pair -> must stay silent.
        (d / "ok.md").write_text("# T\n\n## A\n", encoding="utf-8")
        (d / "ok.zh-CN.md").write_text("# T\n\n## A\n", encoding="utf-8")
        if check_bilingual([d / "ok.md"]):
            failures.append("false positive on a matching pair")

        # COMPLIANT: allowlisted path -> must stay silent.
        if check_bilingual([ROOT / ".agents" / "skills" / "sdd-implementation" / "SKILL.md"]):
            failures.append("false positive on an allowlisted file")

    if failures:
        print("SELFTEST FAILED - this gate cannot be trusted:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        ok = _selftest()
        print("selftest: " + ("PASS" if ok == 0 else "FAIL"))
        return ok

    if _selftest() != 0:
        return 1

    files = tracked_markdown()
    problems = check_bilingual(files) + check_rule_index()

    if problems:
        print("Document gate failed:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print(
            "\nEvery Markdown document needs a mirrored pair with the same heading "
            "skeleton, and every rule needs one home in both rule indexes.",
            file=sys.stderr,
        )
        return 1

    rules = parse_rule_index(ROOT / "standards" / "RULES.md")
    print(f"OK: {len(files)} Markdown files mirror-checked, {len(rules)} rules indexed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
