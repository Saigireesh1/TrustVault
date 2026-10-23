# TrustVault

Secure document sharing with per-document permissions, private file storage, and a tamper-evident audit trail.

> Hackathon starter implementation. Not a certified secure document platform. Read `THREATS.md` and `docs/SETUP.md` before deployment.

## Stack
- Python / Django
- PostgreSQL
- Django templates + Bootstrap
- Django TestCase

## Features in this build
- Role-aware users: Administrator, Document Owner, Viewer
- Per-document `read` and `edit` grants
- Server-side checks on detail, download, edit, delete, grant and revoke
- Private filesystem storage with random storage keys
- Search by title, filename, category, owner and date
- Basic upload validation and SHA-256 content checksum
- Audit events for uploads, reads, downloads, edits, deletes, grants, revokes and denied actions
- Hash-chain audit verification dashboard
- Soft-delete metadata
- Automated cross-user access and audit tests

## Quick start
Follow [`docs/SETUP.md`](docs/SETUP.md). In short:
```bash
python -m venv .venv
# Activate it, then:
pip install -r requirements.txt
cp .env.example .env  # Windows: Copy-Item .env.example .env
# Configure PostgreSQL credentials in .env
python manage.py makemigrations accounts documents audit
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Demo accounts
Do not publish default demo passwords. Create your own local accounts or run `scripts/seed_demo.py` only for a disposable demo, then change the password and remove unused accounts before deployment. Live credentials must be set in the deployed environment and shared deliberately with judges.

## Tests
```bash
python manage.py test accounts documents audit -v 2
```

## Submission items to finish
- Add real commit history throughout development.
- Fill `PROMPTS.md` with real review outcomes and actual commit links.
- Update `THREATS.md` with test evidence and accepted risks.
- Deploy with HTTPS, private object storage and an independent audit sink.
- Add a real live URL and judge credentials only after deployment.
- Record the five-minute demo and write-up.

## Known limitations
- File version replacement/recovery UI is not implemented despite a model scaffold.
- Basic signature validation is not malware scanning.
- Audit chain is not externally anchored; a database administrator could rewrite it.
- Rate limiting, MFA, malware scanning, backup/restore, and an independent append-only audit sink are not implemented.
- Revocation blocks future requests; it cannot retrieve already-downloaded files.
- Local filesystem storage is single-instance only.
