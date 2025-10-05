import os
import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SQLiteDatabase:
    """
    SQLite database interface for DocuSage (development/demo mode)
    Simpler alternative to PostgreSQL - no server needed!
    """

    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "..", "docusage.db")
        self.conn = None

    async def connect(self):
        """Initialize database connection"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"SQLite database connected: {self.db_path}")

    async def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("SQLite database connection closed")

    async def init_tables(self):
        """Create database tables if they don't exist"""
        await self.connect()

        cursor = self.conn.cursor()

        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                upload_time TEXT NOT NULL,
                status TEXT NOT NULL,
                processed_time TEXT,
                document_type TEXT,
                extracted_text TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Analyses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                analysis_data TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
            )
        """)

        # Findings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                test_name TEXT NOT NULL,
                value REAL,
                value_text TEXT,
                status TEXT,
                test_date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
            )
        """)

        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_document_id ON documents(document_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_document_id ON analyses(document_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_findings_test_name ON findings(test_name, test_date)")

        self.conn.commit()
        logger.info("SQLite database tables initialized")

    async def save_document_metadata(self, metadata):
        """Save document metadata"""
        await self.connect()

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO documents 
            (document_id, filename, file_type, upload_time, status)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                metadata.document_id,
                metadata.filename,
                metadata.file_type,
                metadata.upload_time.isoformat(),
                metadata.status.value if hasattr(metadata.status, 'value') else metadata.status
            )
        )
        self.conn.commit()
        logger.info(f"Document metadata saved: {metadata.document_id}")

    async def update_document_status(self, document_id: str, status: str):
        """Update document processing status"""
        await self.connect()

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE documents 
            SET status = ?, processed_time = ?
            WHERE document_id = ?
        """, (status, datetime.utcnow().isoformat(), document_id))
        self.conn.commit()
        logger.info(f"Document status updated: {document_id} -> {status}")

    async def save_analysis(self, document_id: str, analysis_data: Dict):
        """Save analysis results"""
        await self.connect()

        cursor = self.conn.cursor()

        # Save full analysis
        cursor.execute("""
            INSERT INTO analyses (document_id, analysis_data)
            VALUES (?, ?)
        """, (document_id, json.dumps(analysis_data)))

        # Extract and save findings for trend analysis
        findings = analysis_data.get('analysis', {}).get('findings', [])
        for finding in findings:
            try:
                import re
                value_text = str(finding.get('value', ''))
                numeric_value = None

                if value_text:
                    numbers = re.findall(r'-?\d+\.?\d*', value_text)
                    if numbers:
                        numeric_value = float(numbers[0])

                test_date = analysis_data.get('processed_at', datetime.utcnow().isoformat())
                if isinstance(test_date, str):
                    # Keep as string for SQLite
                    pass

                cursor.execute("""
                    INSERT INTO findings 
                    (document_id, test_name, value, value_text, status, test_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        document_id,
                        finding.get('test_name', 'Unknown'),
                        numeric_value,
                        value_text,
                        finding.get('status', 'NORMAL'),
                        test_date
                    )
                )
            except Exception as e:
                logger.warning(f"Could not save finding: {str(e)}")

        self.conn.commit()
        logger.info(f"Analysis saved: {document_id}")

    async def get_analysis(self, document_id: str) -> Optional[Dict]:
        """Retrieve analysis for a document"""
        await self.connect()

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT analysis_data 
            FROM analyses 
            WHERE document_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (document_id,))

        row = cursor.fetchone()
        if row:
            return json.loads(row['analysis_data'])
        return None

    async def list_documents(self, skip: int = 0, limit: int = 10) -> List[Dict]:
        """List all documents with pagination"""
        await self.connect()

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                document_id, filename, file_type, 
                upload_time, status, processed_time, document_type
            FROM documents
            ORDER BY upload_time DESC
            LIMIT ? OFFSET ?
        """, (limit, skip))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    async def delete_document(self, document_id: str):
        """Delete document and all associated data"""
        await self.connect()

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))
        self.conn.commit()
        logger.info(f"Document deleted: {document_id}")

    async def get_trends(self, document_id: str, test_name: Optional[str] = None) -> Dict:
        """Get historical trends for test metrics"""
        await self.connect()

        cursor = self.conn.cursor()

        if test_name:
            # Get trend for specific test
            cursor.execute("""
                SELECT 
                    f.test_name, f.value, f.value_text, 
                    f.status, f.test_date, d.document_id
                FROM findings f
                JOIN documents d ON f.document_id = d.document_id
                WHERE f.test_name = ?
                ORDER BY f.test_date ASC
            """, (test_name,))
        else:
            # Get all available tests from this document
            cursor.execute("""
                SELECT DISTINCT test_name
                FROM findings
                WHERE document_id = ?
            """, (document_id,))

            rows = cursor.fetchall()
            return {
                "available_tests": [row['test_name'] for row in rows]
            }

        rows = cursor.fetchall()
        if not rows:
            return {"error": "No trend data found"}

        # Build trend data
        data_points = []
        for row in rows:
            data_points.append({
                "date": row['test_date'],
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
