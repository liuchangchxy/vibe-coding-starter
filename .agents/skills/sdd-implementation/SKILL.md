---
name: sdd-implementation
description: Execute a confirmed, scoped implementation plan with evidence-first SDD and regression discipline.
---

# SDD Implementation

Use this skill only after the user has confirmed the scope or named an existing implementation plan. It is intentionally framework-neutral.

## Standard cadence

1. Read `AGENTS.md`, `SPEC.md`, `TESTING.md`, the traceability matrix, and the named plan.
2. Inspect `git status` and the current diff. Preserve unrelated work.
3. Verify the plan's paths, symbols, interfaces, and test commands still exist.
4. For a behavior change, add a focused regression test and run it RED before implementation.
5. Make the smallest implementation change that turns the test GREEN; do not weaken old assertions.
6. Scan for the same pattern elsewhere when fixing a defect.
7. Run the project's applicable test layers and record pass/fail/skipped/未运行 separately.
8. Update the traceability matrix and decision log only when the evidence or confirmed decision changed.

## Complexity switch

Do not create a Master Plan, dispatch Agents, run browser E2E, or perform OSS/data-safety audits unless the task actually triggers those concerns. For high-risk or cross-module changes, use `EXECUTION.md` and the applicable `docs/optional/` extension.

## Stop condition

Report only what the executed evidence proves. Keep unresolved P0/P1 issues visible; record P2/P3 items without using them to invent scope.
