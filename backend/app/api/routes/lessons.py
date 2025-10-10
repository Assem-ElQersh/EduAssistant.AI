from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.core.security import get_current_user, get_current_active_teacher
from backend.app.base_models.models import User
from app.models.lesson import Lesson, LessonCompletion
from app.base_models.course import Enrollment
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonResponse, LessonCompletionResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[LessonResponse])
async def get_lessons(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all lessons for a course"""
    # Check if user is enrolled or is the teacher
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == course_id,
        Enrollment.is_active == True
    ).first()
    
    # Or check if user is the teacher
    from app.base_models.course import Course
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not enrollment and (not course or course.teacher_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view lessons for this course"
        )
    
    lessons = db.query(Lesson).filter(
        Lesson.course_id == course_id,
        Lesson.is_published == True
    ).order_by(Lesson.order_index).all()
    
    return lessons

@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific lesson details"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Check authorization
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == lesson.course_id,
        Enrollment.is_active == True
    ).first()
    
    from app.base_models.course import Course
    course = db.query(Course).filter(Course.id == lesson.course_id).first()
    
    if not enrollment and (not course or course.teacher_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this lesson"
        )
    
    return lesson

@router.post("/", response_model=LessonResponse)
async def create_lesson(
    lesson_data: LessonCreate,
    current_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    """Create a new lesson (teachers only)"""
    # Check if teacher owns the course
    from app.base_models.course import Course
    course = db.query(Course).filter(Course.id == lesson_data.course_id).first()
    
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create lessons for this course"
        )
    
    lesson = Lesson(**lesson_data.dict())
    
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    
    return lesson

@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    lesson_data: LessonUpdate,
    current_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    """Update lesson (only by course teacher)"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Check if teacher owns the course
    from app.base_models.course import Course
    course = db.query(Course).filter(Course.id == lesson.course_id).first()
    
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this lesson"
        )
    
    for field, value in lesson_data.dict(exclude_unset=True).items():
        setattr(lesson, field, value)
    
    db.commit()
    db.refresh(lesson)
    
    return lesson

@router.delete("/{lesson_id}")
async def delete_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    """Delete lesson (only by course teacher)"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Check if teacher owns the course
    from app.base_models.course import Course
    course = db.query(Course).filter(Course.id == lesson.course_id).first()
    
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this lesson"
        )
    
    db.delete(lesson)
    db.commit()
    
    return {"message": "Lesson deleted successfully"}

@router.post("/{lesson_id}/complete", response_model=LessonCompletionResponse)
async def mark_lesson_complete(
    lesson_id: int,
    completion_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a lesson as complete"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Check if user is enrolled in the course
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == lesson.course_id,
        Enrollment.is_active == True
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this course"
        )
    
    # Get or create lesson completion
    completion = db.query(LessonCompletion).filter(
        LessonCompletion.student_id == current_user.id,
        LessonCompletion.lesson_id == lesson_id
    ).first()
    
    if not completion:
        completion = LessonCompletion(
            student_id=current_user.id,
            lesson_id=lesson_id
        )
        db.add(completion)
    
    # Update completion data
    completion.is_completed = completion_data.get("is_completed", True)
    completion.completion_percentage = completion_data.get("completion_percentage", 100)
    completion.time_spent = completion_data.get("time_spent", 0)
    completion.difficulty_rating = completion_data.get("difficulty_rating")
    completion.notes = completion_data.get("notes")
    
    if completion.is_completed and not completion.completed_at:
        from sqlalchemy.sql import func
        completion.completed_at = func.now()
    
    db.commit()
    db.refresh(completion)
    
    return completion

@router.get("/{lesson_id}/completion", response_model=Optional[LessonCompletionResponse])
async def get_lesson_completion(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's completion status for a lesson"""
    completion = db.query(LessonCompletion).filter(
        LessonCompletion.student_id == current_user.id,
        LessonCompletion.lesson_id == lesson_id
    ).first()
    
    return completion
