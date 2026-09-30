# START HERE — the single resume entry point

> **Instruction to the AI**: when the user says *"where do we start"* or *"continue the project"*, read this file first, then act on the priority queue below.
> This file is the **only index of outstanding work**. Status information is *referenced* from the specialist documents, never restated here — restating it is how it drifts.

<p align="center"><a href="START_HERE.md">English</a> · <a href="START_HERE.zh-CN.md">简体中文</a></p>

**Last updated: YYYY-MM-DD · current version follows [the source of truth], not this line**

---

## 1. Where we are (one paragraph)

[One paragraph a fresh session can read in ten seconds: which phase we finished, what shipped, what is verified. Point at the document that owns each claim instead of summarizing it.]

## 2. Priority queue (in order)

| # | Item | One-line description | Detail lives in |
|---|---|---|---|
| 1 | | | |
| 2 | | | |

## 3. The complete "said but not done" list

Everything that surfaced in conversation and has not earned a slot in any task tracker yet. This section exists because these items are otherwise lost when the conversation ends.

- [ ]
- [ ]

## 4. Outstanding debt

[Architectural debt, known defects, deferred cleanups — each with where its full argument lives.]

## 5. Documents that own the truth

| Question | Document |
|---|---|
| What must the product do? | [`SPEC.md`](../SPEC.md) |
| How do we do engineering here? | [`standards/`](../standards/) — index at [`RULES.md`](../standards/RULES.md) |
| What did we decide, and why? | [`DECISIONS.md`](DECISIONS.md) |
| What is actually implemented and proven? | [`REQUIREMENTS_TRACEABILITY.md`](REQUIREMENTS_TRACEABILITY.md) |
| What bites us in this codebase? | [`CONSTRAINTS.md`](CONSTRAINTS.md) |

---

## Why this file exists

A new session starts with no memory. Without one agreed entry point, it either re-derives context from scratch (expensive, and it will get details wrong) or starts guessing. One file, read first, removes both failure modes — and gives the human a single place to answer "what's left?".

**Maintenance**: update it at the end of every work session. If a line in this file disagrees with the document it points at, the document wins and this line is a bug.
