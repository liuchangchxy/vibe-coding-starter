# Wizard and Multi-Step Flow Extension

Enable only for wizards, multi-step forms, guided troubleshooting, surveys, or other step-wise flows.

<p align="center"><a href="STEPPER_WORKFLOWS.md">English</a> · <a href="STEPPER_WORKFLOWS.zh-CN.md">简体中文</a></p>

## 1. Forward navigation must not block
- Except for a hard data prerequisite (the previous step generates the only valid input for the next), "skip / next / jump via the stepper" must never deadlock on an incomplete step.
- An unfilled or failing step is only a **status marker** (warning color, incomplete badge). The user keeps the freedom to browse, skip, and come back.

## 2. Two-track state (draft vs. commit)
- **Transient edit view**: for the current step's interaction only; never the sole source of truth.
- **Session snapshot bus**: keep a map keyed by step/node ID in session memory (e.g. `sessionDrafts[stepId]`).
- **Decouple switching from resetting**:
  - Before leaving a node, atomically stash the current step's transient state (checks, text, expansion, verdicts);
  - On entering a target node, idempotently rehydrate that node's prior answers and verdicts;
  - Never perform a global data wipe inside a step-change listener (e.g. `watch(currentStep)`).

## 3. Validation converges on the final action
- Intermediate states may be incomplete; the user may leave mid-way with the draft preserved.
- Strong completeness validation and guard rails concentrate at the terminal action ("submit", "hand in", "settle", "confirm"). On trigger, aggregate the outstanding items, tell the user, and ask for one explicit confirmation — never block point by point during the flow.
