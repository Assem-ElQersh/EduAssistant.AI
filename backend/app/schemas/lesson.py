from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class LessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int
    content: Optional[str] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    vocabulary: Optional[List[Dict[str, Any]]] = None
    grammar_points: Optional[List[Dict[str, Any]]] = None
    kanji_list: Optional[List[Dict[str, Any]]] = None
    estimated_duration: Optional[int] = None
    difficulty_level: Optional[str] = None
    lesson_type: Optional[str] = None

class LessonCreate(LessonBase):
    course_id: int

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    vocabulary: Optional[List[Dict[str, Any]]] = None
    grammar_points: Optional[List[Dict[str, Any]]] = None
    kanji_list: Optional[List[Dict[str, Any]]] = None
    estimated_duration: Optional[int] = None
    difficulty_level: Optional[str] = None
    lesson_type: Optional[str] = None
    is_published: Optional[bool] = None
    is_free: Optional[bool] = None

class LessonResponse(LessonBase):
    id: int
    course_id: int
    is_published: bool
    is_free: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LessonCompletionResponse(BaseModel):
    id: int
    student_id: int
    lesson_id: int
    is_completed: bool
    completion_percentage: int
    time_spent: int
    attempts: int
    difficulty_rating: Optional[int] = None
    notes: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_accessed: datetime

    class Config:
        from_attributes = True
