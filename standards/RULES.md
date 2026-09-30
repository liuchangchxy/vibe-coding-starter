# Master Rule Index (RULES.md)

> **What this is**: one row per rule, one stable ID per rule, and **exactly one home file** where that rule is defined. Everything else that needs the rule links to it — nothing restates it.
>
> **How to read it**: this is a **lookup table** — for navigation, review, and reorganization. It is *not* required reading at the start of a session. `AGENTS.md` and `SPEC.md` are what a session reads first.
>
> **Why it exists**: a rule written in three places drifts into three different rules. This index is the anti-drift contract, and it is the safety net for any reorganization: `tooling/checks/check_docs.py` fails CI when a rule's declared home no longer contains it. **You cannot lose a rule without the build going red.**

<p align="center"><a href="RULES.md">English</a> · <a href="RULES.zh-CN.md">简体中文</a></p>

---

## 1. Single-source-of-truth map

Read this before editing any rule. If a rule lives here, **edit it here and nowhere else**.

| Rule domain | The one home | Everywhere else |
|---|---|---|
| AI conduct, engines, lessons | `AGENTS.md` | link only |
| Severity ladder P0–P3 | `standards/TESTING.md` §3 | `AGENTS.md`, `standards/EXECUTION.md` link |
| Definition of Done | `standards/TESTING.md` §3 | link only |
| Test gates, layers, evidence | `standards/TESTING.md` §1–§2 | link only |
| Review attack recipes | `standards/REVIEWING.md` | link only |
| Execution loop, rulings | `standards/EXECUTION.md` | link only |
| Architecture method | `standards/ARCHITECTURE.md` | link only |
| Localization and theming | `standards/LOCALIZATION.md` | `SPEC.md` §7 summarizes and links |
| Product rules | `SPEC.md` | link only |
| Decisions and their reasons | `docs/DECISIONS.md` | link only |
| Requirement ↔ evidence status | `docs/REQUIREMENTS_TRACEABILITY.md` | link only |
| Technical pitfalls in this codebase | `docs/CONSTRAINTS.md` | link only |
| Resume entry / outstanding work | `docs/START_HERE.md` | link only |

**The invariant**: `SPEC.md` says *what to build*, `standards/` says *how to build it*, `docs/` records *what happened*. A rule appears in exactly one of those three.

---

## 2. Universal rules

**Enforced by** column: a script name means a physical gate; `discipline` means a process rule with no automatable check yet.

### A — AI conduct (`AGENTS.md`)

| ID | Rule | Home | Enforced by |
|---|---|---|---|
| A-01 | SPEC is the single source of truth for any business change | `AGENTS.md` | discipline |
| A-02 | Non-destructive operations; never delete or overwrite without explicit permission | `AGENTS.md` | discipline |
| A-03 | Anti-test-tampering; never fake a green suite | `AGENTS.md` | `guard_test_tampering.py` |
| A-04 | No hardcoded absolute paths | `AGENTS.md` | `scan_hardcoded_paths.py` |
| A-05 | Localization and theming are first-class dimensions | `AGENTS.md` | `check_docs.py` |
| A-06 | Standard open-source deliverables (SPONSOR, FAQ) | `AGENTS.md` | `test_smoke.py` |
| A-07 | Delivery must be green | `AGENTS.md` | `discipline` |
| A-08 | Mandatory end-to-end verification; never report `skipped` as passing | `AGENTS.md` | discipline |
| A-09 | Auto-persist spoken intent into SPEC before touching code | `AGENTS.md` | discipline |
| A-10 | Mandatory baseline injection into every new project | `AGENTS.md` | `init_project.py` |
| A-11 | Disambiguation gate: 2–3 options before coding an ambiguous request | `AGENTS.md` | discipline |
| A-12 | Micro-checkpoint before high-risk changes | `AGENTS.md` | `checkpoint.py` |
| A-13 | Decision trail into DECISIONS.md | `AGENTS.md` | discipline |
| A-14 | 1-to-4 root-cause divergence protocol | `AGENTS.md` | discipline |
| A-15 | Severity ladder P0–P3 | `AGENTS.md` | discipline |
| A-16 | Convergent DoD with a rulings list; no silent rulings | `AGENTS.md` | discipline |
| A-17 | Self-learning lessons list | `AGENTS.md` | discipline |
| A-18 | Complexity switch: no heavy process for small tasks | `AGENTS.md` | discipline |
| A-19 | SPEC existence ≠ implementation; record evidence separately | `AGENTS.md` | discipline |
| A-20 | Test layers must not impersonate one another | `AGENTS.md` | discipline |
| A-21 | Vague UI feedback becomes a five-dimension change/don't-change ballot | `AGENTS.md` | discipline |
| A-22 | Research on a frozen requirement is exploration; findings stay out of SPEC | `AGENTS.md` | discipline |
| A-23 | Route corrections: technical pitfalls to CONSTRAINTS.md, behaviour to AGENTS.md | `AGENTS.md` | `check_docs.py` |
| A-24 | A new session reads the resume entry point first | `AGENTS.md` | `check_docs.py` |

