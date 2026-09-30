# Reliability Extension: Idempotency, Retry, and Terminal States

Enable only when a request mutates persisted state, triggers an external side effect, or could be executed twice because of a network retry.

<p align="center"><a href="RELIABILITY.md">English</a> · <a href="RELIABILITY.zh-CN.md">简体中文</a></p>

## Minimum requirements
1. State writes carry a stable idempotency identity — a request ID, a business key, or an idempotency key.
2. Re-submitting the same operation does not double-insert, double-charge, double-send, or double-advance state.
3. Completed, cancelled, and closed terminal states reject further illegal writes at the server.
4. Retry policy distinguishes retryable from non-retryable errors and preserves the failure reason.
5. Tests cover at least: first success, retry after failure, duplicate submission, and terminal-state rejection.
