# 🚀 VITALCORE — Vercel Deployable Version

This folder is a **drop-in deployable copy** of VITALCORE built for Vercel Functions (serverless).

The only change from the local version: `database.py` no longer uses **SQLite**
(SQLite files can't persist writes on Vercel — the filesystem is read-only except `/tmp`).
Instead it stores all data in a lightweight JSON store written to `/tmp`.

Everything else is identical — all **13 features** work exactly the same.

---

## ⚠️ Important: Data Lifetime

Serverless "instances" are temporary. `/tmp` is wiped whenever a Vercel Function
**cold-starts** (after ~a few minutes of inactivity during a demo).

- Data you enter **survives between requests while the instance is warm** (e.g. during an active demo session).
- Data **resets** when the instance cold-starts.

**For your interview demo:** add your data right at the start of the demo
(register a patient, book an appointment, log a medicine, pour some water —
it looks great) and present immediately. Don't pre-seed it the night before.

> Upgrade path if you want permanent data later: connect a free **Neon** or
> **Vercel Postgres** database and rewrite `database.py` to use `psycopg` +
> `DATABASE_URL`. This version is intentionally 100% self-contained (zero setup,
> zero accounts) so it deploys in ~2 minutes.

---

## 🧪 Test locally first

Run it exactly like the original — it will use a JSON file in your OS temp dir:

```bash
cd deploy-vercel
pip install -r requirements.txt
python app.py
# -> http://localhost:5001
```

---

## 🌐 Deploy to Vercel

Vercel auto-detects Flask apps: it reads `requirements.txt`, finds the `app` in
`app.py`, and serves every request through one Function. **No build command
needed.**

### Option A — Vercel CLI (fastest)

```bash
npm i -g vercel
cd deploy-vercel
vercel            # first deploy (preview)
vercel --prod     # production URL
```

### Option B — Dashboard (no CLI)

1. Go to https://vercel.com/new
2. Import the project, or drag-and-drop / upload this `deploy-vercel` folder.
3. Framework preset: **Other** (or let it auto-detect Python/Flask)
4. Build Command: *(leave empty)* — Output Directory: *(leave empty)*
5. Hit **Deploy**.

The app works with no environment variables. The `vercel.json` file just keeps
the function bundle lean (excludes `__pycache__`/`instance`).

---

## 📦 What's inside

```
deploy-vercel/
├── app.py              # Flask routes (all 13 features) — init_db() at import
├── database.py         # Serverless JSON store in /tmp (no SQLite)
├── requirements.txt    # flask==3.0.0
├── vercel.json         # Lean function bundle config
├── README-VERCEL.md
└── templates/          # All 15 templates (identical to original)
```