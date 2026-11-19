# Proposal SaaS

A full-stack web application that helps freelancers create, manage, and export professional commercial proposals.

**Live Demo:** https://proposal-saas-lovat.vercel.app
**API Docs:** https://proposal-saas-api.onrender.com/api/docs

> The API runs on a free Render instance that sleeps after 15 minutes of inactivity. The first request may take up to 50 seconds to respond.

**Tech Stack:** Django 5 · Django Ninja · PostgreSQL · Next.js 16 · TypeScript · Tailwind CSS · WeasyPrint

The Problem

Freelancers spend hours formatting proposals in Word or Google Docs. This tool lets a user enter the scope of work, calculates subtotals and taxes, and generates a clean PDF ready to send to a client.

Features

- Account registration and login with JWT authentication
- Per-user data isolation: every query is scoped to the authenticated user
- Create, list, and delete proposals with multiple line items
- Configurable tax rate per proposal, with totals calculated on the server
- Server-side PDF export with multi-page support (repeating table headers, page numbering)
- Interactive API documentation generated from typed schemas

Engineering Decisions

- **Django Ninja over FastAPI.** The domain is relational (users, clients, proposals, line items) and CRUD-heavy, so Django's ORM, migrations, and admin were a better fit than async throughput. Ninja adds typed request and response schemas and OpenAPI docs on top.
- **Server-side PDF generation with WeasyPrint.** Rendering an HTML template on the server produces identical output on every device and avoids browser print inconsistencies. CSS paged-media rules keep table rows intact and repeat the header on each page.
- **Totals computed in the backend.** Subtotal, tax, and total are derived from line items on the model, so the API is the single source of truth for monetary values.
- **Ownership enforced at the query level.** Endpoints filter by the authenticated user, and requests for another user's proposal return 404 instead of leaking its existence.
- **Typed forms with schema validation.** React Hook Form with Zod validates input on the client, while Pydantic schemas validate it again on the server.
- **PostgreSQL in production, SQLite locally.** The database is selected through `DATABASE_URL`, which keeps local setup simple and production realistic.
- **Pinned runtime.** Python 3.12 is pinned for deployment, and Gunicorn runs a single worker to fit the memory limits of the free tier.

Known Limitations

- The access token is stored in `localStorage`. An httpOnly cookie would reduce exposure to XSS.
- PDF downloads pass the token as a query parameter because browser-initiated downloads cannot set headers. A short-lived signed download URL would be safer.
- Clients are created automatically as a default client. A dedicated client management screen is planned.
- Proposal status (Draft, Sent, Accepted, Declined) is stored but cannot yet be changed from the UI.

Project Structure

proposal-saas/
├── backend/     Django project (API, models, PDF template)
├── frontend/    Next.js application
└── render.yaml  Render blueprint (API and database)
```

Local Setup

Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

WeasyPrint requires system libraries (Pango). See the [WeasyPrint installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html) for your platform.

Frontend

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api" > .env.local
npm run dev
```

The API is served at `http://127.0.0.1:8000/api/docs` and the app at `http://localhost:3000`.

Environment Variables

| Variable | Where | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | backend | Django secret and JWT signing key |
| `DEBUG` | backend | Enables debug mode (`True` / `False`) |
| `DATABASE_URL` | backend | PostgreSQL connection string (SQLite if unset) |
| `NEXT_PUBLIC_API_URL` | frontend | Base URL of the API |
