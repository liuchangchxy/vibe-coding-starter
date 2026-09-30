# Data Safety and Migration Extension

Enable only for database migrations, bulk imports, file conversions, cross-system sync, or other irreversible operations. This is not a default gate for every project.

<p align="center"><a href="DATA_SAFETY.md">English</a> · <a href="DATA_SAFETY.zh-CN.md">简体中文</a></p>

## Before
- Name the source, the target, and the recovery path.
- The source is read-only by default; never overwrite or delete it without explicit authorization.
- Create a verifiable backup or snapshot of the target.
- Record the expected entity counts and key constraints.

## During
- Bulk writes use clear transaction boundaries.
- A mid-way failure must roll back; never leave half a batch or orphaned records.
- Unconvertible content goes to an explicit `unconverted` / exception report.
- Retries must not double-write or double-count.

## After
- Physically reconcile source, target, counts, key relations, and exceptions.
- Physically verify the recovery path, not just that a command returned success.
- Report success, failure, skipped, and unconverted counts.
