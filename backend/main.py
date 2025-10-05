from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from typing import Optional
import uuid
from datetime import datetime
import logging

from fastapi.concurrency import run_in_threadpool

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules (these should exist in your project)
try:
	from services.document_processor import DocumentProcessor
	from services.llama_analyzer import LlamaAnalyzer
	from models.schemas import AnalysisResponse, DocumentMetadata
	
	# Use SQLite by default (simpler, no PostgreSQL needed)
	try:
		# Check if PostgreSQL is actually available by trying to connect
		import os
		db_url = os.getenv("DATABASE_URL", "")
		if db_url.startswith("postgresql://") and "localhost" in db_url:
			# Only use PostgreSQL if it's actually running
			import socket
			try:
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.settimeout(1)
				result = sock.connect_ex(('localhost', 5432))
				sock.close()
				if result == 0:
					from database.db import Database
					logger.info("✅ Using PostgreSQL database")
				else:
					raise ConnectionError("PostgreSQL not running")
			except:
				raise ConnectionError("PostgreSQL not available")
		else:
			raise ConnectionError("No PostgreSQL configured")
	except Exception as e:
		logger.info(f"📦 Using SQLite database (PostgreSQL not available: {e})")
		from database.sqlite_db import SQLiteDatabase as Database
		
except Exception:
	# If running in an environment where these modules aren't present, provide stubs/log warnings.
	DocumentProcessor = None
	LlamaAnalyzer = None
	AnalysisResponse = None
	DocumentMetadata = None
	Database = None

app = FastAPI(
	title="DocuSage API",
	description="AI-powered medical document translator",
	version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],  # Configure this properly in production
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Initialize services (if available)
document_processor = DocumentProcessor() if DocumentProcessor else None
llama_analyzer = LlamaAnalyzer() if LlamaAnalyzer else None
db = Database() if Database else None

# Create upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
async def root():
	"""Health check endpoint"""
	return {
		"status": "healthy",
		"service": "DocuSage API",
		"version": "1.0.0"
	}


