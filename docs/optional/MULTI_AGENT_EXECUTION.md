# Multi-Agent Collaboration Extension

Enable only when work genuinely needs parallel research, cross-module collaboration, or independent review. Small tasks use a single agent — process cost must not exceed the task.

<p align="center"><a href="MULTI_AGENT_EXECUTION.md">English</a> · <a href="MULTI_AGENT_EXECUTION.zh-CN.md">简体中文</a></p>

## Recommended boundaries
- **Read-only research agent**: reads named files and evidence; must not modify the working tree.
- **Implementation agent**: executes only a confirmed leaf plan.
- **Review agent**: examines only requirements, diffs, tests, and evidence.
- **Lead agent**: rules on conflicts, merges conclusions, and persists them.

Multiple agents must not simultaneously edit the same shared files without boundaries. Every subtask states its scope, inputs, outputs, evidence path, and uncertainties.
