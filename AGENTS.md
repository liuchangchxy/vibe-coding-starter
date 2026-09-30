# AI Agent Code of Conduct & Automated Pitfall Engine (AGENTS.md)

This repository is a general-purpose project scaffold built on **Spec-Driven Development (SDD)** and **zero-mental-overhead Vibe Coding**.

> **Universal Inheritance Constitution** — This document is the general mother standard. It automatically binds this scaffold itself *and* every open-source project cloned, derived, or initialized from it. Any AI assistant working in this repo or its derivatives (Anti Gravity, Cursor, Claude Code, Windsurf, Aider, Copilot, …) must treat the rules below as the highest code of conduct. **Never dismiss them as local special-cases of one project.**

---

## Engine 1 — Auto-persist spoken intent (Auto-Sync to Spec)

When the user mentions **a feature change, a business rule change, a test failure, or a new requirement** ("don't compute it that way", "make the UI two columns", "the test blows up in this case"):

1. **Mandatory baseline injection** — When the user starts a new project from this scaffold, the AI **must proactively plan** the *Localization & Theme architecture*, *Design Tokens for light/dark*, *SPONSOR.md*, and *FAQ.md* into that project's `SPEC.md` (see `SPEC.md` §6 and §7). These are standard factory settings for every open-source project. Never treat them as optional plugins, and never silently drop them because the user did not ask.
2. **Disambiguation gate** — If the request lacks a measurable acceptance criterion ("make loading faster", "add an export feature") or has several mutually exclusive architectural routes, **never guess and start coding**. List 2–3 concrete options with trade-offs and let the user decide before writing to SPEC.
3. **Extract and persist** — **First** update [SPEC.md](SPEC.md) (or the shard under `specs/`) via a file-editing tool, turning the spoken requirement into a written business rule. Do not merely discuss it in chat, and do not silently change code. Open your reply with: *"💡 Synced this requirement to SPEC.md §X.X."*
   **Exception**: pure confirmation ("ok", "proceed", "go ahead", "agreed") is an execution confirmation, not a requirement change — no SPEC edit needed.
- **Research on a frozen requirement is exploration, not change** — evaluating alternatives (a different framework, library, or service) for a requirement already frozen in SPEC is exploration. The findings stay **out of SPEC**, and SPEC moves only when the user explicitly changes the requirement.
4. **Micro-checkpoint protocol** — Before large refactors, cross-file rewrites, or other high-risk changes, run `python tooling/checks/checkpoint.py save "<what I'm about to do>"` so the state can be restored losslessly in milliseconds.
5. **Decision trail** — For breaking changes or significant architectural rewrites, append a timestamped entry (context / decision / impact) to [docs/DECISIONS.md](docs/DECISIONS.md).
6. **Defect-driven regression defense** — Write or update the regression test *before* changing implementation. **Anti-tampering red line**: never modify an existing assertion or delete an old test case to make a red suite green. Never use `git commit --no-verify`. Never report completion while tests are failing.

---

## Engine 2 — 1-to-4 root-cause divergence (1-to-4 Bug Divergence Protocol)

When the user asks for an **adversarial review**, raises a doubt, or reports any defect, never fix only the single failing line. From each reported point, **enumerate at least four classes of co-occurring/sibling/upstream-downstream defects** and report the evidence for each:

1. **Lateral pattern scan** — grep the whole repo for the same call shape, syntax pattern, or API usage.
2. **Boundary & inverse input scan** — null/None, oversized text, special characters, race conditions, unresolved async, network jitter.
3. **Contract & drift scan** — field naming and types across the boundary, localization/timezone penetration, structured error codes.
4. **Lifecycle & persistence scan** — stale caches, dirty local storage, state not restored after a reload, residue after logout or a user switch.

> 💡 **Output rule**: before fixing, present the four dimensions with explicit findings (either "verified safe" or "found X, fixing it too"). One clue should kill a whole class of defects.

### Severity ladder (P0–P3)
- **P0 Fatal (blocks delivery)** — data corruption, main-flow deadlock or crash, irreversible operations → **must be zeroed out. Absolute veto.**
- **P1 Severe (core gap)** — core behavior diverges from SPEC, garbled text, key flow broken → **must be fixed; suite fully green.**
- **P2 Minor (edge tolerance)** — extreme network jitter, unfriendly copy → **log it as a todo; do not block delivery.**
- **P3 Cosmetic (theoretical)** — formatting nits, extremely unlikely hypotheticals → **ignore. Never spiral on these.**

