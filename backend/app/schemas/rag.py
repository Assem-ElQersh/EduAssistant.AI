from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    course_id: Optional[int] = None
    message_type: str = "question"  # question, explanation, practice, etc.
    conversation_history: Optional[List[Dict[str, Any]]] = []

class ChatResponse(BaseModel):
    message_id: int
    response: str
    sources: List[Dict[str, Any]] = []
    confidence: float = 0.0
    grammar_points: List[str] = []
    vocabulary: List[Dict[str, str]] = []
    recommendations: List[str] = []

class DocumentUpload(BaseModel):
    filename: str
    content: str
    document_type: str  # pdf, text, markdown, etc.
    metadata: Optional[Dict[str, Any]] = {}

class QuizGenerationRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    num_questions: int = 10
    question_types: List[str] = ["multiple_choice"]
    jlpt_level: Optional[str] = None

class LessonSummaryRequest(BaseModel):
    content: str
    target_level: str = "intermediate"
    jlpt_level: Optional[str] = None

class ChatFeedback(BaseModel):
    message_id: int
    rating: int  # 1-5
    was_helpful: bool
    comments: Optional[str] = None
