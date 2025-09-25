from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.course import Course, Enrollment
from app.schemas.course import EnrollmentResponse

router = APIRouter()

@router.get("/my-enrollments", response_model=List[EnrollmentResponse])
async def get_my_enrollments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's enrollments"""
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.is_active == True
    ).all()
    
    return enrollments

@router.get("/course/{course_id}/students", response_model=List[dict])
async def get_course_students(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get students enrolled in a course (teachers only)"""
    # Check if user is the teacher of this course
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view students for this course"
        )
    
    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id == course_id,
        Enrollment.is_active == True
    ).all()
    
    students = []
    for enrollment in enrollments:
        student_data = {
            "enrollment_id": enrollment.id,
            "student_id": enrollment.student_id,
            "student_name": enrollment.student.full_name,
            "student_email": enrollment.student.email,
            "progress": enrollment.progress,
            "grade": enrollment.grade,
            "enrolled_at": enrollment.enrolled_at,
            "completed_at": enrollment.completed_at
        }
        students.append(student_data)
    
    return students