### Convergent Definition of Done
When the user asks to "converge", "do a final review", or "confirm shippability":
- Do **not** keep inventing P2/P3 theoretical risks.
- The bar: **all P0/P1 cleared** and **the automated suite (including real E2E) at 100% with `skipped=0`**. When met, state plainly: *"✅ All core functions and data safety have converged; delivery accepted."*
- **Attach a Rulings list.** At the end of any authorized autonomous run, besides the DoD verdict, list every behavior/scope/cost-level decision the AI made on the user's behalf, one per line, in the format `ruling → cost of being wrong`. Pure implementation details are excluded; anything long-lived also goes into `docs/DECISIONS.md`. **Never rule silently.** (Procedure: `standards/EXECUTION.md` §3.)

---

## Engine 3 — Self-learning from errors and preferences

When the user **corrects, criticizes, or states a working preference** ("don't touch that config", "no full-screen test output", "prefer pure functions"):

1. **Append to the lessons list** — the AI must proactively edit this file (`AGENTS.md`), appending a negative constraint to the **Lessons Learned** section below.
2. From the next interaction onward, that rule is loaded as an inviolable red line.

---

## The 8 universal hard constraints

1. **Single source of truth** — [SPEC.md](SPEC.md) is the final standard for any business change. Code is only the materialization of the spec.
2. **Non-destructive operations** — Never physically delete existing data or overwrite protected system configuration without explicit user permission.
3. **Anti-test-tampering** — Never manufacture a green suite by relaxing assertions, deleting cases, commenting out assertions, or marking tests skipped. Implementation adapts to tests, never the reverse. Physical detector: `tooling/checks/guard_test_tampering.py`.
4. **No hardcoded absolute paths** — Never write a developer machine's absolute path (`C:\Users\...`, `/home/...`) into source. Derive paths from the current file's location or inject them via environment variables. Detector: `tooling/checks/scan_hardcoded_paths.py`.
5. **Localization and visual theming are first-class** — see [standards/LOCALIZATION.md](standards/LOCALIZATION.md).
   - *Interaction localization (applies to anything with user-facing output)*: zero hardcoded natural-language copy; servers must never concatenate human-readable sentences — return structured codes like `{"error_code": "CODE", "params": {...}}`; dictionaries must be key-for-key aligned (Key Parity). Pure low-level libraries with no interaction are exempt.
   - *Visual theming (only for projects with a GUI/Web/mobile surface; pure CLI/backend exempt)*: semantic design tokens only, never raw color values in components; entry points must configure anti-flicker (Zero FOUC).
6. **Standard open-source deliverables** — open-source projects must ship [templates/SPONSOR.md](templates/SPONSOR.md) and [templates/FAQ.md](templates/FAQ.md).
7. **Delivery must be green** — after changing code, run the tests proactively. Never commit a sick tree.
8. **Mandatory end-to-end verification** — never rely on mock unit tests alone. Changes touching a full flow, persistence, or a critical data path must run the corresponding real-link verification. Never report `skipped` as passing.

---

## Complexity switch and evidence

The starter is a *general base plus opt-in extensions*. No project must enable the full process.

1. Small change or single-file fix: this file, `standards/TESTING.md`, and the relevant tests are enough. Do not create a Master Plan or dispatch agents for form's sake.
2. Cross-module work, data migration, irreversible operations, or multi-agent tasks: read `standards/EXECUTION.md` first, then enable the applicable extension under `docs/optional/`.
3. `SPEC.md` records confirmed product rules; implementation status, source locations, and run evidence live in `docs/REQUIREMENTS_TRACEABILITY.md`. An entry without real evidence may only say "unverified" or "not run".
4. Choose the verification layer by project boundary: a browser, a real API, a real database, a real filesystem, or a real CLI. Lower-layer tests must never impersonate a higher-layer user path.
5. Enable the OSS / data-safety / stepper / reliability extensions under `docs/optional/` only when the corresponding situation actually arises.

---

## Lessons Learned (AI-appended)

> ⚠️ The AI appends here automatically whenever the user corrects it. These must never be violated again in a new session.

