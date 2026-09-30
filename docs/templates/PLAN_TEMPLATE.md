# [Plan name]

> Use this for cross-file, cross-module, or high-risk work. A single-file tweak does not need a Master Plan.

<p align="center"><a href="PLAN_TEMPLATE.md">English</a> · <a href="PLAN_TEMPLATE.zh-CN.md">简体中文</a></p>

## 1. Scope
- Goal:
- Corresponding SPEC item:
- Explicitly out of scope:
- Definition of done:

## 2. Current evidence
- Relevant source:
- Relevant tests:
- Current failure / gap:
- Existing working-tree changes:

## 3. Task breakdown
| Task | Input/output boundary | Depends on | Acceptance test | Status |
|---|---|---|---|---|
| T1 | | | | not started |

## 4. Execution discipline
1. Verify the paths, interfaces, and plan are still valid before starting.
2. For a behavior change, write the regression test first and confirm it is RED before implementing GREEN.
3. Never delete or weaken an existing test, and never edit an expected value to accommodate the implementation.
4. Take a checkpoint per `AGENTS.md` before cross-module or high-risk changes.
5. Every stage report states the real test results and the items not run. Never pass off a plan threshold as completion evidence.

## 5. Close-out
- [ ] Traceability matrix updated
- [ ] Test evidence recorded
- [ ] Unfinished items and rulings recorded
- [ ] This plan did not expand into unconfirmed new requirements
