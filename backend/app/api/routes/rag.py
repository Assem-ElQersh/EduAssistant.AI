from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.analytics import ChatMessage
from app.services.rag_service import RAGService
from app.schemas.rag import ChatRequest, ChatResponse, DocumentUpload
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize RAG service
rag_service = RAGService()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with AI assistant for Japanese learning support"""
    try:
        # Get user's learning context
        user_context = {
            "jlpt_level": current_user.jlpt_level,
            "learning_preferences": current_user.learning_preferences,
            "role": current_user.role.value
        }
        
        # Generate AI response using RAG
        response_data = await rag_service.generate_response(
            query=chat_request.message,
            user_context=user_context,
            course_id=chat_request.course_id,
            conversation_history=chat_request.conversation_history
        )
        
        # Save chat message to database
        chat_message = ChatMessage(
            user_id=current_user.id,
            course_id=chat_request.course_id,
            message=chat_request.message,
            response=response_data["response"],
            message_type=chat_request.message_type,
            context_data=response_data.get("context"),
            source_documents=response_data.get("sources"),
            confidence_score=response_data.get("confidence"),
            grammar_topic=response_data.get("grammar_topic"),
            vocabulary_topic=response_data.get("vocabulary_topic"),
            jlpt_level=response_data.get("jlpt_level")
        )
        
        db.add(chat_message)
        db.commit()
        
        # Update user analytics in background
        background_tasks.add_task(
            rag_service.update_user_analytics,
            current_user.id,
            chat_request.message_type,
            response_data
        )
        
        return ChatResponse(
            message_id=chat_message.id,
            response=response_data["response"],
            sources=response_data.get("sources", []),
            confidence=response_data.get("confidence", 0.0),
            grammar_points=response_data.get("grammar_points", []),
            vocabulary=response_data.get("vocabulary", []),
            recommendations=response_data.get("recommendations", [])
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI response"
        )

@router.post("/feedback")
async def provide_chat_feedback(
    message_id: int,
    rating: int,
    was_helpful: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Provide feedback on AI response"""
    chat_message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.user_id == current_user.id
    ).first()
    
    if not chat_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat message not found"
        )
    
    chat_message.user_rating = rating
    chat_message.was_helpful = was_helpful
    db.commit()
    
    return {"message": "Feedback recorded successfully"}

@router.get("/conversation-history")
async def get_conversation_history(
    course_id: Optional[int] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's conversation history"""
    query = db.query(ChatMessage).filter(ChatMessage.user_id == current_user.id)
    
    if course_id:
        query = query.filter(ChatMessage.course_id == course_id)
    
    messages = query.order_by(ChatMessage.created_at.desc()).limit(limit).all()
    
    return {
        "messages": [
            {
                "id": msg.id,
                "message": msg.message,
                "response": msg.response,
                "message_type": msg.message_type,
                "created_at": msg.created_at,
                "rating": msg.user_rating,
                "was_helpful": msg.was_helpful
            }
            for msg in messages
        ]
    }

@router.post("/generate-quiz")
async def generate_ai_quiz(
    topic: str,
    difficulty: str = "medium",
    num_questions: int = 10,
    question_types: List[str] = ["multiple_choice"],
    jlpt_level: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Generate AI-powered quiz questions"""
    if current_user.role.value != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can generate quizzes"
        )
    
    try:
        quiz_data = await rag_service.generate_quiz(
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
            question_types=question_types,
            jlpt_level=jlpt_level or current_user.jlpt_level
        )
        
        return quiz_data
        
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quiz"
        )

@router.post("/generate-lesson-summary")
async def generate_lesson_summary(
    lesson_content: str,
    target_level: str = "intermediate",
    current_user: User = Depends(get_current_user)
):
    """Generate AI-powered lesson summary"""
    if current_user.role.value != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can generate lesson summaries"
        )
    
    try:
        summary_data = await rag_service.generate_lesson_summary(
            content=lesson_content,
            target_level=target_level,
            jlpt_level=current_user.jlpt_level
        )
        
        return summary_data
        
    except Exception as e:
        logger.error(f"Error generating lesson summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate lesson summary"
        )

@router.post("/upload-documents")
async def upload_documents(
    documents: List[DocumentUpload],
    current_user: User = Depends(get_current_user)
):
    """Upload and process documents for RAG system"""
    if current_user.role.value != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can upload documents"
        )
    
    try:
        results = []
        for doc in documents:
            result = await rag_service.process_document(
                content=doc.content,
                filename=doc.filename,
                document_type=doc.document_type,
                metadata=doc.metadata
            )
            results.append(result)
        
        return {"processed_documents": results}
        
    except Exception as e:
        logger.error(f"Error uploading documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process documents"
        )

@router.get("/system-status")
async def get_rag_system_status():
    """Get RAG system status and statistics"""
    try:
        status_data = await rag_service.get_system_status()
        return status_data
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system status"
        )
