from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.core.security import get_current_user, get_current_active_teacher
from app.models.user import User
from app.models.course import Course, Enrollment
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, EnrollmentResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[CourseResponse])
async def get_courses(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    jlpt_level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available courses"""
    query = db.query(Course).filter(Course.is_active == True)
    
    if search:
        query = query.filter(Course.title.ilike(f"%{search}%"))
    
    if jlpt_level:
        query = query.filter(Course.jlpt_level == jlpt_level)
    
    courses = query.offset(skip).limit(limit).all()
    return courses

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific course details"""
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.is_active == True
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return course

@router.post("/", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    """Create a new course (teachers only)"""
    course = Course(
        **course_data.dict(),
        teacher_id=current_user.id
    )
    
    db.add(course)
    db.commit()
    db.refresh(course)
    
    return course

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    """Update course (only by course teacher)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this course"
        )
    
    for field, value in course_data.dict(exclude_unset=True).items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    
    return course

@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    """Delete course (only by course teacher)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this course"
        )
    
    course.is_active = False
    db.commit()
    
    return {"message": "Course deleted successfully"}

@router.post("/{course_id}/enroll", response_model=EnrollmentResponse)
async def enroll_in_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll in a course"""
    # Check if course exists
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.is_active == True
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if already enrolled
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == course_id,
        Enrollment.is_active == True
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    # Create enrollment
    enrollment = Enrollment(
        student_id=current_user.id,
        course_id=course_id
    )
    
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    return enrollment

@router.post("/{course_id}/unenroll")
async def unenroll_from_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unenroll from a course"""
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == course_id,
        Enrollment.is_active == True
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    enrollment.is_active = False
    db.commit()
    
    return {"message": "Unenrolled successfully"}

@router.get("/{course_id}/progress")
async def get_course_progress(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's progress in a course"""
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == course_id,
        Enrollment.is_active == True
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enrolled in this course"
        )
    
    # Calculate detailed progress metrics
    # This would involve querying lessons, assignments, quizzes, etc.
    
    return {
        "course_id": course_id,
        "progress": enrollment.progress,
        "grade": enrollment.grade,
        "enrolled_at": enrollment.enrolled_at,
        "completed_at": enrollment.completed_at
    }
