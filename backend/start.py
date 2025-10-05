"""
Simple startup script for DocuSage backend
Run this to start the API server without Docker
"""
import os
import sys

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🏥 DocuSage Backend API Server")
    print("=" * 60)
    print("\n📋 Configuration:")
    print(f"  • Backend directory: {backend_dir}")
    print(f"  • API endpoint: http://localhost:8000")
    print(f"  • Docs: http://localhost:8000/docs")
    print(f"  • Database: {'Configured' if os.getenv('DATABASE_URL') else 'Not configured (will run without DB)'}")
    print(f"  • Cerebras API: {'Configured' if os.getenv('CEREBRAS_API_KEY') else 'Not configured (LLM features disabled)'}")
    print("\n⚠️  Note: Database features require PostgreSQL to be running")
    print("   You can start it with: docker-compose up -d db")
    print("\n🚀 Starting server...\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
