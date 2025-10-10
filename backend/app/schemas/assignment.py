from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class AssignmentBase(BaseModel):
    courseID: int
    title: str
    description:str
    grade: int
    attachmentID: int
    content: Optional[Dict] = None
    created_at: datetime
    due_date: datetime

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    title: str
    description:str
    grade: int
    attachmentID: int
    content: Optional[Dict] = None
    due_date: datetime

class AssignmentResponse(AssignmentBase):
    id: int
    is_published: bool
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AssignmentSubmissionCreate(BaseModel):
    content: str
    studentID: int
    assignmentID: int
    date_submitted: datetime
    attachmentID: Optional[int]
    content: Optional[Dict]

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
    submissionID: int
    grade: int
