# Base role and language guardrails

Confirmed October 17, 2026. This stage establishes access boundaries. Exam ownership,
review contributions, instructor compensation, subscription packaging and prices
remain later decisions.

| Role | Learning, chat, practice and mentor access | RAG training |
| --- | --- | --- |
| Admin | Every language currently present in the application catalogue/reference library | Allowed |
| Instructor | Explicit teaching assignments plus languages associated with their saved content uploads | Allowed, including a first upload in a new supported language |
| Student | Languages covered by active subscriptions; a cancelled subscription remains valid until its paid period ends | Denied |

Role privileges are read from the database on authenticated requests. A JWT does
not freeze a previous role. Suspended accounts cannot learn, train or administer content; their own account/profile access is preserved.
Peppercorn usage charges remain in force; a balance does not grant language access.
Expired subscriptions preserve the balance but deny learning in that language.
Multiple active per-language subscriptions represent the currently chosen set;
this does not introduce one-language/two-language commercial packages or checkout.

## Instructor scope

An administrator assigns teaching languages in **Admin → Teaching languages**.
`PUT /admin/users/{id}/languages` replaces the explicit assignment set. Students
cannot write assignments, and assignments are ignored after demotion.

A pending or published `/learn/train` upload contributes its explicit language,
or a safely inferred filename language for older uploads. Rejection, deletion
or replacement removes that source of access; an independent admin assignment
still applies. Existing publication and approval workflows continue to govern
which source text reaches learners. Unclassified uploads grant no language.

Saved problem-training submissions contribute only nonempty languages actually
supplied by their author, using the stored `supplied` input. Automatically generated
solutions do not grant the instructor access to additional languages. Failed
submissions grant no access. Global problem deletion requires an administrator.
The complete knowledge registry is available to admins and instructors. Instructor submission/document views remain
limited to their own material.

## Enforcement

A shared service authorizes chat, focused lessons, track content, progress,
problem statements, solution access/reveal, analysis, reflections, practice
session creation, session reads and session actions. Language authorization runs
before provider/execution work and before returning cached successful operation
receipts. Losing access therefore also blocks replaying an old paid response or
resuming an old practice session.

`GET /auth/me/access` supplies the account's allowed languages and training
capability. The interface filters language and reference selectors accordingly.
The server rejects crafted requests even if a client bypasses those selectors.
An account with no languages sees an empty access state and can still sign in,
view its profile/subscriptions and retain its existing peppercorn balance.

New conversations store their language, reference subject and track. Changing
scope requires a new conversation, preventing old history from being included
under a different allowed language. Non-admin thread lists/read endpoints are
restricted to currently allowed languages. Pre-migration conversations have no
reliable language scope: they are retained, visible to their owning admin where
applicable, and excluded from learner/instructor history until a future explicit
migration/classification policy is chosen. They cannot be reused as scoped chats.

Framework subjects currently follow their existing underlying language metadata.
This stage does not split mixed source documents into new framework subscriptions.
Reference access does not admit new executable workouts; the existing execution
verification gates remain necessary.

## Database and endpoints

Migration `0009_language_access` adds `instructor_languages` and conversation
scope columns. Run `alembic upgrade head` before starting the updated backend.
A local SQLite backup is made before applying the migration in this workspace.

- `GET /auth/me/access`: current role, languages, default language and training capability.
- `GET /admin/languages`: all supported language scopes, admin only.
- `GET /admin/users/{id}/languages`: effective and explicit assignments, admin only.
- `PUT /admin/users/{id}/languages`: replace an instructor's explicit teaching set.
- `/training/registry`, `/training/registry/history`, `/training/registry/technologies`: admins and instructors only.

## Verification scope

Regression coverage exercises all three roles, source-derived instructor access,
subscription expiry/cancellation, denied direct URLs, unchanged balances on denial,
thread isolation, receipt replay and saved-session access. Interface checks cover
filtered selectors, empty access and teaching assignments. Test importer history
is isolated in temporary storage so test runs cannot append to the application's
training log. No paid model calls are needed for these checks.

Verified in this workspace on October 17, 2026: 526 backend tests and 78 interface
tests passed. TypeScript checking, the frontend production build, the migration
upgrade/downgrade preservation test and the migration/model drift check passed.
The local database is at `0009_language_access`; a backup is retained under
`var/backups/before-language-access-20261017T165351Z.db`. Runtime lookups found 10
available admin language scopes. Existing students without active subscriptions
receive no learning languages. No subscription or teaching assignment was added
to real users to make verification pass.
