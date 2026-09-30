# Technical Constraints and Pitfalls (CONSTRAINTS.md)

> **What goes here**: pitfalls that will bite you *in this codebase* — the constraint, the trap, the thing that looks fine and isn't. Every entry carries **Why** and **Date**, because a rule whose reason is lost gets deleted by the next person who finds it inconvenient.

<p align="center"><a href="CONSTRAINTS.md">English</a> · <a href="CONSTRAINTS.zh-CN.md">简体中文</a></p>

## How this file is routed

| Kind of correction | Goes to | Shape |
|---|---|---|
| A technical pitfall — "this API breaks on X", "don't touch that config", "that call silently truncates" | **this file**, under the matching domain | `constraint — Why: … (YYYY-MM-DD)` |
| A working preference about AI behavior — "don't run the tests full-screen", "prefer pure functions" | [`AGENTS.md`](../AGENTS.md) lessons list | negative constraint |
| A business rule | [`SPEC.md`](../SPEC.md) | rule text |
| An architectural decision | [`DECISIONS.md`](DECISIONS.md) | context / decision / impact |

Keep the split: a technical pitfall in the lessons list gets buried among behavior rules, and a behavior rule in this file reads as if the code were at fault.

## Entry format

```markdown
- **<one-line constraint>** — Why: <the failure it prevents>. (YYYY-MM-DD)
```

## Domains

Add a section only when it has entries. Delete a section when its last entry goes.

### Data and persistence

- _example_ — **Never rewrite a migration that has already shipped** — Why: some installs have already applied it; editing it in place leaves their schema permanently divergent with no error. (2026-01-01)

### Platform and native

### UI and interaction

### Build, CI, and release

### Dependencies

---

## Don't do this

- Don't record a pitfall without its **Why**. The next reader will "clean up" an unexplained rule.
- Don't record the same pitfall in two domains. Pick the one where someone would look.
- Don't use this file for things the type system or a gate already enforces — that's what `standards/TESTING.md` is for.