### A-L — Lessons learned (`AGENTS.md` lessons list)

| ID | Lesson | Home | Enforced by |
|---|---|---|---|
| A-L01 | Never change a requirement by editing code alone | `AGENTS.md` | discipline |
| A-L02 | Suite must be fully green before delivery | `AGENTS.md` | discipline |
| A-L03 | Never commit with `--no-verify` | `AGENTS.md` | `setup-hooks.py` |
| A-L04 | Never run mock tests alone; run the real link | `AGENTS.md` | discipline |
| A-L05 | Never count `skipped` as passing | `AGENTS.md` | discipline |
| A-L06 | `subprocess.run(text=True)` must declare UTF-8 | `AGENTS.md` | discipline |
| A-L07 | Never edit an old test's expected value to fake green | `AGENTS.md` | `guard_test_tampering.py` |
| A-L08 | Never fix a bug by editing one isolated line | `AGENTS.md` | discipline |
| A-L09 | Pragmatic research; no star-count dogma | `AGENTS.md` | discipline |
| A-L10 | Stay on the named target during OSS evaluation | `AGENTS.md` | discipline |
| A-L11 | Never spiral on local detail over the global product goal | `AGENTS.md` | discipline |
| A-L12 | No premature or polluted SPEC | `AGENTS.md` | discipline |
| A-L13 | Separate evidence states | `AGENTS.md` | discipline |
| A-L14 | Real-link layering | `AGENTS.md` | discipline |
| A-L15 | Complexity stop-loss | `AGENTS.md` | discipline |
| A-L16 | SPA entry must be served no-cache | `AGENTS.md` | discipline |
| A-L17 | Steppers must not block navigation | `AGENTS.md` | discipline |
| A-L18 | Constrained-viewport physical budget (top bar ≤ 44px) | `AGENTS.md` | discipline |
| A-L19 | Zero credentials in the repo | `AGENTS.md` | `test_secret_hygiene.py` |
| A-L20 | Pre-push redaction census | `AGENTS.md` | `test_secret_hygiene.py` |
| A-L21 | History is public; rewrite it on exposure | `AGENTS.md` | discipline |
| A-L22 | 1-to-4 protocol on every bug report | `AGENTS.md` | discipline |
| A-L23 | Zero tolerance for absolute paths | `AGENTS.md` | `scan_hardcoded_paths.py` |
| A-L24 | Universal localization gate | `AGENTS.md` | `check_docs.py` |
| A-L25 | Standard open-source deliverables | `AGENTS.md` | `test_smoke.py` |

### T — Testing gates (`standards/TESTING.md`)

| ID | Rule | Home | Enforced by |
|---|---|---|---|
| T-01 | Defect-driven testing: failing test before implementation | `standards/TESTING.md` | discipline |
| T-02 | Anti-test-tampering physical gate | `standards/TESTING.md` | `guard_test_tampering.py` |
| T-03 | No-hardcoded-absolute-paths gate | `standards/TESTING.md` | `scan_hardcoded_paths.py` |
| T-04 | Contract defense; no silent tolerance | `standards/TESTING.md` | discipline |
| T-05 | 1-to-4 divergence, with a census before touching anything | `standards/TESTING.md` | discipline |
| T-06 | Style-as-test: self-scanning source guards (the triad) | `standards/TESTING.md` | `check_docs.py` |
| T-07 | Gate-as-evidence: every new gate ships a red proof | `standards/TESTING.md` | discipline |
| T-08 | Test layers and evidence reporting | `standards/TESTING.md` | `TEST_EVIDENCE_TEMPLATE.md` |
| T-09 | Secret hygiene gate | `standards/TESTING.md` | `test_secret_hygiene.py` |
| T-10 | Two-layer physical gate; release gate mirrors CI gate | `standards/TESTING.md` | `ci.yml` |
| T-11 | Dictionary parity and no-hardcoded-copy gate (gated) | `standards/TESTING.md` | `check_docs.py` |
| T-12 | Theme and constrained-viewport gate (gated) | `standards/TESTING.md` | discipline |
| T-13 | Async and flaky failure triage (opt-in) | `standards/TESTING.md` | discipline |
| T-14 | Definition of Done: P0/P1 cleared, suite 100%, `skipped=0` | `standards/TESTING.md` | discipline |
| T-15 | Orthogonal verification: the means of verifying is independent of the means of doing | `standards/TESTING.md` | discipline |
| T-16 | Traceability to the source text; accept against the original, not the task list | `standards/TESTING.md` | discipline |
| T-17 | Drift guard: one source of truth, every other copy gated, ungated items declared | `standards/TESTING.md` | discipline |
| T-18 | Ratchet baseline: debt that may only shrink | `standards/TESTING.md` | discipline |

