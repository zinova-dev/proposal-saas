# Proposal SaaS

A web app for freelancers to build commercial proposals and export them as PDF. I built it as a portfolio project to cover a full request cycle: authentication, relational data, business rules, document generation, and deployment.

- Live demo: https://proposal-saas-lovat.vercel.app
- API docs: https://proposal-saas-api.onrender.com/api/docs

The API runs on a free Render instance that sleeps when idle, so the first request after a pause can take up to a minute.

## What it does

Users register, log in, and manage their own proposals. Each proposal has line items and a tax rate. The server calculates subtotal, tax, and total, and can export the proposal as a PDF.

## Stack

Django 5 and Django Ninja on the backend, PostgreSQL in production, Next.js 16 with TypeScript and Tailwind CSS on the frontend, WeasyPrint for PDFs. Frontend is deployed on Vercel, backend and database on Render.

## Design notes

The data is relational and mostly CRUD, so I used Django for the ORM, migrations, and admin, with Ninja for typed schemas and generated API docs. FastAPI's async advantages would not have mattered here.

PDFs are rendered on the server from an HTML template, so the output does not depend on the user's browser. For long proposals the table header repeats on every page and rows are not split across pages.

Totals are calculated in the backend from the line items. The frontend only displays them.

Every proposal query is filtered by the authenticated user, and requesting someone else's proposal returns 404.

## Known limitations

- The JWT is kept in `localStorage`. An httpOnly cookie would be safer.
- The PDF endpoint accepts the token as a query parameter, because a browser download cannot send custom headers. A short-lived signed URL would be better.
- Clients are created automatically as a default client. There is no client management screen yet.
- Proposal status is stored but cannot be changed from the UI yet.

## Running locally

Backend:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

WeasyPrint needs the Pango system libraries. See its [installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html).

Frontend:

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api" > .env.local
npm run dev
```

Environment variables: `SECRET_KEY`, `DEBUG`, and `DATABASE_URL` for the backend (SQLite is used when `DATABASE_URL` is not set), and `NEXT_PUBLIC_API_URL` for the frontend.
