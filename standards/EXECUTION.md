# Multi-Agent Execution Loop (EXECUTION.md)

> **Scope**: this file fills in the **execution procedure** between intent and commit. Division of labor: `AGENTS.md` owns intent and red lines; `standards/TESTING.md` owns tests, gates, and the **Definition of Done**; this file owns **how work is decomposed, delivered, reviewed, and converged**.
> On conflict: red lines defer to AGENTS, stopping defers to the DoD, procedure defers to this file.

<p align="center"><a href="EXECUTION.md">English</a> · <a href="EXECUTION.zh-CN.md">简体中文</a></p>

---

## 0. Applicability switch (read first — this prevents over-engineering)

- **Scale dial**: a single-file tweak or one task needs only one review round; do not run the full loop. **Only a chained multi-task effort or a cross-file refactor** enables the process below.
- **Host adaptation**: hosts supporting sub-agents (Claude Code) use *dispatch mode* (separate implementer and reviewer roles). Single-agent hosts (Cursor, etc.) degrade to *self-checklist mode* — the same items, answered in sequence by one AI, with **no item skippable**.
- **One severity ladder**: every grade follows the **P0–P3** ladder from AGENTS/TESTING. If a tool or review emits Critical/Important/Minor, map it: `Critical→P0/P1 (veto)`, `Important→P1 (must clear)`, `Minor→P2/P3 (log it, never spiral)`.

---

## 1. The eight steps (for chained multi-task work)

| # | Action | Artifact (must land in a file, never only in chat) |
|---|--------|--------------------------------------------------|
| 1 | **Pre-flight seam scan**: before starting, scan the task × shared-file/interface matrix, mark each seam's producer → consumer, and rule on each one | written into the progress ledger |
| 2 | **Task brief**: write each task's requirement as its own brief file (exact values, interface signatures, acceptance criteria verbatim) | `task-N-brief.md` |
| 3 | **Implement**: the implementer reads only the brief; on finishing, writes a **report** (what was done, test evidence, deviations and concerns) | `task-N-report.md` |
| 4 | **Review packet**: produce a single file with `BASE..HEAD` commit list + stat + diff; the reviewer reads only the three (brief / report / diff) | `review-*.diff` |
| 5 | **Two-verdict review**: must output both ① spec conformance ✅/❌ and ② quality Approved / graded findings; **the reviewer re-runs the gates personally, never trusting the report** | review verdict |
| 6 | **Fix loop, ≤5 rounds**: rounds 1–3 wake the original implementer with the findings verbatim; rounds 4–5 hand to a stronger model / fresh agent; **each round is followed by a narrowed re-review**. If round 5 is still red, escalate for a per-item ruling (fix / reject-with-record / log as todo). Never loop forever | per-round record |
| 7 | **Stage final review**: adversarial review of the whole diff, plus an **a/b/c ruling on every deferred item** (a = must fix before merge, b = goes to the todo list, c = discarded) | final review report |
| 8 | **Rulings disclosure + delivery menu**: see §3; then offer Merge / Push / Keep for the user to decide | user confirmation |

**Never invent a stop condition**: at every stage, "can we stop?" is answered by the `standards/TESTING.md` DoD — **P0/P1 cleared, suite 100% with `skipped=0` → declare it passed, explicitly. Never spiral on P2/P3 theoretical risk.**

---

## 2. Carry-forward (review findings must not evaporate)

- A finding you did not fix this round → **write it into the progress ledger** (severity + one line) and **carry it verbatim into the dispatch prompt of the next related task**.
- A cross-stage finding → promote it to a todo line in the roadmap; the final review verifies at stage close that the original text is on file.
- Every "concern" and "deviation" in an implementer's report must be ruled on item by item by the reviewer (accept / escalate / reject). Never skip one silently.

---

## 3. Rulings disclosure (mandatory at stage close)

When the user authorizes an autonomous run ("do it all, stop only on failure"), the close-out must deliver a **rulings list**: every decision the AI made on the user's behalf this stage, one per line, in the format `ruling → cost of being wrong`.
- **Inclusion threshold**: only decisions that change **behavior, scope, or cost**. Pure implementation details are excluded.
- **Division of labor**: anything long-lived goes into `docs/DECISIONS.md` per AGENTS Engine 1.5 (the durable ledger). This list is the **user-facing stage summary**; neither replaces the other.
- **No silent rulings**: an undisclosed decision is a process violation.

---

## 4. Progress ledger × micro-snapshot (two complementary tracks)

- **Code snapshots**: before a big refactor, `python tooling/checks/checkpoint.py save "what I'm about to do"` (AGENTS Engine 1.4) — manages the **code state** and makes it rollback-able.
- **Progress ledger**: during a chained effort, maintain a `progress.md` (current task, completed lines, deferred items, rulings) — manages the **process state** so a long conversation doesn't forget and redo work. It is cleaned up at stage close once its load-bearing content has settled into DECISIONS/ROADMAP.
- They are not interchangeable: the ledger cannot roll back code, and the snapshot does not record review conclusions.

---

## 5. Incident entries (the format for DECISIONS, with a worked example)

Format: `symptom → root-cause chain (how many levels) → minimal fix → how it was verified → how recurrence is prevented`.

> **Example**: a CI release workflow "died on start, zero jobs" → root-cause chain: a secret held binary content → GitHub requires UTF-8 → the workflow failed validation the moment it referenced it → fix: re-set with `base64 < file | gh secret set` → verification: re-ran and all jobs appeared → prevention: the template README now states "secrets hold text only (base64); never binary".

**Optional recipe (only for projects with a version/state synchronized across several files)**: add a consistency grep to CI that goes red when the pubspec version and the documented version disagree — turning drift prevention from discipline into automation.

---

## 6. Anti-patterns (their presence is a violation)

| Anti-pattern | Correct approach |
|---|---|
| Silently making a scope-level decision for the user | Put it in the §3 rulings list |
| Reviewer reads the report but never re-runs the gates | The gates must be re-run by hand |
| Fix rounds continue past 5 | Escalate for a per-item ruling: fix / reject / log |
| Mixing two severity ladders | Use P0–P3; mapping in §0 |
| A finding marked "later" that never reaches the ledger | §2 carry-forward |
| Stage close reports only "all green", no rulings | §3, mandatory list |
| Writing a single measurement into a document as fact | Write a range or magnitude and note the variance (e.g. "about 400 colors, varying run to run"). Never turn one run's value into a constant |
