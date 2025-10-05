from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
	"""Document processing status"""
	UPLOADED = "uploaded"
	PROCESSING = "processing"
	COMPLETED = "completed"
	FAILED = "failed"

class FindingStatus(str, Enum):
	"""Status of individual medical finding"""
	NORMAL = "NORMAL"
	MONITOR = "MONITOR"
	URGENT = "URGENT"

class QuestionPriority(str, Enum):
	"""Priority level for generated questions"""
	URGENT = "URGENT"
	IMPORTANT = "IMPORTANT"
	FOLLOWUP = "FOLLOWUP"

# Request/Response Models

class DocumentMetadata(BaseModel):
	"""Metadata for uploaded document"""
	document_id: str
	filename: str
	file_type: str
	upload_time: datetime
	status: DocumentStatus
	processed_time: Optional[datetime] = None

class PatientContext(BaseModel):
	"""Optional patient context for personalization"""
	age: Optional[int] = None
	gender: Optional[str] = None
	known_conditions: Optional[List[str]] = None

class Finding(BaseModel):
	"""Individual test result or finding"""
	test_name: str
	value: Optional[str] = None
	normal_range: Optional[str] = None
	status: FindingStatus
	plain_english: str
	what_it_means: str
	clinical_significance: str
	recommendations: Optional[List[str]] = None

class Question(BaseModel):
	"""Generated question for doctor"""
	priority: QuestionPriority
	question: str
	category: str

class AnalysisResponse(BaseModel):
	"""Complete analysis response"""
	document_id: str
	document_type: str
	overall_summary: str
	overall_status: FindingStatus
	findings: List[Finding]
	urgent_findings_count: int
	monitor_findings_count: int
	normal_findings_count: int
	questions: List[Question]
	processed_at: datetime

class TrendDataPoint(BaseModel):
	"""Single data point for trend analysis"""
	date: datetime
	value: float
	status: FindingStatus

class TrendResponse(BaseModel):
	"""Trend analysis for a specific test over time"""
	test_name: str
	current_value: float
	previous_value: Optional[float] = None
	percentage_change: Optional[float] = None
	trend_direction: Optional[str] = None  # "improving", "worsening", "stable"
	data_points: List[TrendDataPoint]
	goal_range: Optional[str] = None

# Database Models

class DocumentRecord(BaseModel):
	"""Document record in database"""
	id: int
	document_id: str
	filename: str
	file_type: str
	upload_time: datetime
	status: str
	processed_time: Optional[datetime]
	document_type: Optional[str]
	extracted_text: Optional[str]
    
	class Config:
		from_attributes = True

class AnalysisRecord(BaseModel):
	"""Analysis record in database"""
	id: int
	document_id: str
	analysis_data: Dict
	created_at: datetime
    
	class Config:
		from_attributes = True

