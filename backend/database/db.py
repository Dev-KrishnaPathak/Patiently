import os
import asyncpg
import json
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    """
    PostgreSQL database interface for DocuSage
    Handles document metadata and analysis storage
    """
    
    def __init__(self):
        self.db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://docusage:password@localhost:5432/docusage"
        )
        self.pool = None
    
    async def connect(self):
        """Initialize database connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.db_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Database connection pool created")
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def init_tables(self):
        """Create database tables if they don't exist"""
        await self.connect()
        
        async with self.pool.acquire() as conn:
            # Documents table - must be created first
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
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
                )
            """)
            
            # Analysis table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id SERIAL PRIMARY KEY,
                    document_id VARCHAR(255) NOT NULL,
                    analysis_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
                )
            """)
            
            # Findings table for trend analysis
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS findings (
                    id SERIAL PRIMARY KEY,
                    document_id VARCHAR(255) NOT NULL,
                    test_name VARCHAR(255) NOT NULL,
                    value FLOAT,
                    value_text VARCHAR(255),
                    unit VARCHAR(50),
                    normal_range VARCHAR(100),
                    status VARCHAR(20),
                    test_date TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
                )
            """)
            
            # Create indices for better query performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_document_id 
                ON documents(document_id)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_analyses_document_id 
                ON analyses(document_id)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_findings_test_name 
                ON findings(test_name, test_date)
            """)
            
            logger.info("Database tables initialized")
    
    async def save_document_metadata(self, metadata: 'DocumentMetadata'):
        """Save document metadata"""
        await self.connect()
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO documents 
                (document_id, filename, file_type, upload_time, status)
                VALUES ($1, $2, $3, $4, $5)
            """, 
                metadata.document_id,
                metadata.filename,
                metadata.file_type,
                metadata.upload_time,
                metadata.status
            )
            
            logger.info(f"Document metadata saved: {metadata.document_id}")
    
    async def update_document_status(self, document_id: str, status: str):
        """Update document processing status"""
        await self.connect()
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE documents 
                SET status = $1, processed_time = $2
                WHERE document_id = $3
            """, status, datetime.utcnow(), document_id)
            
            logger.info(f"Document status updated: {document_id} -> {status}")
    
    async def save_analysis(self, document_id: str, analysis_data: Dict):
        """Save analysis results"""
        await self.connect()
        
        async with self.pool.acquire() as conn:
            # Save full analysis
            await conn.execute("""
                INSERT INTO analyses (document_id, analysis_data)
                VALUES ($1, $2)
            """, document_id, json.dumps(analysis_data))
            
            # Extract and save individual findings for trend analysis
            findings = analysis_data.get('analysis', {}).get('findings', [])
            for finding in findings:
                try:
                    # Try to extract numeric value
                    value = finding.get('value', '')
                    numeric_value = None
                    
                    if value:
                        # Extract first number from string
                        import re
                        numbers = re.findall(r'-?\d+\.?\d*', str(value))
                        if numbers:
                            numeric_value = float(numbers[0])
                    
                    test_date = analysis_data.get('processed_at', datetime.utcnow())
                    if isinstance(test_date, str):
                        test_date = datetime.fromisoformat(test_date.replace('Z', '+00:00'))
                    
                    await conn.execute("""
                        INSERT INTO findings 
                        (document_id, test_name, value, value_text, status, test_date)
                        VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                        document_id,
                        finding.get('test_name', 'Unknown'),
                        numeric_value,
                        str(value),
                        finding.get('status', 'NORMAL'),
                        test_date
                    )
                except Exception as e:
                    logger.warning(f"Could not save finding: {str(e)}")
            
            logger.info(f"Analysis saved: {document_id}")
    
    async def get_analysis(self, document_id: str) -> Optional[Dict]:
        """Retrieve analysis for a document"""
        await self.connect()
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT analysis_data 
                FROM analyses 
                WHERE document_id = $1
                ORDER BY created_at DESC
                LIMIT 1
            """, document_id)
            
            if row:
                return row['analysis_data']
            return None
    
    async def list_documents(self, skip: int = 0, limit: int = 10) -> List[Dict]:
        """List all documents with pagination"""
        await self.connect()
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    document_id, filename, file_type, 
                    upload_time, status, processed_time, document_type
                FROM documents
                ORDER BY upload_time DESC
                LIMIT $1 OFFSET $2
            """, limit, skip)
            
            return [dict(row) for row in rows]
    
    async def delete_document(self, document_id: str):
        """Delete document and all associated data"""
        await self.connect()
        
        async with self.pool.acquire() as conn:
            # CASCADE will automatically delete analyses and findings
            await conn.execute("""
                DELETE FROM documents 
                WHERE document_id = $1
            """, document_id)
            
            logger.info(f"Document deleted: {document_id}")
    
    async def get_trends(self, document_id: str, test_name: Optional[str] = None) -> Dict:
        """Get historical trends for test metrics"""
        await self.connect()
        
        async with self.pool.acquire() as conn:
            if test_name:
                # Get trend for specific test
                rows = await conn.fetch("""
                    SELECT 
                        f.test_name, f.value, f.value_text, 
                        f.status, f.test_date, d.document_id
                    FROM findings f
                    JOIN documents d ON f.document_id = d.document_id
                    WHERE f.test_name = $1
                    ORDER BY f.test_date ASC
                """, test_name)
            else:
                # Get all available tests from this document
                rows = await conn.fetch("""
                    SELECT DISTINCT test_name
                    FROM findings
                    WHERE document_id = $1
                """, document_id)
                
                return {
                    "available_tests": [row['test_name'] for row in rows]
                }
            
            if not rows:
                return {"error": "No trend data found"}
            
            # Build trend data
            data_points = []
            for row in rows:
                data_points.append({
                    "date": row['test_date'].isoformat(),
                    "value": row['value'],
                    "value_text": row['value_text'],
                    "status": row['status'],
                    "document_id": row['document_id']
                })
            
            # Calculate trend
            trend_direction = "stable"
            percentage_change = None
            
            if len(data_points) >= 2:
                first_val = data_points[0].get('value')
                last_val = data_points[-1].get('value')
                
                if first_val and last_val:
                    percentage_change = ((last_val - first_val) / first_val) * 100
                    
                    if percentage_change > 5:
                        trend_direction = "increasing"
                    elif percentage_change < -5:
                        trend_direction = "decreasing"
            
            return {
                "test_name": test_name,
                "data_points": data_points,
                "trend_direction": trend_direction,
                "percentage_change": round(percentage_change, 2) if percentage_change else None,
                "total_tests": len(data_points)
            }
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
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
                )
            """)
            
            # Analysis table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id SERIAL PRIMARY KEY,
                    document_id VARCHAR(255) NOT NULL,
                    analysis_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
                )
            """)
            
            #