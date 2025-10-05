# 🏥 Patiently - AI-Powered Medical Document Analyzer

[![Deploy to GitHub Pages](https://github.com/Dev-KrishnaPathak/Patiently/actions/workflows/deploy.yml/badge.svg)](https://github.com/Dev-KrishnaPathak/Patiently/actions/workflows/deploy.yml)

> Transform complex medical reports into clear, understandable insights using AI.

**Live Demo**: https://dev-krishnapathak.github.io/Patiently/

---

## ✨ Features

- 🔍 **Smart Document Analysis** - Upload PDF/image medical reports
- 🤖 **AI-Powered Insights** - Llama 3.1-8b analyzes your results
- 📊 **Visual Health Trends** - Interactive bar graphs with color-coded status
- 💬 **Doctor Questions** - AI generates personalized questions based on your results
- 🎯 **Borderline Detection** - Smart classification of values at risk boundaries
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

---

## 🚀 Quick Start

### Frontend (GitHub Pages)

The frontend is automatically deployed to GitHub Pages on every push to `main`.

**Visit**: https://dev-krishnapathak.github.io/Patiently/

### Backend (Local Development)

1. **Install Python dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   # Create .env file
   CEREBRAS_API_KEY=your_api_key_here
   ```

3. **Start the backend server**:
   ```bash
   # Windows
   START_BACKEND.bat
   
   # Or manually
   cd backend
   python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```

4. **Backend API**: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## 🛠️ Tech Stack

### Frontend
- **React 19** - UI library
- **Vite** - Build tool
- **React Router** - Client-side routing
- **Recharts** - Data visualization
- **Lucide Icons** - Icon library
- **Tailwind CSS** - Styling

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.13** - Programming language
- **SQLite** - Database (production: PostgreSQL)
- **Cerebras API** - Llama 3.1-8b LLM
- **PyPDF2 / pdfplumber** - PDF processing
- **Tesseract OCR** - Image text extraction

---

## 📁 Project Structure

```
Patiently/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Pages deployment
├── backend/
│   ├── database/              # Database layer
│   ├── models/                # Pydantic schemas
│   ├── services/              # Business logic
│   │   ├── document_processor.py
│   │   └── llama_analyzer.py
│   ├── uploads/               # User uploads (ignored)
│   ├── main.py               # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/           # Page components
│   │   ├── App.jsx          # Main app with routing
│   │   └── main.jsx         # Entry point
│   ├── public/              # Static assets
│   ├── index.html
│   ├── package.json
│   └── vite.config.js       # Vite configuration
├── .gitignore
└── README.md
```

---

## 🔧 Development

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:5173

### Backend Development

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Visit: http://localhost:8000

---

## 🌐 Deployment

### GitHub Pages (Frontend)

The frontend is automatically deployed via GitHub Actions:

1. Push to `main` branch
2. GitHub Actions builds the frontend
3. Deploys to GitHub Pages
4. Available at: https://dev-krishnapathak.github.io/Patiently/

### Backend Deployment Options

#### Option 1: Railway / Render / Fly.io
- Deploy FastAPI backend to cloud platform
- Set environment variables (CEREBRAS_API_KEY)
- Update frontend API_BASE_URL

#### Option 2: Docker
```bash
docker-compose up -d
```

#### Option 3: Traditional Hosting
- Install Python 3.13+
- Install dependencies: `pip install -r requirements.txt`
- Set environment variables
- Run: `uvicorn main:app --host 0.0.0.0 --port 8000`

---

## 🔐 Environment Variables

### Backend (.env)

```env
CEREBRAS_API_KEY=your_cerebras_api_key
DATABASE_URL=sqlite:///./docusage.db  # or PostgreSQL URL
```

### Frontend

Update `API_BASE_URL` in `Dashboard.jsx`:
```javascript
const API_BASE_URL = 'https://your-backend-url.com/api';
```

---

## 📊 How It Works

1. **Upload**: User uploads medical report (PDF/Image)
2. **Extract**: Backend extracts text using PDF parser or OCR
3. **Analyze**: Llama 3.1-8b AI analyzes test results
4. **Classify**: Smart borderline detection (NORMAL/MONITOR/URGENT)
5. **Visualize**: Frontend displays results with bar graphs
6. **Guide**: AI generates personalized doctor questions

---

## 🎯 Key Features

### Smart Borderline Detection
- Values within **5-10% of limits** → URGENT
- Values within **10-20% of limits** → MONITOR
- Values **>20% from limits** → NORMAL

Example:
- B12 at 210 pg/mL (range: 200-900) → **URGENT** (borderline low)
- B12 at 500 pg/mL (range: 200-900) → **NORMAL** (optimal)

### AI-Generated Questions
```
"My Vitamin D is 18 ng/mL, which is below the normal range of 30-50. 
What supplementation dosage do you recommend?"
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

This project is for educational and personal use.

---

## 👨‍💻 Author

**Krishna Pathak**
- GitHub: [@Dev-KrishnaPathak](https://github.com/Dev-KrishnaPathak)
- Repository: [Patiently](https://github.com/Dev-KrishnaPathak/Patiently)

---

## 🙏 Acknowledgments

- **Cerebras** - For providing Llama 3.1-8b API
- **FastAPI** - Modern Python web framework
- **React** - UI library
- **Vite** - Lightning-fast build tool

---

**Made with ❤️ and AI**