@app.post("/api/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
	"""
	Upload and process a medical document
    
	Accepts: PDF, JPG, PNG (Max 10MB)
	Returns: document_id and processing status (enqueued)
	"""
	try:
		# Validate file type
		allowed_types = ["application/pdf", "image/jpeg", "image/png", "text/plain"]
		if file.content_type not in allowed_types:
			raise HTTPException(
				status_code=400,
				detail=f"Invalid file type. Allowed: PDF, JPG, PNG, TXT"
			)

		# Generate unique document ID
		document_id = str(uuid.uuid4())

		# Save file to disk without loading entire content into memory
		file_extension = (file.filename or "").split(".")[-1]
		file_path = os.path.join(UPLOAD_DIR, f"{document_id}.{file_extension}")

		# Stream file to disk in a threadpool to avoid blocking event loop
		def _save_file_sync(src_file, dest_path, max_bytes=10 * 1024 * 1024):
			bytes_written = 0
			with open(dest_path, "wb") as dest:
				while True:
					chunk = src_file.read(1024 * 64)
					if not chunk:
						break
					bytes_written += len(chunk)
					if bytes_written > max_bytes:
						raise ValueError("File size exceeds 10MB limit")
					dest.write(chunk)

		try:
			await run_in_threadpool(_save_file_sync, file.file, file_path)
		except ValueError as ve:
			# remove partial file if created
			try:
				if os.path.exists(file_path):
					os.remove(file_path)
			except Exception:
				pass
			raise HTTPException(status_code=400, detail=str(ve))

		logger.info(f"File uploaded: {document_id} - {file.filename}")

		# Store metadata in database if available
		if db and DocumentMetadata:
			metadata = DocumentMetadata(
				document_id=document_id,
				filename=file.filename,
				file_type=file.content_type,
				upload_time=datetime.utcnow(),
				status="processing"
			)
			await db.save_document_metadata(metadata)

		# Start background processing (non-blocking)
		background_tasks.add_task(
			_background_process,
			document_id,
			file_path,
			file.filename,
			file.content_type
		)

		return JSONResponse(
			status_code=202,
			content={
				"document_id": document_id,
				"filename": file.filename,
				"status": "uploaded",
				"message": "Document uploaded successfully. Processing enqueued."
			}
		)

	except HTTPException as e:
		raise e
	except Exception as e:
		logger.error(f"Upload error: {str(e)}")
		raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/document/{document_id}/process")
async def process_document(document_id: str):
	"""
	Process uploaded document: Extract text, classify, and analyze
	"""
	try:
		# Get file path
		file_path = None
		for ext in ["pdf", "jpg", "jpeg", "png"]:
			potential_path = os.path.join(UPLOAD_DIR, f"{document_id}.{ext}")
			if os.path.exists(potential_path):
				file_path = potential_path
				break

		if not file_path:
			raise HTTPException(status_code=404, detail="Document not found")

		# Step 1: Extract text from document
		logger.info(f"Extracting text from: {document_id}")
		if not document_processor:
			raise HTTPException(status_code=500, detail="Document processor not configured")
		extracted_text = await document_processor.extract_text(file_path)

		if not extracted_text:
			raise HTTPException(
				status_code=400,
				detail="Could not extract text from document"
			)

		# Step 2: Classify document type
		logger.info(f"Classifying document: {document_id}")
		document_type = await llama_analyzer.classify_document(extracted_text) if llama_analyzer else "unknown"

		# Step 3: Analyze with Llama
		logger.info(f"Analyzing with Llama: {document_id}")
		analysis = await llama_analyzer.analyze_document(
			text=extracted_text,
			document_type=document_type
		) if llama_analyzer else {"findings": []}

		# Step 4: Generate questions
		logger.info(f"Generating questions: {document_id}")
		questions = await llama_analyzer.generate_questions(
			findings=analysis.get("findings", []),
			document_type=document_type
		) if llama_analyzer else []

		# Combine results
		result = {
			"document_id": document_id,
			"document_type": document_type,
			"extracted_text": extracted_text,  # Full text (removed 500 char limit)
			"analysis": analysis,
			"questions": questions,
			"processed_at": datetime.utcnow().isoformat()
		}

		# Save analysis to database if available
		if db:
			await db.save_analysis(document_id, result)
			await db.update_document_status(document_id, "completed")

		logger.info(f"Processing completed: {document_id}")

		return JSONResponse(status_code=200, content=result)

	except HTTPException as e:
		raise e
	except Exception as e:
		logger.error(f"Processing error: {str(e)}")
		if db:
			await db.update_document_status(document_id, "failed")
		raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.get("/api/document/{document_id}/analysis")
async def get_analysis(document_id: str):
	"""
	Retrieve analysis results for a document
	"""
	try:
		if not db:
			raise HTTPException(status_code=500, detail="Database not configured")
		analysis = await db.get_analysis(document_id)

		if not analysis:
			raise HTTPException(status_code=404, detail="Analysis not found")

		return JSONResponse(status_code=200, content=analysis)

	except HTTPException as e:
		raise e
	except Exception as e:
		logger.error(f"Retrieval error: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
async def list_documents(skip: int = 0, limit: int = 10):
	"""
	List all uploaded documents
	"""
	try:
		if not db:
			raise HTTPException(status_code=500, detail="Database not configured")
		documents = await db.list_documents(skip=skip, limit=limit)
		return JSONResponse(status_code=200, content={"documents": documents})

	except Exception as e:
		logger.error(f"List error: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/document/{document_id}")
async def delete_document(document_id: str):
	"""
	Delete a document and its analysis
	"""
	try:
		# Delete file
		for ext in ["pdf", "jpg", "jpeg", "png"]:
			file_path = os.path.join(UPLOAD_DIR, f"{document_id}.{ext}")
			if os.path.exists(file_path):
				os.remove(file_path)

		# Delete from database
		if db:
			await db.delete_document(document_id)

		return JSONResponse(
			status_code=200,
			content={"message": "Document deleted successfully"}
		)

	except Exception as e:
		logger.error(f"Delete error: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/document/{document_id}/trends")
async def get_trends(document_id: str, test_name: Optional[str] = None):
	"""
	Get historical trends for specific test metrics
	"""
	try:
		if not db:
			raise HTTPException(status_code=500, detail="Database not configured")
		trends = await db.get_trends(document_id, test_name)
		return JSONResponse(status_code=200, content=trends)

	except Exception as e:
		logger.error(f"Trends error: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))


async def _background_process(document_id: str, file_path: str, filename: str, content_type: str):
	"""
	Background processing helper used by the upload endpoint.
	Mirrors logic in /api/document/{document_id}/process but runs asynchronously in background.
	"""
	try:
		logger.info(f"Background processing started: {document_id}")

		if not document_processor:
			logger.error("Document processor not available; skipping background processing")
			if db:
				await db.update_document_status(document_id, "failed")
			return

		extracted_text = await document_processor.extract_text(file_path)
		if not extracted_text:
			await db.update_document_status(document_id, "failed")
			logger.error(f"Background extract failed: {document_id}")
			return

		document_type = await llama_analyzer.classify_document(extracted_text) if llama_analyzer else "unknown"

		analysis = await llama_analyzer.analyze_document(
			text=extracted_text,
			document_type=document_type
		) if llama_analyzer else {"findings": []}

		questions = await llama_analyzer.generate_questions(
			findings=analysis.get("findings", []),
			document_type=document_type
		) if llama_analyzer else []

		result = {
			"document_id": document_id,
			"document_type": document_type,
			"extracted_text": extracted_text[:500],
			"analysis": analysis,
			"questions": questions,
			"processed_at": datetime.utcnow().isoformat()
		}

		if db:
			await db.save_analysis(document_id, result)
			await db.update_document_status(document_id, "completed")
		logger.info(f"Background processing completed: {document_id}")

	except Exception as e:
		logger.error(f"Background processing error for {document_id}: {e}")
		try:
			if db:
				await db.update_document_status(document_id, "failed")
		except Exception:
			pass


if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000)

