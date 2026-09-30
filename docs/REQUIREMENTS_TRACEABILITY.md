# Requirement Traceability Matrix

This file records **whether a requirement actually landed**. It does not replace `SPEC.md`. `SPEC.md` holds only confirmed product rules; this matrix holds implementation status, code evidence, and real run evidence.

<p align="center"><a href="REQUIREMENTS_TRACEABILITY.md">English</a> · <a href="REQUIREMENTS_TRACEABILITY.zh-CN.md">简体中文</a></p>

## Rules of use

- Give every significant requirement a stable ID, e.g. `REQ-001`.
- Status may only be: `not started`, `in progress`, `partial`, `verified`, `closed`.
- "Verified" requires a command that was actually run and its result. Plans, static reading, and an agent's self-report are not evidence.
- `skipped`, not-run, and environment-limited items must be stated as they are. Never write them up as green.
- Do not put diagnoses, candidate designs, or future ideas here. The user confirms those into `SPEC.md` first.

## Matrix

| ID | SPEC section / requirement | Source location | Test location and command | Result (pass/fail/skipped) | Status | Uncovered boundary / notes |
|---|---|---|---|---|---|---|
| REQ-001 | `SPEC.md` §[section] | `[path]:[symbol]` | `[path]`; `[command]` | `[result]` | not started | |

## Minimum stage-report format

```text
Requirement batch: [name]
Touched this round: [REQ-xxx]
Source evidence: [files and symbols]
Test command and result: [command; pass/fail/skipped]
Real link: [highest layer actually executed; reason if not run]
Current status: [not started / in progress / partial / verified / closed]
Remaining gaps: [list]
```
