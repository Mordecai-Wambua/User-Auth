User-Auth – Django JWT auth with social login (Google) and API docs

Overview
This repository contains a production‑ready Django REST backend focused on user authentication. It uses:
- Django 5.2 with a custom email‑only user model
- DRF Auth Kit for JWT authentication via secure HTTP‑only cookies
- django‑allauth for account management and Google OAuth2 social login
- drf‑spectacular for OpenAPI schema and Swagger/Redoc UI
- CORS/CSRF hardening, email via Resend (production) or console (local)

You can run it locally with Python, with Docker, or deploy it to Google Cloud Run (Cloud Build configuration included).


Key features
- Email‑only user model (no username); soft‑delete behavior
- JWT auth with refresh rotation, cookies configured per environment
- Signup, login, logout, email verification, password reset flows powered by DRF Auth Kit and Allauth
- Google social login (authorization code flow)
- Auto‑generated API docs (OpenAPI schema, Swagger UI, Redoc)
- CORS/CSRF configuration via environment variables
- Production‑minded settings, including secure cookies and Resend email backend


Tech stack
- Python 3.13+ for local development (Docker image uses Python 3.12)
- Django 5.2, DRF Auth Kit, django‑allauth, drf‑spectacular
- PostgreSQL (via dj‑database‑url). SQLite can be used for quick local trials
- Gunicorn for production server in Docker/Cloud Run


Project structure
```
User-Auth/
├─ User_Auth/                 # Django project
│  ├─ settings.py             # Env‑driven settings (JWT, CORS, Allauth, email, etc.)
│  ├─ urls.py                 # Routes: auth kit, social, API docs
│  ├─ asgi.py, wsgi.py
├─ accounts/                  # Custom user app
│  ├─ models.py               # CustomUser, managers, soft delete
│  ├─ migrations/
├─ manage.py
├─ pyproject.toml             # Python deps
├─ Dockerfile                 # Production image with uv and gunicorn
├─ docker-compose.yml         # Simple local container run
├─ cloudbuild.yaml            # GCP Cloud Build + Cloud Run deployment steps
└─ uv.lock                    # Locked dependency graph for uv
```


Getting started (local, without Docker)
Prerequisites
- Python 3.13+
- PostgreSQL (recommended) or use SQLite for quick trial

1) Clone and enter the project
- git clone <repo-url>
- cd User-Auth

2) Create and activate a virtual environment
- python -m venv .venv
- On Windows: .venv\Scripts\activate
- On macOS/Linux: source .venv/bin/activate

3) Install dependencies
- pip install -U pip
- pip install -r <(uv export)  [Optional: if you use uv locally]
- OR simply: pip install -e .
  Note: pyproject.toml defines the dependencies. If pip complains, install packages listed there manually.

4) Create and fill .env
Copy these variables into a .env in the project root and adjust values:
- SECRET_KEY=your-secret-key
- DEBUG=true
- DATABASE_URL=sqlite:///db.sqlite3
- ALLOWED_HOSTS=localhost,127.0.0.1
- CORS_ALLOWED_ORIGINS=http://localhost:3000
- CSRF_TRUSTED_ORIGINS=http://localhost:3000
- FRONTEND_URL=http://localhost:3000
- CALLBACK=http://127.0.0.1:3000/login
- GOOGLE_CLIENT_ID=your-google-client-id  (needed for Google login)
- GOOGLE_CLIENT_SECRET=your-google-client-secret
- RESEND_API_KEY=your-resend-key  (enables real emails in production)
- DEFAULT_FROM_EMAIL=noreply@your-domain.com     (used if RESEND is enabled)

Notes
- When DEBUG=false, settings treat the environment as production: secure cookies, etc. Make sure ALLOWED_HOSTS is set.
- If DATABASE_URL points to Postgres, ensure the database exists and is accessible.

5) Apply migrations and create a superuser
- python manage.py migrate
- python manage.py createsuperuser --email admin@example.com

6) Run the server
- python manage.py runserver 8000
Visit http://127.0.0.1:8000/api/docs/ for Swagger UI.


