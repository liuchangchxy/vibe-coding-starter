# Decision and Evolution Timeline (DECISIONS.md)

> A micro-log (lightweight ADR) of major architectural adjustments, requirement changes, and the reasoning behind them.
> **Purpose**: stop you — weeks or months later — from asking "why on earth did we make it behave like this?", and stop requirements from flip-flopping.

<p align="center"><a href="DECISIONS.md">English</a> · <a href="DECISIONS.zh-CN.md">简体中文</a></p>

---

## Entry template
```markdown
### [YYYY-MM-DD] [Change title]
- **Context**: user feedback / performance bottleneck / test anomaly
- **Decision**: changed rule XXX to YYY
- **SPEC section**: SPEC.md §X.X
- **Impact**: [modules or files touched]
```

---

## Timeline

### [2026-09-22] Repository scaffold initialization
- **Context**: create the Vibe Coding Starter general standard template.
- **Decision**: establish SDD (spec-driven) + two-layer gates + a self-evolving lessons list as the core workflow.
- **SPEC section**: whole document initialized.
- **Impact**: global.

### [2026-09-22] Harden against local-detail rabbit holes and premature SPEC pollution
- **Context**: during real sessions, an AI readily let a local technical detail in one sentence hijack the design, elevating a supporting mechanism to the system's core positioning and polluting the single source of truth before any research had converged.
- **Decision**:
  1. Add a primary/secondary check in AGENTS Engine 1: never let local detail dominate; the user's end-user scenario and product experience always govern;
  2. Add a rule against premature or polluted SPEC: no unverified technical hypothesis may enter the core positioning of SPEC.md;
  3. Permanently freeze these as lessons 11 and 12.
- **SPEC section**: global standards evolution.
- **Impact**: AGENTS.md.

### [2026-09-24] [Example] One severity ladder: P0–P3
- **Context**: different review stages emitted two ladders (P0–P3 and Critical/Important/Minor). Coexistence scrambles the convergence criteria.
- **Decision**: P0–P3 from AGENTS/TESTING is the only ladder; other ladders are mapped (Critical→P0/P1, Important→P1, Minor→P2/P3). Stopping always follows the DoD.
- **SPEC section**: global standards evolution.
- **Impact**: `standards/EXECUTION.md` §0, `standards/REVIEWING.md` output format.

### [2026-09-24] [Example] When an experiment overturns a prior instruction, the experiment wins
- **Context**: an instruction was given following a documented precedent ("clear that config key"), but a controlled experiment showed that shape also caused the failure.
- **Decision**: stop executing the literal instruction, adopt the stronger fix the evidence supported, and file the experiment that overturned the original instruction.
- **SPEC section**: not a business rule; engineering execution layer.
- **Impact**: DECISIONS.md entry format; execution discipline in `standards/EXECUTION.md` §5.

### [2026-09-30] Full restructure into layers, and full bilingual documentation
- **Context**: eight Markdown files had accumulated at the root while others were nested under `docs/`; the same rule (severity ladder, 1-to-4, secret hygiene) was defined in two or three files at once and had begun to drift. The repo also positions itself as an open-source template while shipping Chinese-only docs.
- **Decision**:
  1. Re-layer the tree: convention-bound files stay at the root; `standards/` holds method, `docs/` holds project records, `templates/` holds copy-in files, `tooling/` holds scripts and tests;
  2. Introduce `standards/RULES.md`, a master index giving every rule one stable ID and exactly one home, gated by `tooling/checks/check_docs.py`;
  3. Every Markdown document ships in two mirrored files, `NAME.md` (English, the default) and `NAME.zh-CN.md` (Simplified Chinese). Chinese is the authoring source; English mirrors it;
  4. Promote `templates/ci.yml` to a live `.github/workflows/ci.yml` so the scaffold verifies itself.
- **SPEC section**: global standards evolution.
- **Impact**: the entire repository.
