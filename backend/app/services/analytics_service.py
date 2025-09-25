import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.db.database import SessionLocal
from app.models.analytics import StudySession, LearningAnalytics, WeaknessIdentification
from app.models.quiz import QuizAttempt
from app.models.assignment import AssignmentSubmission
from app.models.user import User

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.db = SessionLocal()
    
    async def process_study_session(self, session_id: int):
        """Process a study session and update analytics"""
        try:
            session = self.db.query(StudySession).filter(StudySession.id == session_id).first()
            if not session:
                return
            
            # Update daily analytics
            await self._update_daily_analytics(session)
            
            # Identify potential weaknesses
            await self._analyze_weaknesses(session)
            
            # Update engagement metrics
            await self._update_engagement_metrics(session)
            
        except Exception as e:
            logger.error(f"Error processing study session {session_id}: {str(e)}")
        finally:
            self.db.close()
    
    async def _update_daily_analytics(self, session: StudySession):
        """Update daily learning analytics"""
        try:
            today = session.started_at.date()
            
            # Get or create daily analytics record
            daily_analytics = self.db.query(LearningAnalytics).filter(
                and_(
                    LearningAnalytics.student_id == session.student_id,
                    LearningAnalytics.date == today,
                    LearningAnalytics.course_id == session.course_id
                )
            ).first()
            
            if not daily_analytics:
                daily_analytics = LearningAnalytics(
                    student_id=session.student_id,
                    course_id=session.course_id,
                    date=today
                )
                self.db.add(daily_analytics)
            
            # Update metrics
            daily_analytics.total_study_time = (daily_analytics.total_study_time or 0) + (session.duration // 60)
            daily_analytics.sessions_count = (daily_analytics.sessions_count or 0) + 1
            
            # Update concepts studied
            if session.concepts_studied:
                existing_concepts = daily_analytics.concepts_mastered or []
                new_concepts = list(set(existing_concepts + session.concepts_studied))
                daily_analytics.concepts_mastered = new_concepts
            
            # Calculate engagement score based on session data
            engagement_score = self._calculate_engagement_score(session)
            daily_analytics.engagement_score = engagement_score
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating daily analytics: {str(e)}")
            self.db.rollback()
    
    async def _analyze_weaknesses(self, session: StudySession):
        """Analyze session for potential weaknesses"""
        try:
            if not session.concepts_studied or session.accuracy_rate is None:
                return
            
            # If accuracy is below threshold, identify potential weaknesses
            if session.accuracy_rate < 70:  # 70% threshold
                for concept in session.concepts_studied:
                    await self._update_weakness_record(
                        session.student_id,
                        concept,
                        session.course_id,
                        session.accuracy_rate,
                        session.questions_answered,
                        session.correct_answers
                    )
                    
        except Exception as e:
            logger.error(f"Error analyzing weaknesses: {str(e)}")
    
    async def _update_weakness_record(
        self,
        student_id: int,
        concept_name: str,
        course_id: int,
        accuracy_rate: float,
        total_attempts: int,
        correct_attempts: int
    ):
        """Update or create weakness identification record"""
        try:
            weakness = self.db.query(WeaknessIdentification).filter(
                and_(
                    WeaknessIdentification.student_id == student_id,
                    WeaknessIdentification.concept_name == concept_name,
                    WeaknessIdentification.course_id == course_id
                )
            ).first()
            
            if not weakness:
                # Determine concept type from name (simplified logic)
                concept_type = self._classify_concept_type(concept_name)
                
                weakness = WeaknessIdentification(
                    student_id=student_id,
                    course_id=course_id,
                    concept_name=concept_name,
                    concept_type=concept_type,
                    description=f"Difficulty with {concept_name}",
                    total_attempts=total_attempts,
                    correct_attempts=correct_attempts,
                    accuracy_rate=accuracy_rate
                )
                self.db.add(weakness)
            else:
                # Update existing record
                weakness.total_attempts += total_attempts
                weakness.correct_attempts += correct_attempts
                weakness.accuracy_rate = (weakness.correct_attempts / weakness.total_attempts) * 100
                
                # Update improvement trend
                previous_accuracy = weakness.accuracy_rate
                if accuracy_rate > previous_accuracy + 5:
                    weakness.improvement_trend = "Improving"
                elif accuracy_rate < previous_accuracy - 5:
                    weakness.improvement_trend = "Declining"
                else:
                    weakness.improvement_trend = "Stable"
                
                weakness.last_updated = datetime.utcnow()
            
            # Generate recommendations
            weakness.recommended_actions = self._generate_weakness_recommendations(
                concept_name, weakness.concept_type, accuracy_rate
            )
            
            # Mark as resolved if accuracy improves significantly
            if weakness.accuracy_rate > 85:
                weakness.is_active = False
                weakness.resolved_at = datetime.utcnow()
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating weakness record: {str(e)}")
            self.db.rollback()
    
    def _classify_concept_type(self, concept_name: str) -> str:
        """Classify concept type based on name"""
        concept_lower = concept_name.lower()
        
        if any(word in concept_lower for word in ["particle", "が", "を", "に", "で", "と"]):
            return "grammar"
        elif any(word in concept_lower for word in ["verb", "conjugation", "tense"]):
            return "grammar"
        elif any(word in concept_lower for word in ["kanji", "漢字"]):
            return "kanji"
        elif any(word in concept_lower for word in ["vocabulary", "vocab", "word"]):
            return "vocabulary"
        else:
            return "general"
    
    def _generate_weakness_recommendations(
        self, 
        concept_name: str, 
        concept_type: str, 
        accuracy_rate: float
    ) -> List[str]:
        """Generate personalized recommendations for weaknesses"""
        recommendations = []
        
        if concept_type == "grammar":
            recommendations.extend([
                f"Review {concept_name} grammar rules",
                "Practice with more example sentences",
                "Try pattern recognition exercises"
            ])
        elif concept_type == "vocabulary":
            recommendations.extend([
                f"Create flashcards for {concept_name}",
                "Practice using words in context",
                "Review word associations and mnemonics"
            ])
        elif concept_type == "kanji":
            recommendations.extend([
                f"Practice writing {concept_name} characters",
                "Study radical patterns",
                "Use spaced repetition for memorization"
            ])
        
        # Add difficulty-specific recommendations
        if accuracy_rate < 50:
            recommendations.append("Start with basic concepts and build gradually")
            recommendations.append("Consider reviewing prerequisite materials")
        elif accuracy_rate < 70:
            recommendations.append("Focus on consistent practice")
            recommendations.append("Try different learning approaches")
        
        return recommendations
    
    def _calculate_engagement_score(self, session: StudySession) -> float:
        """Calculate engagement score based on session metrics"""
        try:
            base_score = 50.0  # Base engagement score
            
            # Time factor (longer sessions = higher engagement, up to a point)
            time_minutes = session.duration // 60
            if time_minutes > 0:
                time_factor = min(time_minutes / 30, 2.0)  # Cap at 2x for 30+ minutes
                base_score += time_factor * 20
            
            # Accuracy factor
            if session.accuracy_rate is not None:
                accuracy_factor = session.accuracy_rate / 100
                base_score += accuracy_factor * 20
            
            # Activity diversity factor
            if session.activities:
                activity_factor = min(len(session.activities) / 5, 1.0)  # Cap at 5 activities
                base_score += activity_factor * 10
            
            # Cap at 100
            return min(base_score, 100.0)
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {str(e)}")
            return 50.0  # Default score
    
    async def _update_engagement_metrics(self, session: StudySession):
        """Update user engagement metrics"""
        try:
            user = self.db.query(User).filter(User.id == session.student_id).first()
            if not user:
                return
            
            # Update study streak
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            # Check if user studied yesterday
            yesterday_session = self.db.query(StudySession).filter(
                and_(
                    StudySession.student_id == session.student_id,
                    func.date(StudySession.started_at) == yesterday
                )
            ).first()
            
            if yesterday_session or user.last_login and user.last_login.date() == yesterday:
                user.study_streak += 1
            else:
                user.study_streak = 1  # Reset streak
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating engagement metrics: {str(e)}")
            self.db.rollback()
    
    async def generate_performance_insights(self, student_id: int, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive performance insights"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get recent analytics
            analytics = self.db.query(LearningAnalytics).filter(
                and_(
                    LearningAnalytics.student_id == student_id,
                    LearningAnalytics.date >= start_date
                )
            ).all()
            
            # Get recent quiz attempts
            quiz_attempts = self.db.query(QuizAttempt).filter(
                and_(
                    QuizAttempt.student_id == student_id,
                    QuizAttempt.completed_at >= start_date
                )
            ).all()
            
            # Calculate insights
            insights = {
                "study_consistency": self._analyze_study_consistency(analytics),
                "performance_trend": self._analyze_performance_trend(quiz_attempts),
                "learning_velocity": self._calculate_learning_velocity(analytics),
                "strength_areas": self._identify_strengths(student_id),
                "improvement_areas": self._identify_improvement_areas(student_id),
                "recommendations": self._generate_personalized_recommendations(
                    student_id, analytics, quiz_attempts
                )
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating performance insights: {str(e)}")
            return {}
    
    def _analyze_study_consistency(self, analytics: List[LearningAnalytics]) -> Dict[str, Any]:
        """Analyze study consistency patterns"""
        if not analytics:
            return {"score": 0, "pattern": "No data"}
        
        # Calculate consistency score based on regular study sessions
        total_days = len(analytics)
        study_days = len([a for a in analytics if a.total_study_time > 0])
        
        consistency_score = (study_days / max(total_days, 1)) * 100
        
        if consistency_score >= 80:
            pattern = "Highly consistent"
        elif consistency_score >= 60:
            pattern = "Moderately consistent"
        elif consistency_score >= 40:
            pattern = "Somewhat irregular"
        else:
            pattern = "Irregular"
        
        return {
            "score": round(consistency_score, 1),
            "pattern": pattern,
            "study_days": study_days,
            "total_days": total_days
        }
    
    def _analyze_performance_trend(self, quiz_attempts: List[QuizAttempt]) -> Dict[str, Any]:
        """Analyze performance trend over time"""
        if len(quiz_attempts) < 2:
            return {"trend": "Insufficient data", "change": 0}
        
        # Sort by completion date
        sorted_attempts = sorted(quiz_attempts, key=lambda x: x.completed_at)
        
        # Compare first half vs second half
        mid_point = len(sorted_attempts) // 2
        first_half_avg = sum(a.percentage for a in sorted_attempts[:mid_point]) / mid_point
        second_half_avg = sum(a.percentage for a in sorted_attempts[mid_point:]) / (len(sorted_attempts) - mid_point)
        
        change = second_half_avg - first_half_avg
        
        if change > 5:
            trend = "Improving"
        elif change < -5:
            trend = "Declining"
        else:
            trend = "Stable"
        
        return {
            "trend": trend,
            "change": round(change, 1),
            "recent_average": round(second_half_avg, 1),
            "overall_average": round(sum(a.percentage for a in sorted_attempts) / len(sorted_attempts), 1)
        }
    
    def _calculate_learning_velocity(self, analytics: List[LearningAnalytics]) -> Dict[str, Any]:
        """Calculate learning velocity (concepts learned per time unit)"""
        if not analytics:
            return {"velocity": 0, "assessment": "No data"}
        
        total_concepts = sum(len(a.concepts_mastered or []) for a in analytics)
        total_time = sum(a.total_study_time or 0 for a in analytics)
        
        if total_time == 0:
            velocity = 0
        else:
            velocity = total_concepts / (total_time / 60)  # Concepts per hour
        
        if velocity > 5:
            assessment = "Fast learner"
        elif velocity > 2:
            assessment = "Good pace"
        elif velocity > 1:
            assessment = "Steady progress"
        else:
            assessment = "Needs more practice"
        
        return {
            "velocity": round(velocity, 2),
            "assessment": assessment,
            "total_concepts": total_concepts,
            "total_hours": round(total_time / 60, 1)
        }
    
    def _identify_strengths(self, student_id: int) -> List[str]:
        """Identify student's strength areas"""
        # Get concepts with high accuracy
        strong_concepts = self.db.query(WeaknessIdentification.concept_name).filter(
            and_(
                WeaknessIdentification.student_id == student_id,
                WeaknessIdentification.accuracy_rate > 85,
                WeaknessIdentification.is_active == False  # Resolved weaknesses = strengths
            )
        ).limit(5).all()
        
        return [concept.concept_name for concept in strong_concepts]
    
    def _identify_improvement_areas(self, student_id: int) -> List[Dict[str, Any]]:
        """Identify areas needing improvement"""
        weak_areas = self.db.query(WeaknessIdentification).filter(
            and_(
                WeaknessIdentification.student_id == student_id,
                WeaknessIdentification.is_active == True,
                WeaknessIdentification.accuracy_rate < 70
            )
        ).order_by(WeaknessIdentification.accuracy_rate).limit(5).all()
        
        return [
            {
                "concept": area.concept_name,
                "type": area.concept_type,
                "accuracy": area.accuracy_rate,
                "priority": "High" if area.accuracy_rate < 50 else "Medium"
            }
            for area in weak_areas
        ]
    
    def _generate_personalized_recommendations(
        self,
        student_id: int,
        analytics: List[LearningAnalytics],
        quiz_attempts: List[QuizAttempt]
    ) -> List[str]:
        """Generate personalized study recommendations"""
        recommendations = []
        
        # Study time recommendations
        if analytics:
            avg_study_time = sum(a.total_study_time or 0 for a in analytics) / len(analytics)
            if avg_study_time < 30:  # Less than 30 minutes per day
                recommendations.append("Try to study for at least 30 minutes daily for better retention")
        
        # Performance recommendations
        if quiz_attempts:
            avg_score = sum(a.percentage for a in quiz_attempts) / len(quiz_attempts)
            if avg_score < 70:
                recommendations.append("Focus on reviewing incorrect answers to improve quiz performance")
        
        # Consistency recommendations
        study_days = len([a for a in analytics if a.total_study_time > 0])
        if study_days < len(analytics) * 0.6:  # Less than 60% consistency
            recommendations.append("Try to maintain a regular study schedule for better progress")
        
        return recommendations
