# PostgreSQL Setup Guide (Without Docker)

## Option 1: Install PostgreSQL on Windows (Recommended)

### Download and Install
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer (choose version 15 or newer)
3. During installation:
   - Set password: `password` (or remember your own)
   - Port: `5432` (default)
   - Install pgAdmin (optional GUI tool)

### Create Database
After installation, open PowerShell and run:

```powershell
# Login to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE docusage;
CREATE USER docusage WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE docusage TO docusage;
\q
```

### Update Connection String
Your `.env` file is already configured:
```
DATABASE_URL=postgresql://docusage:password@localhost:5432/docusage
```

## Option 2: Use SQLite (Simpler Alternative)

For development/testing without PostgreSQL, we can use SQLite instead.

Let me know which option you prefer!

---

## Quick SQLite Setup (No Installation Needed)

If you want to skip PostgreSQL entirely for now, I can modify the backend to use SQLite instead, which requires no installation and just creates a local file.

