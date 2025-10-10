from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.core.security import get_current_user, get_current_active_teacher
from backend.app.base_models.models import User
from app.models.assignment import Assignment, AssignmentSubmission
from app.base_models.course import Enrollment
from app.schemas.assignment import (
    AssignmentCreate, 
    AssignmentUpdate, 
    AssignmentResponse,
    AssignmentSubmissionCreate,
    AssignmentSubmissionResponse,
    GradeSubmissionRequest
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[AssignmentResponse])
async def get_assignments(
    course_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assignments (filtered by course if specified)"""
    query = db.query(Assignment).filter(Assignment.is_published == True)
    
    if course_id:
        # Check authorization for specific course
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == course_id,
            Enrollment.is_active == True
        ).first()
        
        from app.base_models.course import Course
        course = db.query(Course).filter(Course.id == course_id).first()
        
        if not enrollment and (not course or course.teacher_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view assignments for this course"
            )
        
        query = query.filter(Assignment.course_id == course_id)
    else:
        # Get assignments for all enrolled courses
        if current_user.role == "student":
            enrolled_course_ids = db.query(Enrollment.course_id).filter(
                Enrollment.student_id == current_user.id,
                Enrollment.is_active == True
            ).subquery()
            
            query = query.filter(Assignment.course_id.in_(enrolled_course_ids))
        else:
            # Teachers see assignments for their courses
            from app.base_models.course import Course
            teacher_course_ids = db.query(Course.id).filter(
                Course.teacher_id == current_user.id
            ).subquery()
            
            query = query.filter(Assignment.course_id.in_(teacher_course_ids))
    
    assignments = query.order_by(Assignment.due_date).all()
    return assignments

@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific assignment details"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check authorization
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == assignment.course_id,
        Enrollment.is_active == True
    ).first()
    
    from app.base_models.course import Course
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    
    if not enrollment and (not course or course.teacher_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this assignment"
        )
    
    return assignment

@router.post("/", response_model=AssignmentResponse)
async def create_assignment(
    assignment_data: AssignmentCreate,
    current_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    """Create a new assignment (teachers only)"""
    # Check if teacher owns the course
    from app.base_models.course import Course
    course = db.query(Course).filter(Course.id == assignment_data.course_id).first()
    
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create assignments for this course"
        )
    
    assignment = Assignment(**assignment_data.dict())
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return assignment

@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_data: AssignmentUpdate,
    current_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    """Update assignment (only by course teacher)"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check if teacher owns the course
    from app.base_models.course import Course
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this assignment"
        )
    
    for field, value in assignment_data.dict(exclude_unset=True).items():
        setattr(assignment, field, value)
    
    db.commit()
    db.refresh(assignment)
    
    return assignment

@router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    """Delete assignment (only by course teacher)"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check if teacher owns the course
    from app.base_models.course import Course
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this assignment"
        )
    
    db.delete(assignment)
    db.commit()
    
    return {"message": "Assignment deleted successfully"}

@router.post("/{assignment_id}/submit", response_model=AssignmentSubmissionResponse)
async def submit_assignment(
    assignment_id: int,
    submission_data: AssignmentSubmissionCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit an assignment"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check if user is enrolled in the course
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == assignment.course_id,
        Enrollment.is_active == True
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this course"
        )
    
    # Check for existing submission
    existing_submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == current_user.id
    ).first()
    
    if existing_submission and assignment.max_attempts == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment already submitted"
        )
    
    # Calculate attempt number
    attempt_number = 1
    if existing_submission:
        attempt_number = existing_submission.attempt_number + 1
        
        if attempt_number > assignment.max_attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum attempts ({assignment.max_attempts}) exceeded"
            )
    
    # Create submission
    submission = AssignmentSubmission(
        assignment_id=assignment_id,
        student_id=current_user.id,
        content=submission_data.content,
        file_attachments=submission_data.file_attachments,
        audio_submission=submission_data.audio_submission,
        attempt_number=attempt_number,
        max_score=assignment.max_points
    )
    
    # Check if submission is late
    from datetime import datetime
    if assignment.due_date and datetime.utcnow() > assignment.due_date:
        submission.is_late = True
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # Trigger AI auto-grading if enabled
    if assignment.auto_grade:
        background_tasks.add_task(auto_grade_submission, submission.id)
    
    return submission

@router.get("/{assignment_id}/submission", response_model=Optional[AssignmentSubmissionResponse])
async def get_assignment_submission(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's submission for an assignment"""
    submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == current_user.id
    ).first()
    
    return submission

@router.post("/{assignment_id}/grade")
async def grade_submission(
    assignment_id: int,
    grade_data: GradeSubmissionRequest,
    current_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    """Grade an assignment submission (teachers only)"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check if teacher owns the course
    from app.base_models.course import Course
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    
    if not course or course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to grade this assignment"
        )
    
    # Get submission
    submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == grade_data.student_id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Update grade
    submission.score = grade_data.score
    submission.grade_percentage = (grade_data.score / submission.max_score) * 100
    submission.teacher_feedback = grade_data.feedback
    submission.is_graded = True
    
    from sqlalchemy.sql import func
    submission.graded_at = func.now()
    
    db.commit()
    
    return {"message": "Assignment graded successfully"}

async def auto_grade_submission(submission_id: int):
    """Background task for AI auto-grading"""
    # This would integrate with the RAG service for AI grading
    # Implementation depends on the specific AI grading logic
    logger.info(f"Auto-grading submission {submission_id}")
    pass
