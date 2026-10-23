# API and route access policy

TrustVault currently uses Django server-rendered routes rather than a separate REST API. All state-changing forms use POST and CSRF protection.

| Method | Route | Policy |
|---|---|---|
| GET/POST | `/accounts/login/` | Public login; Django authentication |
| POST | `/accounts/logout/` | Authenticated session |
| GET/POST | `/` | Authenticated; search returns only owned or explicitly granted documents; upload restricted to owner/admin role |
| GET | `/documents/<uuid>/` | Owner or active explicit read/edit grant |
| POST | `/documents/<uuid>/download/` | Owner or active explicit read/edit grant; permission checked on every request |
| GET/POST | `/documents/<uuid>/edit/` | Owner or active edit grant |
| POST | `/documents/<uuid>/delete/` | Owner only; soft delete |
| POST | `/documents/<uuid>/grants/` | Owner only |
| POST | `/documents/<uuid>/grants/<user_id>/revoke/` | Owner only |
| GET | `/audit/` | Active TrustVault administrator or superuser; global audit feed |
| `/admin/` | Django administration | Django staff/superuser authentication; audit events are read-only in admin |

Document access is not inherited from the Administrator role. An admin must have an explicit grant to read file content. Production deployments should add throttling, an independent audit sink, and API-level request correlation IDs.
