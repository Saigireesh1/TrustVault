# TrustVault threat model

This document is a living record. Change each status only after running the stated test against the current commit and deployed environment.

| Threat | Mitigation | Verification | Status / accepted risk |
|---|---|---|---|
| IDOR: guess another document UUID | Server-side policy on detail/download/edit/delete/grant routes | Cross-user endpoint tests | Implemented; run tests |
| Search metadata leakage | Queryset scoped to owner or explicit grant before filtering | Search isolation test | Implemented; run tests |
| Stale access after revocation | Current grant queried on each request; no reusable public URL | Revoke then repeat download | Implemented for next request; in-flight response cannot be recalled |
| Public file URL bypass | Private local storage, no public media route | Attempt direct URL access | Implemented locally; verify host configuration |
| Read-to-edit escalation | Separate read/edit permission checks | Read grant cannot edit test | Implemented; run tests |
| Viewer grants access | Owner check on grant/revoke routes | Forged POST as viewer | Implemented; run tests |
| Upload extension spoofing | Small allowlist, signature check, size cap | Test mismatched signatures and oversized file | Basic checks only; malware scanning is accepted gap |
| Filename/path traversal | Server-generated random storage key and basename on download | Upload names with path separators | Implemented; test on target OS |
| CSRF on state-changing forms | Django CSRF middleware and POST-only mutation views | Missing-token POST test | Framework protection enabled; test deployment |
| Audit row edited/deleted via app model | Model-level immutability and read-only admin | Audit model tests | Implemented at application layer only |
| Entire audit chain rewritten by DB administrator | Hash chain verification | Tamper event and verify failure | Accepted limitation; add external immutable sink/checkpoints |
| Compromised admin account | Admin cannot read content without explicit grant | Admin-without-grant test | Policy implemented; account compromise remains risk |
| Session stolen | Django sessions, HTTPS secure cookies in production | Deployment configuration review | Secure cookie settings conditional on DEBUG=False; MFA not implemented |
| Brute-force login | Django password validators | Load/security test | Rate limiting not implemented; accepted hackathon gap |
| Malware or polyglot file | Signature checks and allowlist | Malformed upload tests | No malware scanner; accepted gap |
| Storage loss or accidental deletion | Soft-delete metadata | Recovery drill | File backup/restore not implemented; accepted gap |
| Concurrency between revoke and download | Check grant at request boundary | Concurrent request test | In-flight downloads already authorised may complete; accepted limitation |
| Audit event spoofing through details | Server controls event fields; avoid sensitive data in details | Forged form fields and log review | Application routes do not accept arbitrary audit payloads |
| Secret leakage | `.env` ignored by Git; `.env.example` only | Scan repo before publishing | Developer must verify Git history and deployment secrets |

## Test policy
Security tests must assert the response or data boundary, not just that a button is hidden. At minimum test direct detail, download, edit, delete, grant, revoke and search routes as a different user. If an authorisation check is removed, the relevant test should fail. Run tests against a clean database before each release.
