from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class AssignmentBase(BaseModel):
    title: str
    description: str
    instructions: Optional[str] = None
    assignment_type: str
    max_points: float = 100.0
    passing_score: float = 70.0
    content: Optional[str] = None
    resources: Optional[List[Dict[str, Any]]] = None
    rubric: Optional[Dict[str, Any]] = None
    target_grammar: Optional[List[str]] = None
    target_vocabulary: Optional[List[str]] = None
    jlpt_level: Optional[str] = None
    allow_late_submission: bool = True
    max_attempts: int = 1
    time_limit: Optional[int] = None
    auto_grade: bool = False
    ai_feedback: bool = True

class AssignmentCreate(AssignmentBase):
    course_id: int
    due_date: Optional[datetime] = None
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    assignment_type: Optional[str] = None
    max_points: Optional[float] = None
    passing_score: Optional[float] = None
    content: Optional[str] = None
    resources: Optional[List[Dict[str, Any]]] = None
    rubric: Optional[Dict[str, Any]] = None
    target_grammar: Optional[List[str]] = None
    target_vocabulary: Optional[List[str]] = None
    jlpt_level: Optional[str] = None
    allow_late_submission: Optional[bool] = None
    max_attempts: Optional[int] = None
    time_limit: Optional[int] = None
    auto_grade: Optional[bool] = None
    ai_feedback: Optional[bool] = None
    is_published: Optional[bool] = None
    due_date: Optional[datetime] = None
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None

class AssignmentResponse(AssignmentBase):
    id: int
    course_id: int
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None

    class Config:
        from_attributes = True

class AssignmentSubmissionCreate(BaseModel):
    content: str
    file_attachments: Optional[List[str]] = None
    audio_submission: Optional[str] = None

class AssignmentSubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    content: str
    file_attachments: Optional[List[str]] = None
    audio_submission: Optional[str] = None
    score: Optional[float] = None
    max_score: float
    grade_percentage: Optional[float] = None
    is_graded: bool
    teacher_feedback: Optional[str] = None
    ai_feedback: Optional[Dict[str, Any]] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    attempt_number: int
    time_spent: Optional[int] = None
    is_late: bool
    submitted_at: datetime
    graded_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GradeSubmissionRequest(BaseModel):
    student_id: int
    score: float
    feedback: Optional[str] = None
