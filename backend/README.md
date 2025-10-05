# DocuSage Backend API

AI-powered medical document translator - FastAPI backend service.

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** (or 3.10+)
- **PostgreSQL** (optional, for persistence)
- **Tesseract OCR** (optional, for image/scanned PDF processing)
- **Poppler** (optional, for PDF-to-image conversion)
- **Cerebras API Key** (optional, for LLM analysis features)

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   # Windows
   run.bat

   # macOS/Linux
   python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```

3. **Access the API:**
   - API Server: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000

## 📋 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database (optional - app works without it in demo mode)
DATABASE_URL=postgresql://docusage:password@localhost:5432/docusage

# Cerebras API for LLM features (optional)
CEREBRAS_API_KEY=your_cerebras_api_key_here
```

### With Docker (Recommended for Database)

```bash
# Start PostgreSQL
docker-compose up -d db

# Initialize database tables
python -c "import asyncio; from database.db import Database; asyncio.run(Database().init_tables())"

# Start API server
run.bat
```

## 🔌 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/upload` | Upload document (PDF, JPG, PNG) |
| `POST` | `/api/document/{id}/process` | Process uploaded document |
| `GET` | `/api/document/{id}/analysis` | Get analysis results |
| `GET` | `/api/documents` | List all documents |
| `DELETE` | `/api/document/{id}` | Delete document |
| `GET` | `/api/document/{id}/trends` | Get trend data |

### Example Usage

**Upload a document:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@lab_results.pdf"
```

**Get analysis:**
```bash
curl "http://localhost:8000/api/document/{document_id}/analysis"
```

## 🏗️ Architecture

```
backend/
├── main.py                    # FastAPI app & endpoints
├── requirements.txt           # Python dependencies
├── run.bat                   # Windows startup script
├── database/
│   ├── __init__.py
│   └── db.py                 # PostgreSQL database layer
├── services/
│   ├── __init__.py
│   ├── document_processor.py # PDF/image text extraction
│   └── llama_analyzer.py     # LLM analysis wrapper
├── models/
│   ├── __init__.py
│   └── schemas.py            # Pydantic models
└── uploads/                   # Uploaded files (auto-created)
```

## 🔧 Features

### Document Processing Pipeline

1. **Upload** - Streams file to disk (max 10MB)
2. **Extract** - Uses pdfplumber → PyPDF2 → OCR fallback
3. **Classify** - LLM determines document type
4. **Analyze** - LLM translates medical jargon to plain English
5. **Generate Questions** - Creates doctor visit questions
6. **Store** - Saves to PostgreSQL (if configured)

### Supported File Types

- **PDF** - Text-based or scanned (with OCR)
- **JPG/JPEG** - Images with text (OCR)
- **PNG** - Images with text (OCR)

### OCR Stack

- **pdfplumber** - Primary PDF text extraction
- **PyPDF2** - Fallback PDF reader
- **pytesseract** - Optical Character Recognition
- **pdf2image** - PDF to image conversion
- **Pillow** - Image processing

## 🗄️ Database Schema

### Documents Table
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) UNIQUE NOT NULL,
    filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    upload_time TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL,
    processed_time TIMESTAMP,
    document_type VARCHAR(100),
    extracted_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Analyses Table
```sql
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);
```

### Findings Table (for trends)
```sql
CREATE TABLE findings (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    value FLOAT,
    value_text VARCHAR(255),
    status VARCHAR(20),
    test_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);
```

## 🧪 Testing

Visit the interactive API docs at http://localhost:8000/docs to test endpoints.

### Test without Database

The API runs in "demo mode" without PostgreSQL:
- Upload and processing work
- Analysis is performed (if Cerebras API key is set)
- Results are returned but not persisted
- List/trends endpoints return errors

### Test with Database

1. Start PostgreSQL: `docker-compose up -d db`
2. Init tables: `python -c "import asyncio; from database.db import Database; asyncio.run(Database().init_tables())"`
3. All endpoints work with persistence

## 🐛 Troubleshooting

### "Import could not be resolved" errors
These are linting warnings if packages aren't installed. Run:
```bash
pip install -r requirements.txt
```

### "CEREBRAS_API_KEY is not set" warning
Normal if you haven't configured the LLM. The API works for uploads but won't perform analysis.

### "Database not configured" errors
Normal if PostgreSQL isn't running. Upload/process endpoints work, but storage/retrieval features are disabled.

### OCR not working
Install system dependencies:
- **Tesseract**: https://github.com/tesseract-ocr/tesseract
- **Poppler**: https://poppler.freedesktop.org/

## 📦 Dependencies

See `requirements.txt` for full list. Key packages:

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **asyncpg** - PostgreSQL async driver
- **httpx** - HTTP client for API calls
- **pdfplumber, PyPDF2** - PDF processing
- **pytesseract, pdf2image, Pillow** - OCR & images
- **pydantic** - Data validation

## 🔐 Security Notes

- Max file upload: 10MB
- CORS enabled for all origins (configure in production)
- Files streamed to disk to avoid memory issues
- Database uses parameterized queries (SQL injection safe)

## 📝 License

Part of the DocuSage project.
