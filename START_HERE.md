# 🚀 DocuSage - Quick Start Guide

## ✅ What's Been Set Up

### Backend ✓
- ✅ All Python dependencies installed
- ✅ **SQLite database** configured (no PostgreSQL needed!)
- ✅ **Cerebras API key** configured in `.env`
- ✅ All endpoints ready (upload, process, analyze, trends)
- ✅ Automatic database fallback (PostgreSQL → SQLite)

### Frontend ✓
- ✅ Dashboard UI with file upload
- ✅ Landing page with randomized hero tiles
- ✅ Blue color palette matching design
- ✅ Hover effects and animations

---

## 🎯 How to Start Everything

### Step 1: Start Backend Server

Open a **PowerShell** terminal and run:

```powershell
cd c:\Users\krish\Desktop\Doc\backend
python start_server.py
```

**Backend will be available at:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs

**What's enabled:**
- ✅ File uploads (PDF, JPG, PNG)
- ✅ Document processing & OCR
- ✅ **AI Analysis** (Cerebras/Llama API configured!)
- ✅ SQLite database (auto-created)
- ✅ All CRUD operations

### Step 2: Start Frontend Server

Open a **NEW PowerShell** terminal and run:

```powershell
cd c:\Users\krish\Desktop\Doc\frontend
npm install  # Only needed first time
npm run dev
```

**Frontend will be available at:**
- http://localhost:5174

---

## 🧪 Test the Integration

1. **Open frontend:** http://localhost:5174
2. **Go to Dashboard** (click "Get Started")
3. **Upload a medical document** (PDF or image)
4. **Watch it process** (extraction → analysis → results)
5. **View analysis** in plain English!

---

## 📦 What's in the `.env` File

```env
# Cerebras API for AI analysis
CEREBRAS_API_KEY=csk-eeyjye8xdryhp9vvcwheyx555ry2jjhvxkwyvm4e8wvfth2x

# Database (SQLite is used automatically, no PostgreSQL needed)
DATABASE_URL=postgresql://docusage:password@localhost:5432/docusage
```

---

## 🗄️ Database: SQLite vs PostgreSQL

**Currently using: SQLite** (Simple, no installation needed!)

### SQLite (Current Setup) ✅
- **File:** `backend/docusage.db` (auto-created)
- **Pros:** No installation, easy setup, portable
- **Cons:** Single-user, basic features
- **Perfect for:** Development, testing, demos

### PostgreSQL (Optional Upgrade)
If you need multi-user support or advanced features later:

```powershell
# Install PostgreSQL from: https://www.postgresql.org/download/windows/
# OR start Docker container:
docker-compose up -d db

# Initialize database:
cd backend
python -c "import asyncio; from database.db import Database; asyncio.run(Database().init_tables())"
```

The backend will automatically use PostgreSQL if available!

---

## 🔧 Troubleshooting

### Backend won't start
```powershell
# Make sure you're in the backend directory:
cd c:\Users\krish\Desktop\Doc\backend

# Check if port 8000 is available:
netstat -ano | findstr :8000

# If something is using it, kill it:
taskkill /PID <PID> /F
```

### Frontend won't start
```powershell
# Make sure you're in the frontend directory:
cd c:\Users\krish\Desktop\Doc\frontend

# Clean install:
rm -r node_modules
npm install
npm run dev
```

### "Module not found" errors
```powershell
# Backend:
cd backend
pip install -r requirements.txt

# Frontend:
cd frontend
npm install
```

### API returns errors
- Check backend terminal for error messages
- Visit http://localhost:8000/docs to test endpoints
- Make sure `.env` file exists in `backend/` folder

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/upload` | POST | Upload document |
| `/api/document/{id}/process` | POST | Process document |
| `/api/document/{id}/analysis` | GET | Get analysis |
| `/api/documents` | GET | List all documents |
| `/api/document/{id}` | DELETE | Delete document |
| `/api/document/{id}/trends` | GET | Get trends |

**Test them at:** http://localhost:8000/docs

---

## 🎨 Features

### Backend
- ✅ PDF & image text extraction
- ✅ OCR for scanned documents
- ✅ AI-powered medical jargon translation
- ✅ Document classification
- ✅ Trend analysis over time
- ✅ Question generation for doctor visits

### Frontend
- ✅ Beautiful dashboard UI
- ✅ Drag & drop file upload
- ✅ Real-time processing status
- ✅ Stat cards with animations
- ✅ Randomized hero section
- ✅ Responsive design

---

## 📝 Next Steps

1. **Start both servers** (backend + frontend)
2. **Upload a test document** (any medical PDF or lab report image)
3. **Explore the analysis** (plain English translations!)
4. **Check the trends** (if you upload multiple reports)

**Have fun building! 🎉**

---

## 💡 Pro Tips

- Backend auto-reloads when you edit code
- Frontend auto-reloads when you edit React files
- Database file is at: `backend/docusage.db`
- All uploads saved to: `backend/uploads/`
- Check `backend/README.md` for detailed API docs

---

**Questions or issues?** Check the terminal output for detailed error messages!
