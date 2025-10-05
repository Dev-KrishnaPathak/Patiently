"""
Startup script for DocuSage Backend
Ensures we're in the right directory and starts the server
"""
import os
import sys
import subprocess

# Change to backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

print("=" * 60)
print("🏥 DocuSage Backend API Server")
print("=" * 60)
print(f"\n📂 Working directory: {backend_dir}")
print("🌐 Server: http://localhost:8000")
print("📚 API Docs: http://localhost:8000/docs")
print("\n🚀 Starting server...\n")

# Start uvicorn
subprocess.run([
    sys.executable, "-m", "uvicorn",
    "main:app",
    "--host", "127.0.0.1",
    "--port", "8000",
    "--reload"
])
