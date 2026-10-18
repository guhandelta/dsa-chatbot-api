# Admin workspace

`/admin` is restricted to the current server-confirmed admin role. The frontend
waits for session restoration before requesting administrative data. Every new
endpoint also requires an active admin on the server. Train and Registry retain
their existing admin/instructor access.

## Views

- Overview: measured account/access counts, review queues, operation failures,
  ledger integrity, credit movement and recorded learning events.
- People & access: server-filtered, paginated accounts; effective access;
  entitlement source/expiry; role changes; suspension/reinstatement; teaching
  assignments and manual language grants.
- Content & reviews: paginated document queues, escaped extracted previews,
  approval/rejection/withdrawal with review notes; problem-validation reports;
  recorded readiness evidence. Problem publication cannot bypass validation.
- Peppercorns: student search, gift review/confirmation, ledger with pagination,
  and current balance reconciliation.
- Operations & safety: loaded source fingerprint/time, schema revision, database
  reachability, execution configuration, recovery counts, operation receipts,
  security events and recent trace details.
- AI quality & usage: actual provider/model metadata from completed chat receipts,
  measured trace latency/tokens/estimated cost, and recorded evaluation evidence.
- Audit & configuration: actor/target/time, reasons and before/after state for
  supported administrative changes; read-only routing and execution settings.

## Student peppercorn gifts

Select **Peppercorns**, find a student by email, choose the account, enter an
integer amount and reason, review the recipient/amount, and confirm the gift.
Account management also links directly to the selected student's gift panel.

`POST /admin/users/{id}/gifts` takes JSON `{amount, reason}` and requires an
`Idempotency-Key`. Amounts must be integers from 1 to 1,000,000; a trimmed reason
must contain 3–80 characters. Only student recipients qualify. A suspended
student can receive credits but still cannot spend them while suspended.

The existing durable operation protocol protects duplicates and transport retries.
One transaction writes the atomic credit, append-only ledger entry, audit event,
and successful receipt. If that transaction fails, the credit is rolled back.
Changed input using an existing key is rejected. Gifts do not debit the admin,
charge the student, purchase languages, or modify subscriptions. The UI retains
the reviewed request after an uncertain transport result; its shared receipt
helper retains the same key in session storage for an identical retry.

Manual language grants are a separate action and use their own request receipts.
They create/extend manual entitlements without changing provider-managed
subscription expiry, cancellation state, or payment records.

## Honest measurement boundaries

- Activity, operation failures and credit movements use the selected 7/30/90-day
  window. Current roles, access, queues, ledger reconciliation and recovery counts
  are current-state measurements, not historical snapshots.
- Active students means current student accounts with a completed tracked learning
  operation in the period. Entitled students are distinct active student accounts
  with an unexpired active/cancelled language entitlement, including manual grants.
  Neither number is labelled paying customers or revenue.
- Learning events can include repeated attempts/solves. They do not establish
  distinct mastery or a learning-outcome score.
- Usage/latency samples contain at most 1,000 persisted traces in the period;
  instrumentation currently covers mentor/analysis rather than all provider calls.
  Costs use the existing approximate rate table, including fallback rates for
  unknown models. They are not provider invoices or total application spend.
- Routing aggregates sample the latest 1,000 completed chat receipts. Older or
  failed operations may lack routing metadata. Completion does not certify quality.
- Runtime configuration does not perform a paid model probe or certify execution
  isolation. Provider key values, passwords and tokens are not returned.
- Readiness files are historical audit evidence. File modification time is not
  necessarily evaluation time, and record counts do not certify teaching quality.
- Housekeeping's latest successful pass and backup freshness are not monitored.
  Those values are explicitly marked unmeasured. No automatic readiness or revenue
  claim is inferred from missing data.
- Audit history begins with this feature; prior changes are not backfilled.

## Migration and startup

Back up the database and run `alembic upgrade head` before restarting the API.
Migration `0010_admin_audit` adds one table and indexes; existing ledger,
subscription, approval and learning records are preserved. Use
`.venv/bin/uvicorn app.main:app --reload --port 8000` for local development.

Production execution, backup scheduling, full AI telemetry and representative
human quality evaluation remain operational work; the dashboard reports their
available evidence rather than manufacturing successful states.
