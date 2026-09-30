# Open-Source Reuse Audit

Enable only when reading, borrowing from, or reusing an external project. Reading is not copying.

<p align="center"><a href="OSS_REUSE_AUDIT_TEMPLATE.md">English</a> · <a href="OSS_REUSE_AUDIT_TEMPLATE.zh-CN.md">简体中文</a></p>

## Classification
- **Direct source reuse / adaptation**: record the exact source file, pinned commit, license, target file, and how attribution is preserved.
- **Behavior / test-pattern reference**: record only the behavior or test idea referenced. Never call this a source port.
- **Keep our own implementation**: state the basis for comparison and why it was not replaced.
- **Not adopted / closed**: state the product mismatch, license, maintenance cost, or insufficient evidence.
- **Awaiting user confirmation / awaiting evidence**: list the single blocking question. Never disguise it as an approved task.

## Audit table
| Candidate repo | Pinned commit | Source file | License | Classification | Target file | Attribution/NOTICE | Test evidence | Status |
|---|---|---|---|---|---|---|---|---|
| `[owner/repo]` | `[sha]` | `[path]` | `[license]` | `[class]` | `[path]` | `[method]` | `[path/command]` | `[status]` |

When a license is unknown or incompatible, do not copy source. GPL/AGPL implications must be stated separately and the user decides whether to integrate another way.
