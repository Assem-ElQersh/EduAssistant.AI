from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    course_code: str
    difficulty_level: Optional[str] = None
    jlpt_level: Optional[str] = None
    estimated_duration: Optional[int] = None
    syllabus: Optional[str] = None
    objectives: Optional[str] = None
    prerequisites: Optional[str] = None
    max_students: int = 100

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[str] = None
    jlpt_level: Optional[str] = None
    estimated_duration: Optional[int] = None
    syllabus: Optional[str] = None
    objectives: Optional[str] = None
    prerequisites: Optional[str] = None
    max_students: Optional[int] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None

class CourseResponse(CourseBase):
    id: int
    teacher_id: int
    is_active: bool
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    is_active: bool
    progress: float
    grade: Optional[str] = None
    enrolled_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
