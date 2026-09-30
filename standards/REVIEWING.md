# Adversarial Review Recipes (REVIEWING.md)

> **Scope**: review is the **discovery phase**. The fixing phase must return to `standards/TESTING.md` — root-cause treatment, sweeping the whole repo for the same pattern rather than editing one isolated line.
> **Output discipline**: the reviewer **must re-run the gates personally** (analyze/test). Never conclude from the implementer's report alone. Anything found outside the diff range is marked "⚠️ out of scope" and escalated for a ruling — never unilaterally widen the change.

<p align="center"><a href="REVIEWING.md">English</a> · <a href="REVIEWING.zh-CN.md">简体中文</a></p>

---

## Output format (two verdicts, both mandatory)

1. **Spec conformance** — check item by item against the brief/SPEC → ✅ / ❌ with evidence (`file:line`).
2. **Quality verdict** — `Approved`, or a findings list graded **P0–P3** (Critical→P0/P1, Important→P1, Minor→P2/P3; mapping in `standards/EXECUTION.md` §0).

Every finding carries `file:line` + *what is wrong* + *why it matters*. Empty advice like "could be nicer" is banned.

---

## Six attack recipes (walk all of them each round)

### 1. Detecting idle tests
A test whose assertion carries no real constraint is idle. Check: delete the implementation, or replace it with the identity function — does the test still pass? Does the assertion merely echo the implementation (`expect(f(x), f(x))`)? **A test only exists if it can go red when the implementation is wrong.**

### 2. Boundary and quantitative math
Hand-compute the boundaries for time, money, indices, and sequence numbers: `±1`, empty collections, zero length, carry/date rollover, floating-point precision floors. **Example**: SQL comparing float dates vs. Dart comparing microsecond integers can disagree at the same boundary — pin both sides to one canonical form (e.g. a fixed-width string) or add boundary tests.

### 3. Evidence-chain inversion ("the gate that cannot fail")
Ask: **can this acceptance gate go red when the implementation is wrong?** If the file the gate depends on is never referenced by the build (configured but not wired), or the verification is unrelated to the thing being verified, the gate is an **idle ritual**. Multi-layer proof: config file → build settings → produced binary. Only when all three layers show it does the gate count as effective.

### 4. Self-proving vector trap
A test that computes the expected value with **the same formula as the implementation** is circular; break the implementation and it stays green. Pin **external literals**: test vectors published by a standards body, hand-computed answers, upstream golden files.

### 5. Cross-boundary key consistency
When one contract is implemented in several places (frontend/backend fields, dual-platform native readers, config keys), grep the whole repo for old and new key names and verify **key-for-key, type-identical, with a version gate**. Any side left unchanged or mistyped means silent data loss.

### 6. Stale cache and delivery penetration
- **Static-entry hard-cache deadlock**: if a SPA's entry HTML is not served with `Cache-Control: no-cache, no-store, must-revalidate`, no amount of asset hash-busting helps — the client keeps loading the cached entry.
- **Embedded containers and shell memory residency**: inside Electron, a native desktop WebView, a platform iframe, or a mobile native shell, a refresh or rebuild often cannot break through the container's own in-memory web view cache.
- **Fingerprint penetration rule**: when closing out delivery, never substitute "the build command succeeded" or "the backend port returns 200" for end-side delivery. Extract a **physical fingerprint** carrying a unique change signature (version metadata, Git commit SHA, a build timestamp marker, or a unique style signature on a new DOM node) from the real DOM/runtime of the final consuming end, proving the new artifact physically reached the user's viewport.

---

## The reviewer's three laws

1. **Run the gates yourself** — a green in someone's report means nothing until you run it.
2. **Red must be reproducible** — for a claimed critical fix, prefer "red before, green after" evidence over merely seeing a new test pass.
3. **Adversarial posture** — every round, actively attempt at least once to *make this implementation fail* (swap the formula, feed malformed input, add concurrency, introduce cross-boundary mismatch). If you find nothing, write down where you looked.

---

## Interfaces with the other documents

- How to fix what you found → `standards/TESTING.md` §1.1 (defect-driven testing) and §1.5 (1-to-4 global sweep);
- When to stop reviewing → `standards/TESTING.md` §3 DoD (P0/P1 cleared, suite 100% with `skipped=0`);
- Where findings go → `standards/EXECUTION.md` §2 carry-forward (ledger → next task → roadmap).