### R — Review recipes (`standards/REVIEWING.md`)

| ID | Rule | Home | Enforced by |
|---|---|---|---|
| R-01 | Two verdicts: spec conformance and quality grade | `standards/REVIEWING.md` | discipline |
| R-02 | Detect idle tests (delete the implementation; does it still pass?) | `standards/REVIEWING.md` | discipline |
| R-03 | Boundary and quantitative math | `standards/REVIEWING.md` | discipline |
| R-04 | Evidence-chain inversion ("the gate that cannot fail") | `standards/REVIEWING.md` | discipline |
| R-05 | Self-proving vector trap | `standards/REVIEWING.md` | discipline |
| R-06 | Cross-boundary key consistency | `standards/REVIEWING.md` | discipline |
| R-07 | Stale cache and delivery penetration (physical fingerprint) | `standards/REVIEWING.md` | discipline |
| R-08 | Reviewer's three laws (run the gates yourself, reproduce red, adversarial posture) | `standards/REVIEWING.md` | discipline |

### E — Execution loop (`standards/EXECUTION.md`)

| ID | Rule | Home | Enforced by |
|---|---|---|---|
| E-01 | Applicability switch: scale dial, host adaptation, one severity ladder | `standards/EXECUTION.md` | discipline |
| E-02 | The eight steps and their file artifacts | `standards/EXECUTION.md` | discipline |
| E-03 | Carry-forward: findings never evaporate | `standards/EXECUTION.md` | discipline |
| E-04 | Rulings disclosure at stage close | `standards/EXECUTION.md` | discipline |
| E-05 | Progress ledger × micro-snapshot (two tracks, not interchangeable) | `standards/EXECUTION.md` | `checkpoint.py` |
| E-06 | Incident entries: symptom → root cause → fix → verify → prevent | `standards/EXECUTION.md` | discipline |
| E-07 | Anti-pattern list | `standards/EXECUTION.md` | discipline |
| E-08 | Never write a single measurement into a document as fact | `standards/EXECUTION.md` | discipline |

### C — Architecture method (`standards/ARCHITECTURE.md`)

| ID | Rule | Home | Enforced by |
|---|---|---|---|
| C-01 | The seven derivation steps, in order | `standards/ARCHITECTURE.md` | discipline |
| C-02 | Three criteria: cheap to change, hard to misuse, visible when broken | `standards/ARCHITECTURE.md` | discipline |
| C-03 | Copy/build criteria by layer (commodity / standard / differentiation) | `standards/ARCHITECTURE.md` | discipline |

### L — Localization and theming (`standards/LOCALIZATION.md`)

| ID | Rule | Home | Enforced by |
|---|---|---|---|
| L-01 | Zero hardcoded natural language | `standards/LOCALIZATION.md` | `check_docs.py` |
| L-02 | Servers never concatenate human sentences | `standards/LOCALIZATION.md` | discipline |
| L-03 | Key parity gate | `standards/LOCALIZATION.md` | `check_docs.py` |
| L-04 | Bare data only (ISO-8601 UTC, bare numbers) | `standards/LOCALIZATION.md` | discipline |
| L-05 | Language state is a single source of truth, and a switch fans out | `standards/LOCALIZATION.md` | discipline |
| L-06 | Layout elasticity budget of 30%–50% | `standards/LOCALIZATION.md` | discipline |
| L-07 | Missing-key degradation (show the key, warn in dev) | `standards/LOCALIZATION.md` | discipline |
| L-08 | Uniform `Accept-Language` header | `standards/LOCALIZATION.md` | discipline |
| L-09 | Structured error codes, never sentences | `standards/LOCALIZATION.md` | discipline |
| L-10 | Persisted enums must be neutral codes | `standards/LOCALIZATION.md` | discipline |
| L-11 | Content fallback chain `target → default → raw` | `standards/LOCALIZATION.md` | discipline |
| L-12 | AI prompt passthrough with "Respond strictly in {target_language}" | `standards/LOCALIZATION.md` | discipline |
| L-13 | Theme has a single source of truth (`light`/`dark`/`system`) | `standards/LOCALIZATION.md` | discipline |
| L-14 | Semantic design tokens; no raw color values | `standards/LOCALIZATION.md` | discipline |
| L-15 | Zero FOUC | `standards/LOCALIZATION.md` | discipline |
| L-16 | Per-stack adapters must be applied per stack, not globally | `standards/LOCALIZATION.md` | discipline |

---

## 3. Maintaining this index

1. **Adding a rule**: create it in its home file, add one row here with the next free ID, and note what enforces it.
2. **Changing a rule**: change the home file. Never restate the rule in a second file — link instead.
3. **Removing a rule**: delete the row and the rule together, in one commit, and record why in `docs/DECISIONS.md`.
4. **Gate**: `python tooling/checks/check_docs.py` verifies every ID's home file still exists and still contains the rule. Run it before every commit.
