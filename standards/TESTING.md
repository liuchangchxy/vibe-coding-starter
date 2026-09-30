# Engineering Standards and Regression Defense (TESTING.md)

To keep a Vibe Coding session stable and aligned with the requirements — and to eliminate "changed it back and forth, fixed A and broke B" — every developer and AI collaborator must obey the following red lines.

> **How this document is organized** — §1 holds **universal gates** that apply to every project unconditionally. §2 holds **capability-gated rules** that activate only when the project's shape matches the stated boundary; unmatched projects are exempt automatically (never force an unrelated framework rule onto a project). §3 is the Definition of Done. §4 lists the common commands.

<p align="center"><a href="TESTING.md">English</a> · <a href="TESTING.zh-CN.md">简体中文</a></p>

---

## 1. Universal engineering gates

### 1. Defect-driven testing
* **Principle**: for a confirmed bug or requirement change, **never edit business code first**.
* **Procedure**:
  1. **Locate the root cause first** — no guess-fixes. Before writing anything, name why it fails; a fix aimed at a symptom will need a second fix.
2. **Write the failing test** — add a case for the bug or the new rule.
  3. **Verify it fails** — confirm it goes red against the current code.
  4. **Change the implementation** — until the test goes green.
  5. **Keep it forever** — the case stays in the permanent regression suite.

### 2. Anti-test-tampering gate
* **Principle**: when a test fails, fix the implementation. **Never** relax an existing assertion (`assert`/`expect`/`toBe`), delete an old case, comment out an assertion, or mark a test skipped to manufacture green.
* **Physical defense**: run `python tooling/checks/guard_test_tampering.py`; it analyzes the Git diff and treats any deletion or loosening of an assertion line as a quality incident and blocks it.
* **Exemption**: for a legitimately changed requirement, say so explicitly in the commit message and record it in `docs/DECISIONS.md`. Never tamper silently.

### 3. No-hardcoded-absolute-paths gate
* **Principle**: code must never bind to one developer machine's drive letter or home directory.
* **Physical defense**: run `python tooling/checks/scan_hardcoded_paths.py`. Derive paths dynamically from the current file's location (e.g. `Path(__file__).resolve().parent`, `import.meta.url`, or the language's equivalent) or inject them via environment variables.

### 4. Contract defense and no silent tolerance
* **Principle**: refuse *silent* deadlocks and data drift caused by loose error tolerance. Fail loudly rather than swallow an inconsistency.
* **Contract assertion**: field names across a boundary, configuration keys, and function return shapes must be pinned by tests (see `standards/REVIEWING.md` recipe 5, cross-boundary key consistency).
* **Applies to**: projects with a cross-process or cross-device contract (API, config keys, native bridge, dual-platform readers). A purely in-process function library is exempt.

### 5. 1-to-4 root-cause divergence
* **Principle**: never treat a defect as one isolated line.
* **Census before you touch anything**: any "change these N places" task starts with a full-repo re-scan of the same pattern. An audit's sample count is a lower bound (a report saying 15 often means 35). Skipping the census and editing directly counts as a fake completion.
* **Divergence action**: for each confirmed defect, investigate four classes of sibling defects and report the evidence:
  1. **Lateral** — same call, similar structure, same API pattern elsewhere;
  2. **Boundary/inverse** — null, oversized, special characters, races, unresolved async, network jitter;
  3. **Contract drift** — field naming and types, localization/timezone penetration, structured error codes;
  4. **Lifecycle/persistence** — stale cache, dirty local state, restore-after-reload, residue after logout.