1. **[Init]** Never change a requirement by editing code alone — sync `SPEC.md` first.
2. **[Init]** Before delivery, make sure the automated suite is fully green. No "fixed A, broke B".
3. **[Adversarial review]** Never commit with `--no-verify`; the pre-commit gate must run.
4. **[User correction]** Never run mock unit tests alone. Run the real end-to-end link before every delivery.
5. **[Absolute]** Never count a suite containing `skipped` as passing. Confirm the cases physically ran with `skipped=0`; if the environment forced a skip, state it plainly.
6. **[Windows encoding]** Every `subprocess.run(..., text=True)` must pass `encoding="utf-8", errors="replace"`. Bare `text=True` turns UTF-8 Chinese into GBK mojibake.
7. **[Self-deceiving tests]** Never quietly edit an old test's expected value to fake a green run. Fix the implementation. Any test tampering is a severe quality incident.
8. **[Global root-cause treatment]** Never fix a bug by editing one isolated line; sweep the whole project for the same pattern.
9. **[Pragmatic research]** Never hand-wave or dismiss a small open-source project because of its star count. Do code-level, runnable, empirical evaluation. Respect existing wheels; conclude from code facts.
10. **[Stay on target]** When asked to dissect a named candidate project and "take the good, drop the bad", do not wander off into unrelated algorithm detail. Stay focused on that project's features, implementation, strengths, weaknesses, and integration strategy.
11. **[Don't get stuck on local detail]** When one sentence contains both a local technical detail (a file-conversion routine) and a global product goal (matching a competitor's experience), never spiral on the detail. The user's end-user scenario and product experience govern; local implementation serves it. Never let the tail wag the dog.
12. **[No premature or polluted SPEC]** Until research and empirical verification have converged, never write unverified technical hypotheses into the core sections of `SPEC.md`. SPEC holds *what the user actually wants and how it will be accepted*, not the AI's pet technical topic.
13. **[Separate evidence states]** A requirement existing in SPEC does not mean it is implemented. Record source, tests, run results, and uncovered boundaries separately in the traceability matrix.
14. **[Real-link layering]** Unit tests, mocks, a successful build, and API integration tests must not impersonate one another. Reports must state the layer and pass/fail/skipped/not-run.
15. **[Complexity stop-loss]** Do not apply multi-agent, Master Plan, browser E2E, or OSS audits to small tasks. Enable extensions only when the trigger condition holds.
16. **[SPA entry, zero cache]** A SPA's static entry (HTML) must be served with `Cache-Control: no-cache, no-store, must-revalidate`. Otherwise hash-busted assets are moot because clients and embedded hosts (Electron/WebView/iframe) keep serving the cached entry.
17. **[Non-blocking steppers]** In wizards and multi-step flows, never block forward/backward/skip because a previous step is incomplete. Step transitions must auto-persist a draft and restore idempotently; prior state is only a validation marker. Gate strictly at the final commit action.
18. **[Constrained viewport budget]** Touch/mobile layouts must strip desktop-only affordances (keyboard shortcut hints). The top bar must stay on a single compact line (≤ 44px); the primary trigger and current-state feedback must be visible in the first screen with zero scrolling. Never substitute "the page can scroll" for information-density work.
19. **[Zero credentials in the repo]** Real credentials (admin passwords, API keys, tokens, private keys) must never be written into any Git-tracked file — including test scripts, seed/init scripts, deploy scripts, and documentation examples. Scripts read them from environment variables and **must fail loudly when they are missing**, never fall back to a weak or example value.
20. **[Pre-push redaction census]** Before pushing to a public repo, scan the whole tree and handle every item: internal IPs/hostnames, real passwords, API keys, databases and build artifacts, `.env`-like files. **Census first, then act.**
21. **[History is public]** Once a credential is committed, deleting it in a later commit leaves it in plaintext in the old commits. On confirmed exposure, rewrite history (`git filter-repo --replace-text`) rather than adding a deletion commit.
22. **[1-to-4 protocol]** On a bug report or adversarial review, enumerate lateral, boundary, contract, and lifecycle sibling defects with evidence.
23. **[Zero tolerance for absolute paths]** Never hardcode a local filesystem path; derive it dynamically or inject via environment variables.
24. **[Universal localization gate]** Never patch localization on afterwards. Interaction layers forbid raw copy; servers forbid concatenated human-readable sentences; dictionaries must be bidirectionally aligned under a gate. Pure algorithm/no-interaction projects are exempt.
25. **[Standard open-source deliverables]** An open-source project must ship SPONSOR.md and FAQ.md.
