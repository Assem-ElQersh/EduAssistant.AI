from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.core.security import get_current_user, get_current_active_teacher
from backend.app.base_models.models import User
from app.models.analytics import StudySession, LearningAnalytics, WeaknessIdentification
from app.models.assignment import AssignmentSubmission
from app.models.quiz import QuizAttempt
from app.base_models.course import Enrollment
from app.services.analytics_service import AnalyticsService

router = APIRouter()
analytics_service = AnalyticsService()

@router.get("/dashboard/student")
async def get_student_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive student dashboard analytics"""
    try:
        # Get recent study sessions
        recent_sessions = db.query(StudySession).filter(
            StudySession.student_id == current_user.id
        ).order_by(desc(StudySession.started_at)).limit(10).all()
        
        # Get current enrollments with progress
        enrollments = db.query(Enrollment).filter(
            and_(
                Enrollment.student_id == current_user.id,
                Enrollment.is_active == True
            )
        ).all()
        
        # Get recent quiz attempts
        recent_quizzes = db.query(QuizAttempt).filter(
            QuizAttempt.student_id == current_user.id
        ).order_by(desc(QuizAttempt.completed_at)).limit(5).all()
        
        # Get current weaknesses
        weaknesses = db.query(WeaknessIdentification).filter(
            and_(
                WeaknessIdentification.student_id == current_user.id,
                WeaknessIdentification.is_active == True
            )
        ).all()
        
        # Calculate statistics
        total_study_time = db.query(func.sum(StudySession.duration)).filter(
            StudySession.student_id == current_user.id
        ).scalar() or 0
        
        avg_quiz_score = db.query(func.avg(QuizAttempt.percentage)).filter(
            QuizAttempt.student_id == current_user.id
        ).scalar() or 0
        
        return {
            "user_info": {
                "id": current_user.id,
                "username": current_user.username,
                "full_name": current_user.full_name,
                "jlpt_level": current_user.jlpt_level,
                "study_streak": current_user.study_streak
            },
            "study_statistics": {
                "total_study_time": total_study_time // 60,  # Convert to minutes
                "sessions_this_week": len([s for s in recent_sessions if s.started_at >= datetime.now() - timedelta(days=7)]),
                "average_quiz_score": round(avg_quiz_score, 1),
                "courses_enrolled": len(enrollments)
            },
            "recent_activity": [
                {
                    "id": session.id,
                    "type": session.session_type,
                    "duration": session.duration // 60,
                    "date": session.started_at,
                    "accuracy": session.accuracy_rate
                }
                for session in recent_sessions
            ],
            "course_progress": [
                {
                    "course_id": enrollment.course_id,
                    "course_title": enrollment.course.title,
                    "progress": enrollment.progress,
                    "grade": enrollment.grade
                }
                for enrollment in enrollments
            ],
            "weaknesses": [
                {
                    "concept": weakness.concept_name,
                    "type": weakness.concept_type,
                    "accuracy": weakness.accuracy_rate,
                    "recommendations": weakness.recommended_actions
                }
                for weakness in weaknesses[:5]  # Top 5 weaknesses
            ],
            "recent_quizzes": [
                {
                    "quiz_id": attempt.quiz_id,
                    "quiz_title": attempt.quiz.title,
                    "score": attempt.percentage,
                    "completed_at": attempt.completed_at
                }
                for attempt in recent_quizzes
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard data: {str(e)}"
        )

@router.get("/dashboard/teacher")
async def get_teacher_dashboard(
    current_user: User = Depends(get_current_active_teacher),
    db: Session = Depends(get_db)
):
    """Get comprehensive teacher dashboard analytics"""
    try:
        # Get teacher's courses
        courses = current_user.created_courses
        course_ids = [course.id for course in courses]
        
        # Get total students across all courses
        total_students = db.query(func.count(Enrollment.id)).filter(
            and_(
                Enrollment.course_id.in_(course_ids),
                Enrollment.is_active == True
            )
        ).scalar()
        
        # Get recent assignments submissions
        recent_submissions = db.query(AssignmentSubmission).join(
            AssignmentSubmission.assignment
        ).filter(
            AssignmentSubmission.assignment.has(course_id__in=course_ids)
        ).order_by(desc(AssignmentSubmission.submitted_at)).limit(20).all()
        
        # Get class performance statistics
        class_performance = []
        for course in courses:
            avg_score = db.query(func.avg(QuizAttempt.percentage)).join(
                QuizAttempt.quiz
            ).filter(
                QuizAttempt.quiz.has(course_id=course.id)
            ).scalar() or 0
            
            completion_rate = db.query(func.avg(Enrollment.progress)).filter(
                Enrollment.course_id == course.id
            ).scalar() or 0
            
            class_performance.append({
                "course_id": course.id,
                "course_title": course.title,
                "student_count": len(course.enrollments),
                "avg_score": round(avg_score, 1),
                "completion_rate": round(completion_rate, 1)
            })
        
        # Get common weaknesses across students
        common_weaknesses = db.query(
            WeaknessIdentification.concept_name,
            func.count(WeaknessIdentification.id).label('student_count'),
            func.avg(WeaknessIdentification.accuracy_rate).label('avg_accuracy')
        ).join(Enrollment, WeaknessIdentification.student_id == Enrollment.student_id).filter(
            and_(
                Enrollment.course_id.in_(course_ids),
                WeaknessIdentification.is_active == True
            )
        ).group_by(WeaknessIdentification.concept_name).order_by(
            desc('student_count')
        ).limit(10).all()
        
        return {
            "teacher_info": {
                "id": current_user.id,
                "full_name": current_user.full_name,
                "courses_count": len(courses)
            },
            "overview_stats": {
                "total_students": total_students,
                "total_courses": len(courses),
                "pending_submissions": len([s for s in recent_submissions if not s.is_graded]),
                "avg_class_performance": round(sum(cp['avg_score'] for cp in class_performance) / len(class_performance) if class_performance else 0, 1)
            },
            "class_performance": class_performance,
            "recent_submissions": [
                {
                    "student_name": submission.student.full_name,
                    "assignment_title": submission.assignment.title,
                    "course_title": submission.assignment.course.title,
                    "submitted_at": submission.submitted_at,
                    "is_graded": submission.is_graded,
                    "score": submission.grade_percentage
                }
                for submission in recent_submissions
            ],
            "common_weaknesses": [
                {
                    "concept": weakness.concept_name,
                    "affected_students": weakness.student_count,
                    "avg_accuracy": round(weakness.avg_accuracy, 1)
                }
                for weakness in common_weaknesses
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching teacher dashboard: {str(e)}"
        )

@router.get("/performance-trends")
async def get_performance_trends(
    days: int = Query(30, description="Number of days to analyze"),
    course_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance trends over time"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Base query for user's analytics
        query = db.query(LearningAnalytics).filter(
            and_(
                LearningAnalytics.student_id == current_user.id,
                LearningAnalytics.date >= start_date,
                LearningAnalytics.date <= end_date
            )
        )
        
        if course_id:
            query = query.filter(LearningAnalytics.course_id == course_id)
        
        analytics = query.order_by(LearningAnalytics.date).all()
        
        # Process trends
        trends = {
            "study_time": [],
            "quiz_scores": [],
            "engagement": [],
            "concepts_learned": []
        }
        
        for record in analytics:
            date_str = record.date.strftime("%Y-%m-%d")
            trends["study_time"].append({
                "date": date_str,
                "value": record.total_study_time
            })
            trends["quiz_scores"].append({
                "date": date_str,
                "value": record.average_score or 0
            })
            trends["engagement"].append({
                "date": date_str,
                "value": record.engagement_score or 0
            })
            trends["concepts_learned"].append({
                "date": date_str,
                "value": len(record.concepts_mastered or [])
            })
        
        return {
            "period": f"{days} days",
            "trends": trends,
            "summary": {
                "total_study_time": sum(t["value"] for t in trends["study_time"]),
                "avg_quiz_score": sum(t["value"] for t in trends["quiz_scores"]) / len(trends["quiz_scores"]) if trends["quiz_scores"] else 0,
                "avg_engagement": sum(t["value"] for t in trends["engagement"]) / len(trends["engagement"]) if trends["engagement"] else 0,
                "total_concepts": sum(t["value"] for t in trends["concepts_learned"])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching performance trends: {str(e)}"
        )

@router.get("/weaknesses")
async def get_student_weaknesses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed weakness analysis for student"""
    try:
        weaknesses = db.query(WeaknessIdentification).filter(
            WeaknessIdentification.student_id == current_user.id
        ).order_by(desc(WeaknessIdentification.last_updated)).all()
        
        # Group by concept type
        grouped_weaknesses = {}
        for weakness in weaknesses:
            concept_type = weakness.concept_type
            if concept_type not in grouped_weaknesses:
                grouped_weaknesses[concept_type] = []
            
            grouped_weaknesses[concept_type].append({
                "concept_name": weakness.concept_name,
                "description": weakness.description,
                "accuracy_rate": weakness.accuracy_rate,
                "total_attempts": weakness.total_attempts,
                "correct_attempts": weakness.correct_attempts,
                "difficulty_level": weakness.difficulty_level,
                "is_active": weakness.is_active,
                "improvement_trend": weakness.improvement_trend,
                "recommended_actions": weakness.recommended_actions,
                "error_patterns": weakness.error_patterns,
                "first_identified": weakness.first_identified,
                "last_updated": weakness.last_updated
            })
        
        return {
            "total_weaknesses": len([w for w in weaknesses if w.is_active]),
            "by_category": grouped_weaknesses,
            "improvement_summary": {
                "improving": len([w for w in weaknesses if w.improvement_trend == "Improving"]),
                "stable": len([w for w in weaknesses if w.improvement_trend == "Stable"]),
                "declining": len([w for w in weaknesses if w.improvement_trend == "Declining"])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching weaknesses: {str(e)}"
        )

@router.post("/track-study-session")
async def track_study_session(
    session_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track a study session for analytics"""
    try:
        study_session = StudySession(
            student_id=current_user.id,
            course_id=session_data.get("course_id"),
            session_type=session_data.get("session_type", "lesson"),
            duration=session_data.get("duration", 0),
            activities=session_data.get("activities", []),
            questions_answered=session_data.get("questions_answered", 0),
            correct_answers=session_data.get("correct_answers", 0),
            concepts_studied=session_data.get("concepts_studied", []),
            difficulty_level=session_data.get("difficulty_level", "medium")
        )
        
        # Calculate accuracy rate
        if study_session.questions_answered > 0:
            study_session.accuracy_rate = (study_session.correct_answers / study_session.questions_answered) * 100
        
        db.add(study_session)
        db.commit()
        
        # Update user's total study time
        current_user.total_study_time += session_data.get("duration", 0) // 60
        db.commit()
        
        # Trigger analytics processing in background
        await analytics_service.process_study_session(study_session.id)
        
        return {"message": "Study session tracked successfully", "session_id": study_session.id}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking study session: {str(e)}"
        )