### 6. Style-as-test (self-scanning source guards)
* **Principle**: any rule that "someone will break again" must become a **permanent test that scans your own source**, turning a suggestion into a gate. (`standards/EXECUTION.md`'s "CI greps the version number" is one special case of this method.)
* **The triad**:
  1. Scan **source text**, not runtime behavior (forbidden APIs, illegal literals, keys that must appear in pairs);
  2. The guard **ships its own violating and compliant samples** — prove it can go red and green before trusting its repo-wide verdict;
  3. Exemptions go through an **allowlist that must state WHY**, matched by **content signature rather than line number** (line numbers drift).
* **CLI convention**: every guard exposes `--selftest`, which runs only its built-in samples and reports pass/fail. This makes the red proof runnable by anyone, including CI, instead of being a claim in a report.
* **When to write one**: the **second** time a rule is violated, not the third.

### 7. Gate-as-evidence (every new gate ships a red proof)
* **Principle**: **a gate that has never gone red does not exist.** Every new gate (guard test, smoke assertion, CI step) must ship a mutation proof: how you broke it, the raw red output, and green again after reverting.
* **Red controls must be attributed**: every "verified" claim in a document must name *which control* verified it. Citing the wrong layer (something that actually died one layer earlier but is written up as caught later) is an evidence-chain defect.
* **Why**: green only proves "it didn't blow up this time"; red proves "it will make a noise when it does". A gate without a mutation proof is, 99% of the time, a ritual that cannot fail (see `standards/REVIEWING.md` recipe 3).

### 8. Orthogonal verification
* **Principle**: the means of *verifying* a thing must be independent of the means of *doing* it. Self-confirmation is not verification.
* **Three standing instances**:
  1. Whoever wrote the code does not solely verify it — a second pair of eyes, or a fresh agent, runs the gates;
  2. The verification checklist comes from the **original requirement text**, never from the task list that was derived from it (a task list inherits whatever the implementer misunderstood);
  3. A CI configuration change is proven by an ordinary push first, and only then is the release tag cut.
* **Why**: when the same mind produces both the artifact and its acceptance, a shared misunderstanding passes both. Independence is the only thing that catches it.

### 9. Traceability to the source text
* **Principle**: every user request earns a chain **original text → task → code**, and the chain is the deliverable, not paperwork.
* **Acceptance rule**: when checking whether something is finished, the criterion is the **original text**, not the task list. A task list is a lossy compression of what the user said; checking against it can only prove you did what you wrote down, not what was asked.
* **Physical form**: the original text goes into the traceability matrix or changelog verbatim. A summary may accompany it; it may not replace it.

### 10. Test layers and evidence reporting
* **Principle**: choose layers by the project's actual boundary. Lower-layer evidence must never impersonate a higher-layer user path.
* **The ladder** (take what applies; a project without the corresponding shape must not manufacture it for form's sake):
  1. **Unit / domain** — pure logic and data rules;
  2. **API / integration** — real service boundaries or component collaboration;
  3. **Database / file physical** — real persistence, transactions, rollback, conversion output;
  4. **Real-client E2E** — only when a user interface and flow exist;
  5. **Build / deploy smoke** — the deliverable starts or completes the key deploy step;
  6. **Visual smoke** — only when a visual surface exists. A machine judges "is it blank"; a human or AI judges "is it good" — the latter cannot be machine-tested.
* **Reporting discipline**: every stage report states, per layer, the **command, pass, fail, skipped, and the reason for anything not run**. Use [docs/templates/TEST_EVIDENCE_TEMPLATE.md](../docs/templates/TEST_EVIDENCE_TEMPLATE.md). Sync requirement status to [docs/REQUIREMENTS_TRACEABILITY.md](../docs/REQUIREMENTS_TRACEABILITY.md).
* **Forbidden**: calling a successful build or a mock test "the real user path passed". A project with no browser need not manufacture browser E2E — but anything touching persistence, external side effects, or a critical data path must run the corresponding real-link verification.

### 11. Secret hygiene
* **Principle**: credentials are **never** "committed then deleted" — they never enter the repository. Once recorded in history, they count as leaked.
* **Before committing**: any file containing credentials must read them from environment variables and **fail loudly when they are missing** (never fall back to a weak or example value). Never commit a `.env` with real values; commit only `.env.example`, whose values are **obvious placeholders**.
* **Before pushing**: run a redaction census (internal addresses and hostnames, real passwords, API keys, databases and build artifacts), handle every item, and record it. **Census first, then act.** For a public project this is part of the release gate.
* **On confirmed exposure**: rewrite history per `AGENTS.md` lesson 21 rather than adding a deletion commit — the latter only changes HEAD, not what an attacker can see. Report that the SHAs changed.
* **Why**: a credential's exposure surface is **all history plus all clones**, not the working tree.

### 12. Two-layer physical gate
* **Local gate (pre-commit hook)** — installed by `python tooling/checks/setup-hooks.py`. It runs the suite plus the anti-tampering and absolute-path checks on every commit and refuses a non-green tree. **Never use `git commit --no-verify`.**
* **Remote gate (GitHub Actions)** — `.github/workflows/ci.yml`. Runs the same suite on a clean runner for every push and pull request; red never merges.
* **The release gate must mirror the CI gate**: any check that guards correctness must be mounted in **both** the CI pipeline and the release pipeline. CI-only means the defect flows straight out of the release path. Write the failure mode of the release gate (e.g. the tag was pushed but no artifact was produced) into the release documentation.

---

### 13. Drift guard (single source of truth across copies)
* **Principle**: any fact a human copies into several files — a version number, a schema id, a port, a default — will drift. Name **one** file as the source of truth and gate every other copy against it.
* **Also document what is deliberately NOT gated, and why.** An undocumented omission looks like a forgotten one. (A dynamic badge that reads the release API, or a file that links to the source instead of repeating it, needs no gate — say so.)
* **Release integration**: the same guard runs with a `--tag` mode so a release tag that disagrees with the source of truth fails the release, not just CI.

### 14. Ratchet baseline (debt that may only shrink)
* **Principle**: when a newly written rule is violated all over a mature codebase, do not skip the gate — **record the current offenders in a baseline file and gate the count**.
* **Behavior**: a new violation fails immediately; removing one requires updating the baseline, so the number is monotonically non-increasing. Existing debt becomes visible and tracked instead of blocking the rule entirely.
* **Why**: the choice is not "perfect gate vs. no gate". A ratchet converts an all-or-nothing rule into a one-way valve, which is what makes it adoptable on real code.
* **Sunset**: when the baseline reaches empty, delete the baseline file and keep the gate at zero tolerance.

---

## 2. Capability-gated rules

These activate only when the project's shape matches the stated boundary. **Unmatched projects are exempt automatically.** Never force an unrelated framework rule onto a project.

### 1. Dictionary parity and no-hardcoded-copy gate (projects with human-facing interaction or copy)
* **Boundary**: projects with a user interface (Web/GUI/App), CLI output, or backend API error responses. Pure algorithm libraries and drivers are exempt.
* **Core principles**:
  - **Zero hardcoded natural language**: display copy goes through a language dictionary; never scatter raw strings through business logic;
  - **Backend purity**: interface errors return structured codes; never concatenate natural-language sentences;
  - **Key parity**: the main and target language dictionaries must be 100% mirrored; a missing translation is a hard failure;
  - **Static scan guard**: write a source-scanning test per §1.6 to catch newly written raw copy;
  - **Close all five rework sources**: the closed-type recipe, the gate set, and the pseudo-locale/outlet-inventory recipe are in [LOCALIZATION.md](LOCALIZATION.md) part 2. A gate with no type layer is discipline; a type layer with no smoke layer leaks through notifications and widgets.

### 2. Theme and constrained-viewport gate (projects with a graphical interface)
* **Boundary**: active only when the project has a graphical view (Web/desktop/mobile). Pure CLI or backend is exempt.
* **Core principles**:
  - **Semantic design tokens**: colors come from semantic variables and respond to light/dark automatically; no raw color literals in components;
  - **Zero FOUC**: the entry point must detect the theme early so nothing flashes before render;
  - **Peripheral-specificity removal**: on touch/mobile/constrained viewports, strip desktop-only affordances (keyboard shortcut guides, hover tooltips, unclickable shortcut badges). An interaction with no supporting peripheral must be removed or converted to touch;
  - **Platform awareness**: any UI or interaction change must explicitly consider **every** target platform (desktop pointer vs. touch, hover vs. long-press, keyboard vs. gesture) — never validate on one and assume the rest. A change that is only verified on one platform is unverified.
  - **Constrained-viewport physical budget**: the mobile top bar stays on a single line (≤ 44px is a good default). Never let a title, status, or action wrap and eat the viewport. The primary trigger and current-state feedback are visible in the first screen with zero scrolling; never substitute "the page can scroll" for information-density work.

### 3. Async and flaky failure triage (opt-in)
* **Boundary**: enable **only** when tests involve async UI, browser timing, network, or flakiness. **Do not impose this on ordinary deterministic unit tests.**
1. **Preserve the failure scene** — record the command, run count, failing step, and test order; add page/state, key DOM or runtime state, console/run logs, failed requests, server logs, network state, and how the service was started.
2. **Reproduce and shrink before touching the implementation** — reproduce under the same conditions, reduce the long flow to a minimal case, and first decide whether the cause is product logic, async readiness/wait conditions, cross-test state pollution, stale build output, or the environment/service process.
3. **Wait for an observable condition** — wait for the page or business state to reach the expectation, with a sane upper bound. Fixed `sleep`, blanket timeout inflation, global retries, or relaxed assertions are **not acceptable as the primary fix**; the test must keep the behavior constraint it was verifying.
4. **Confirm you are testing the current code** — check which service and frontend assets the test actually started. If the test serves build output, build first and confirm the browser loaded *this* build. Every scenario needs an explicit precondition and cleanup so an earlier failure cannot pollute a later one.
5. **Repeat by risk** — after a fix, run the minimal repro and the related regression. Schedule repeat sampling only when flakiness or a race has actually been confirmed; **a fixed repetition count is not a universal DoD**. Report the real conditions, total runs, and the pass/fail counts. Never let one success hide a known instability.

---

## 3. Definition of Done

**Severity ladder**
- **P0 Fatal** — data loss/corruption, main-flow deadlock or crash → **zeroed out, absolute veto**;
- **P1 Severe** — core behavior diverges from SPEC, garbled text, key flow broken → **must be fixed**;
- **P2 Minor** — extreme network jitter tolerance, copy polish → **log as a todo, does not block delivery**;
- **P3 Cosmetic** — theoretical risks, formatting nits → **ignore; never spiral**.

**Green-light conditions**
- All P0/P1 cleared;
- Every automated test and static scan declared in scope (hardcoded paths, assertion tampering) actually ran and passed 100%;
- The automated suite reports `skipped=0` (if a physical-hardware absence forced a skip, state the exemption reason plainly);
- When met, confirm acceptance and ship.

---

## 4. Commands

```bash
# 1. Run the project's unit and smoke tests
python -m unittest discover -s tooling/tests -p "test_*.py" -v
# or, for a Node project: npm test

# 2. Check the Git diff for tampered test assertions
python tooling/checks/guard_test_tampering.py

# 3. Scan the source for hardcoded absolute paths
python tooling/checks/scan_hardcoded_paths.py

# 4. Verify bilingual doc parity and the rule index
python tooling/checks/check_docs.py
```
