# TrustVault architecture

## Permission policy
- Owner: may read, edit metadata, soft-delete, and grant/revoke access to their own documents.
- Viewer with `read`: may read metadata and download the file.
- User with `edit`: may read and edit metadata. Content replacement/version upload is not implemented yet.
- Administrator: may manage accounts and view global audit events, but does not automatically gain access to document contents.
- Unauthenticated or inactive users: no access.

All permission decisions are made by server-side functions in `documents/permissions.py`. List/search results are filtered in the database. Download re-checks current grant state before opening private storage.

## File storage
Files are stored under `private_uploads/` with random storage keys and no public URL route. Downloads are streamed through an authenticated view. This local filesystem approach is suitable for a single-instance demo; production multi-instance deployments should use private object storage and an authenticated proxy/download service.

## Audit
`audit/services.py` serializes appends through a locked chain-state row and computes SHA-256 hashes over canonical event payloads. The dashboard verifies the chain. Model-level update/delete is rejected. A database administrator can still rewrite the whole chain, so external immutable storage or signed checkpoints are required for strong non-repudiation.

## Revocation
The application queries the current `DocumentGrant` table during each protected request. Revoking a grant removes it from active permissions; the next request fails. It cannot erase files already downloaded or revoke a copy held outside TrustVault.
