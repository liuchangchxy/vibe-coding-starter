# Top-Down Architecture Derivation (ARCHITECTURE.md)

> **Scope**: this file teaches the **method** — how to derive a good architecture from zero. The **product** of the derivation goes into `SPEC.md` §2 (architecture and data flow). SPEC §2 is "what this project looks like"; this file is "how to arrive at it".
> **Audience**: vibe coders. You do not need UML. You need to answer the seven questions below.

<p align="center"><a href="ARCHITECTURE.md">English</a> · <a href="ARCHITECTURE.zh-CN.md">简体中文</a></p>

---

## The seven steps (strictly in order; nothing proceeds until the previous step is on paper)

1. **Write the forces first, not the diagram.**
   Architecture is trade-offs under constraint. Start by listing: who uses it / at what scale / how many maintainers / what must never be lost.
   → Those four lines eliminate 90% of technology options (a personal tool does not deserve a cluster; a solo maintainer does not deserve microservices).

2. **Data model first — define the nouns.**
   Define the core entities, their peer relationships, and their invariants (who may change whom, what must hold simultaneously).
   → A system's solidity ≈ the clarity of its entities and invariants; UI, API, and sync are all projections of that model. **Get this wrong and everything downstream is rework.**

3. **Draw the consistency boundaries.**
   Mark what must be atomic (inside a transaction), what may be temporarily inconsistent, and what converges it (queue / cursor / retry).
   → This is the soul of backend design. Golden disciplines like "single write path" are usually products of this boundary.

4. **Choose boring technology — scale decides, taste does not.**
   For every component, ask: does my scale deserve this? Use files where a database is unnecessary; stay single-machine where distributed is unnecessary.
   → "I didn't use the fancy thing" is usually correct judgment, not a shortfall.

5. **Interface before implementation — freeze the wiring diagram.**
   Write the data structures and interface contracts (the ones shared across the frontend/backend or between modules) before the implementation.
   → Once the contract is frozen, parties can work in parallel and verify each other instead of stepping on each other.

6. **Design for deletion.**
   Ask: six months from now, if I want to remove this piece, does it come off cleanly? (One-way dependencies, logic enclosed within its directory, tests that tell you what you broke.)
   → The hidden criterion of good architecture: **deletion is cheap**.

7. **Decision trail and architecture verification are one thing.**
   Record key trade-offs into `docs/DECISIONS.md` on the spot (context / decision / impact). The design must include its **acceptance method** (E2E matrix, contract tests). Verification is not a postscript to the code; it is part of the design.

---

## The three criteria for "good architecture" (forget words like "elegant" and "advanced")

> **Cheap to change · Hard to misuse · Visible when broken**

- **Cheap to change** — clear layering, frozen contracts, clean deletion;
- **Hard to misuse** — default-deny, single write path, types and conventions enforced by the type system or tests rather than by discipline;
- **Visible when broken** — errors have a path to the surface, derived state has a unified invalidation mechanism, monitoring and logging are part of the design rather than patches.

Score your design against these three sentences before delivering. It is more honest than any architecture diagram.

---

## "Copy vs. build" criteria (against both reinventing wheels and blind adoption)

| Layer | Strategy |
|---|---|
| **Commodity** (frameworks, databases, generic UI, utility libraries) | **Use existing open source.** Do not build it. |
| **Standards** (HTTP, OAuth, protocol-level) | **Copy the published RFC/standard.** The standard *is* the whole world's shared wheel. |
| **Differentiation** (your core data model + unique experience) | **You must build it.** It is the product. |

Research discipline when evaluating candidate projects lives in the AGENTS lessons list (pragmatic research, code-level evidence, no star-count dogma): **you copy decisions and standards, not entire repositories. Before forking a whole repo, check its protocol compatibility and license.**
