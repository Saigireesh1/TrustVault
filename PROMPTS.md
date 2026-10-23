# TrustVault AI development log

Keep this file updated during the week. These are initial planning records, not claims that code review or verification has already passed. Add actual outputs, issues, test results and commit links as you work. Do not invent commit IDs.

## Entry 1 — 2026-10-21 — Permission model
**Prompt:** Design a Django document-level permission model with owner, read and edit grants, immediate revocation and per-request server-side checks.
**Output:** Initial plan uses an explicit `DocumentGrant` row and shared `can_read`/`can_edit` functions.
**Potential issue to verify:** A UI-only check or cached grant would permit direct-route access or stale access after revocation.
**Action:** Centralise policy in `documents/permissions.py`; detail/download routes invoke it.
**Verification:** Run `python manage.py test documents -v 2`; add direct-route tests and verify removing the check causes a test failure.
**Commit:** Add the real commit URL after committing this implementation.

## Entry 2 — 2026-10-21 — Download authorisation
**Prompt:** Review a Django download view for IDOR, public URL bypass and revoked grants.
**Output:** Download is served from private storage only after checking the current grant.
**Potential issue to verify:** A direct storage URL, or a long-lived signed URL, would bypass revocation.
**Action:** Store files outside static directories and stream via a POST-only authenticated view.
**Verification:** Attempt download as an ungranted user and after revocation; inspect production storage configuration.
**Commit:** Add the real commit URL after committing the fix.

## Entry 3 — 2026-10-21 — Audit integrity
**Prompt:** Propose an append-only audit trail with a verifiable hash chain and concurrency-safe sequence numbers.
**Output:** Hash-linked events plus a locked chain-state row and a verification function.
**Potential issue to verify:** A hash chain alone does not protect against an attacker who can rewrite the database and recompute every hash.
**Action:** Document this limitation; production design requires an independently controlled append-only sink or signed external checkpoints.
**Verification:** Run audit tests; modify a test event directly in a disposable database and confirm verification fails.
**Commit:** Add the real commit URL after committing the fix.

## Entry 4 — YYYY-MM-DD — Adversarial tests
**Prompt:** Generate tests for cross-user reads, read-versus-edit grants, revocation and search leakage.
**Output:** Test cases are in `documents/tests.py`.
**Potential issue to verify:** Tests must hit the actual endpoint; testing only a helper function would miss a view that forgot to call it.
**Action:** Keep both policy-unit tests and endpoint tests.
**Verification:** Remove a check in a disposable working tree and confirm the endpoint test fails.
**Commit:** Replace with actual date and commit URL.

## Entry 5 — YYYY-MM-DD — Upload validation
**Prompt:** Review upload validation for extension spoofing, path traversal and oversized files.
**Output:** Allowlist, basic file signatures, size cap and random storage keys.
**Potential issue to verify:** Signatures do not detect malware or all polyglot files.
**Action:** Document malware scanning as an accepted gap; test mismatched extension/content and file-size limits.
**Verification:** Record actual test results.
**Commit:** Replace with actual date and commit URL.

## Reusable project instructions
- Never treat hidden controls or random IDs as authorisation.
- Every file operation and metadata endpoint must enforce server-side access.
- No public media URLs or reusable links that outlive a permission grant.
- Audit denials as well as successes; never log secrets or document content.
- Treat AI-generated security code as untrusted until reviewed and tested.
- Never invent test outcomes, deployment URLs or commit links.