Environment variables reference
(all read in User_Auth/settings.py via django‑environ)
- SECRET_KEY: Required secret. Never commit to VCS.
- DEBUG: true/false; production is when DEBUG=false.
- DATABASE_URL: e.g., sqlite:///db.sqlite3 or postgres://user:pass@host:5432/db
- ALLOWED_HOSTS: Comma‑separated list for production, e.g., api.example.com
- CORS_ALLOWED_ORIGINS: Comma‑separated origins allowed by CORS
- CSRF_TRUSTED_ORIGINS: Comma‑separated list of trusted origins
- FRONTEND_URL: Base URL used to build email verification/reset links
- CALLBACK: Social login callback base URL (frontend path)
- GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET: Google OAuth credentials
- RESEND_API_KEY: Enables Anymail Resend backend if present; otherwise console backend is used
- DEFAULT_FROM_EMAIL: From email address (used with Resend)
- PORT: Container/server port; Dockerfile defaults to 8080 (Cloud Run will inject PORT)


Authentication and API routes
Core URL configuration is in User_Auth/urls.py.
- Admin:               /admin/
- Auth Kit (JWT):      /api/auth/           (multiple endpoints: register, login, logout, token refresh, email verify, password reset, etc.)
- Social auth:         /api/auth/social/    (Google OAuth endpoints)
- OpenAPI schema:      /api/schema/
- Swagger UI:          /api/docs/
- Redoc:               /api/redoc/

Notes on auth
- JWTs are managed by DRF Auth Kit with secure HTTP‑only cookies when USE_AUTH_COOKIE is true.
- Access token lifetime: 30 minutes; refresh token lifetime: 7 days; refresh rotation enabled.
- Email verification is mandatory (ACCOUNT_EMAIL_VERIFICATION="mandatory").
- Social login type is set to authorization code flow.


Custom user model
Defined in accounts/models.py:
- CustomUser extends AbstractUser, removes username, uses unique email as USERNAME_FIELD.
- REQUIRED_FIELDS include first_name and last_name.
- delete() is overridden to perform soft‑delete (sets is_active=False).


API documentation
Visit Swagger UI at /api/docs/ and Redoc at /api/redoc/.
OpenAPI schema is served at /api/schema/ (used by tools/clients).


Running with Docker
Build the image:
- docker build -t user-auth .

Run with environment file (.env.prod suggested):
- docker run --rm -p 8000:8080 --env-file .env.prod user-auth

Important
- The container runs Gunicorn and binds to the PORT environment variable (defaults to 8080).
- Map host port 8000 to container port 8080 (or set PORT=8000 inside the container and map 8000:8000).


docker-compose
docker-compose.yml provides a simple service named web.
By default it maps host 8000 to container 8000, but the Dockerfile binds to ${PORT} (8080 by default). Choose one of the following:
1) Update your .env.prod to include PORT=8000, keep ports: "8000:8000".
2) Or change the compose ports to "8000:8080" to match the default.

Example compose usage:
- docker compose up --build
- Navigate to http://localhost:8000/api/docs/


Deployment on Google Cloud Run (via Cloud Build)
This repository includes cloudbuild.yaml to:
1) Build and push the container image to Artifact Registry.
2) Run database migrations via a Cloud Run Job (django-migrate-job) before deployment.
3) Deploy the service (django-backend-service) to Cloud Run with Cloud SQL instance attached.

You must pre‑provision and configure:
- Artifact Registry repository and appropriate _PROJECT_ID/_REGION substitutions.
- A Cloud Run Job named django-migrate-job (one‑time creation) with permissions and network access.
- Cloud SQL instance and secrets (DB_PASSWORD) referenced in cloudbuild.yaml.
- Service account with required roles to run jobs, access secrets, and deploy.


Email delivery
- If RESEND_API_KEY is present, anymail.backends.resend is used in production; DEFAULT_FROM_EMAIL should be a verified domain/sender.
- In local development without RESEND_API_KEY, Django’s console email backend is used (emails print to console).


Troubleshooting
- 403 CSRF failures during login: ensure CORS_ALLOWED_ORIGINS and CSRF_TRUSTED_ORIGINS include your frontend origin, and cookies aren’t blocked by the browser (check SameSite and HTTPS in production).
- 400/401 auth issues: verify cookies are set; check DOMAIN/ALLOWED_HOSTS and that DEBUG/IS_PRODUCTION derived settings match your environment.
- Social login failing: confirm CALLBACK, FRONTEND_URL, and Google OAuth credentials; ensure the Google OAuth consent screen and redirect URIs are configured.
- Emails not sent: without RESEND_API_KEY, emails go to console. In production, set and verify RESEND_API_KEY and DEFAULT_FROM_EMAIL.


License
This project is provided as‑is for educational and demonstration purposes. Add your preferred license file if you intend to distribute.
