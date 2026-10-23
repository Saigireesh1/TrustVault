# TrustVault setup

## Requirements
- Python 3.11+ (recommended)
- PostgreSQL 15+
- Git

## 1. Create a virtual environment

Windows PowerShell:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## 2. Create PostgreSQL database

Run in `psql` as a PostgreSQL administrator (choose a strong password):
```sql
CREATE USER trustvault_user WITH PASSWORD 'replace-with-a-strong-password';
CREATE DATABASE trustvault OWNER trustvault_user;
```
Set the same password in `.env`. Never commit `.env`.

## 3. Initialise and run

```bash
python manage.py check
python manage.py makemigrations accounts documents audit
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/ and sign in with the superuser. Set the role field for demo users through Django admin. For sample accounts, see the warning in `scripts/seed_demo.py` and run `python manage.py shell < scripts/seed_demo.py` (PowerShell: `Get-Content scripts/seed_demo.py | python manage.py shell`).

## 4. Run automated tests

```bash
python manage.py test accounts documents audit -v 2
```
The tests verify cross-user denial, explicit read/edit grants, immediate next-request revocation, search isolation and basic audit-chain integrity. Add tests before changing permission code.

## 5. Production checklist

- Set `DJANGO_DEBUG=False`, a cryptographically random `DJANGO_SECRET_KEY`, exact `DJANGO_ALLOWED_HOSTS`, and secure database credentials.
- Terminate HTTPS at a trusted host/proxy and verify `SECURE_SSL_REDIRECT` works with the platform's proxy configuration.
- Keep `private_uploads/` outside any public static directory. Never map `MEDIA_URL` to it. Use private object storage with authenticated delivery for multi-instance deployment.
- Configure backups, restore tests, file malware scanning, rate limiting, monitoring and an independent append-only audit sink.
- Create separate low-privilege database credentials for the application and restrict direct database access.
- Change/remove demo users and passwords before making the application public.
- Run `python manage.py check --deploy` and address every relevant warning.

## Important limitations
This is a hackathon starter, not a certified secure document system. File signature checks are basic and do not replace malware scanning. Hash chaining detects ordinary tampering but cannot prove integrity against an attacker who controls the database and can rewrite the whole chain. Use independently controlled, append-only audit storage and signed/externally anchored checkpoints for stronger evidence. A user can retain a file already downloaded; revocation prevents future app-mediated access, not copies already obtained. The local filesystem storage is not suitable for horizontally scaled production without private shared storage.
