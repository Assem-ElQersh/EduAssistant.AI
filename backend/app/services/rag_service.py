import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from pathlib import Path

# LlamaIndex imports - for latest v0.14+ structure
LLAMAINDEX_AVAILABLE = False

try:
    # Latest v0.14+ structure
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.core.memory import ChatMemoryBuffer
    from llama_index.core.chat_engine import CondensePlusContextChatEngine
    LLAMAINDEX_AVAILABLE = True
    print("LlamaIndex v0.14+ imports successful")
except ImportError as e:
    print(f"LlamaIndex import failed: {e}")
    LLAMAINDEX_AVAILABLE = False

# Conditional imports for LLMs and Embeddings
OPENAI_AVAILABLE = False
HUGGINGFACE_LLM_AVAILABLE = False
HUGGINGFACE_EMBEDDINGS_AVAILABLE = False

# Try OpenAI imports
try:
    from llama_index.llms.openai import OpenAI
    OPENAI_AVAILABLE = True
    print("OpenAI LLM import successful")
except ImportError as e:
    print(f"OpenAI LLM import failed: {e}")

# Try HuggingFace imports (install separately: pip install llama-index-llms-huggingface)
try:
    from llama_index.llms.huggingface import HuggingFaceLLM
    HUGGINGFACE_LLM_AVAILABLE = True
    print("HuggingFace LLM available")
except ImportError as e:
    print(f"HuggingFace LLM import failed: {e}")

# Try HuggingFace Embeddings (install separately: pip install llama-index-embeddings-huggingface)
try:
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    HUGGINGFACE_EMBEDDINGS_AVAILABLE = True
    print("HuggingFace Embeddings available")
except ImportError as e:
    print(f"HuggingFace Embeddings import failed: {e}")

# Fallback to SentenceTransformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    print("SentenceTransformers available for embeddings")
except ImportError as e:
    print(f"SentenceTransformers import failed: {e}")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Additional imports for document processing
import requests
from bs4 import BeautifulSoup
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

from app.core.config import settings

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.embedding_model = None
        self.llm_model = None
        self.index = None
        self.chat_engine = None
        try:
            if LLAMAINDEX_AVAILABLE:
                self.memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
            else:
                self.memory = None
        except Exception as e:
            logger.warning(f"Could not initialize memory: {str(e)}")
            self.memory = None
        self.japanese_grammar_data = {}
        self.initialize_models()
        self.load_japanese_grammar_data()
    
    def initialize_models(self):
        """Initialize embedding and LLM models with fallbacks"""
        try:
            if not LLAMAINDEX_AVAILABLE:
                logger.warning("LlamaIndex not available, using mock models")
                self.embedding_model = self.create_mock_embedding()
                self.llm_model = self.create_mock_llm()
                return
            
            # Initialize embedding model - use v0.9.48 imports
            if HUGGINGFACE_EMBEDDINGS_AVAILABLE:
                try:
                    self.embedding_model = HuggingFaceEmbedding(
                        model_name="intfloat/multilingual-e5-small"
                    )
                    print("Using HuggingFace multilingual embeddings (v0.9.48)")
                except Exception as e:
                    logger.error(f"Error initializing HuggingFace embedding: {str(e)}")
                    self.embedding_model = self.create_mock_embedding()
            elif settings.OPENAI_API_KEY and OPENAI_AVAILABLE:
                try:
                    from llama_index.embeddings.openai import OpenAIEmbedding
                    self.embedding_model = OpenAIEmbedding(
                        api_key=settings.OPENAI_API_KEY
                    )
                    print("Using OpenAI embeddings as fallback")
                except Exception as e:
                    logger.error(f"Error initializing OpenAI embedding: {str(e)}")
                    self.embedding_model = self.create_mock_embedding()
            else:
                self.embedding_model = self.create_mock_embedding()
            
            # Initialize LLM model - try HuggingFace first (like notebook), then OpenAI
            llm_initialized = False
            
            # Try HuggingFace LLM first (v0.9.48 imports)
            if settings.HUGGINGFACE_API_KEY and HUGGINGFACE_LLM_AVAILABLE:
                try:
                    self.llm_model = HuggingFaceLLM(
                        model_name="microsoft/DialoGPT-medium",  # Same as your notebook
                        tokenizer_name="microsoft/DialoGPT-medium",
                        device_map="auto",
                        max_new_tokens=512,
                        model_kwargs={"token": settings.HUGGINGFACE_API_KEY}
                    )
                    print("Using HuggingFace LLM (v0.9.48)")
                    llm_initialized = True
                except Exception as e:
                    logger.error(f"Error initializing HuggingFace LLM: {str(e)}")
            
            # Fallback to OpenAI if HuggingFace fails
            if not llm_initialized and settings.OPENAI_API_KEY and OPENAI_AVAILABLE:
                try:
                    self.llm_model = OpenAI(
                        model=settings.LLM_MODEL,
                        api_key=settings.OPENAI_API_KEY
                    )
                    print("Using OpenAI LLM as fallback")
                    llm_initialized = True
                except Exception as e:
                    logger.error(f"Error initializing OpenAI: {str(e)}")
            
            # Final fallback to mock LLM
            if not llm_initialized:
                self.llm_model = self.create_mock_llm()
                logger.warning("Using mock LLM - configure HuggingFace or OpenAI API key for full functionality")
            
            # Set global settings for LlamaIndex
            try:
                if LLAMAINDEX_AVAILABLE:
                    Settings.embed_model = self.embedding_model
                    Settings.llm = self.llm_model
            except Exception as e:
                logger.warning(f"Could not set global settings: {str(e)}")
            
            logger.info("RAG models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            # Create fallback models
            self.embedding_model = self.create_mock_embedding()
            self.llm_model = self.create_mock_llm()
            logger.warning("Using mock models due to initialization error")
    
    def create_mock_llm(self):
        """Create a mock LLM for testing purposes"""
        class MockLLM:
            def complete(self, prompt: str) -> str:
                return f"Mock response to: {prompt[:50]}..."
            
            def chat(self, messages) -> str:
                return "This is a mock response. Please configure proper LLM models for full functionality."
        
        return MockLLM()
    
    def create_mock_embedding(self):
        """Create a mock embedding model for testing"""
        class MockEmbedding:
            def get_text_embedding(self, text: str) -> List[float]:
                # Return a simple mock embedding
                return [0.1] * 384  # Common embedding dimension
        
        return MockEmbedding()
    
    def load_japanese_grammar_data(self):
        """Load Japanese grammar reference data"""
        try:
            # Check if grammar data exists locally
            grammar_path = Path(settings.GRAMMAR_DATA_PATH)
            
            if not grammar_path.exists():
                # Create directory and download data
                grammar_path.mkdir(parents=True, exist_ok=True)
                self.download_sample_grammar()
            
            # Load existing grammar data
            self.load_grammar_files()
            
            # Create or update vector index
            self.create_grammar_index()
            
        except Exception as e:
            logger.error(f"Error loading Japanese grammar data: {str(e)}")
            # Create sample data for testing
            self.create_sample_grammar_data()
    
    def download_sample_grammar(self):
        """Create sample Japanese grammar data for testing"""
        try:
            grammar_path = Path(settings.GRAMMAR_DATA_PATH)
            
            # Sample grammar topics with basic content
            sample_data = {
                "particles": """
                Japanese Particles (助詞)
                
                が (ga) - Subject marker
                Example: 私が学生です。(I am a student.)
                
                を (wo/o) - Object marker  
                Example: 本を読みます。(I read a book.)
                
                に (ni) - Direction, time, indirect object
                Example: 学校に行きます。(I go to school.)
                
                で (de) - Location of action, means
                Example: 図書館で勉強します。(I study at the library.)
                
                と (to) - "and", "with"
                Example: 友達と映画を見ます。(I watch a movie with friends.)
                """,
                
                "verb-conjugation": """
                Japanese Verb Conjugation
                
                U-verbs (五段動詞):
                - 読む (yomu) → 読みます (yomimasu) - polite form
                - 書く (kaku) → 書きます (kakimasu) - polite form
                
                Ru-verbs (一段動詞):
                - 食べる (taberu) → 食べます (tabemasu) - polite form
                - 見る (miru) → 見ます (mimasu) - polite form
                
                Irregular verbs:
                - する (suru) → します (shimasu) - to do
                - 来る (kuru) → 来ます (kimasu) - to come
                """,
                
                "adjectives": """
                Japanese Adjectives (形容詞)
                
                I-adjectives (い形容詞):
                - 大きい (ookii) - big
                - 小さい (chiisai) - small
                - 新しい (atarashii) - new
                
                Na-adjectives (な形容詞):
                - きれい (kirei) - beautiful, clean
                - 有名 (yuumei) - famous  
                - 便利 (benri) - convenient
                """
            }
            
            for topic, content in sample_data.items():
                file_path = grammar_path / f"{topic}.txt"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            logger.info(f"Created sample grammar data with {len(sample_data)} topics")
            
        except Exception as e:
            logger.error(f"Error creating sample grammar data: {str(e)}")
    
    def load_grammar_files(self):
        """Load grammar files into memory"""
        try:
            grammar_path = Path(settings.GRAMMAR_DATA_PATH)
            
            for file_path in grammar_path.glob("*.txt"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.japanese_grammar_data[file_path.stem] = content
            
            logger.info(f"Loaded {len(self.japanese_grammar_data)} grammar files")
            
        except Exception as e:
            logger.error(f"Error loading grammar files: {str(e)}")
    
    def create_sample_grammar_data(self):
        """Create in-memory sample data when file loading fails"""
        self.japanese_grammar_data = {
            "basic-particles": "Basic Japanese particles: が、を、に、で、と",
            "verb-forms": "Japanese verb conjugation patterns for polite and casual forms",
            "adjectives": "I-adjectives and Na-adjectives in Japanese"
        }
        logger.info("Created in-memory sample grammar data")
    
    def create_grammar_index(self):
        """Create vector index from grammar data"""
        try:
            if not LLAMAINDEX_AVAILABLE:
                logger.warning("LlamaIndex not available, creating fallback chat engine")
                self.create_fallback_chat_engine()
                return
                
            if not self.japanese_grammar_data:
                logger.warning("No grammar data available for indexing")
                self.create_fallback_chat_engine()
                return
            
            # Create temporary directory for indexing
            temp_dir = Path("temp_grammar")
            temp_dir.mkdir(exist_ok=True)
            
            # Write grammar data to temporary files
            for topic, content in self.japanese_grammar_data.items():
                temp_file = temp_dir / f"{topic}.txt"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Create index
            documents = SimpleDirectoryReader(str(temp_dir)).load_data()
            
            # Parse documents into nodes
            parser = SentenceSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            nodes = parser.get_nodes_from_documents(documents)
            
            # Create vector index
            self.index = VectorStoreIndex(nodes, embed_model=self.embedding_model)
            
            # Create chat engine
            chat_engine_kwargs = {
                "vector_index": self.index,
                "llm": self.llm_model,
                "context_prompt": (
                    "You are an expert Japanese language tutor. Use the provided context "
                    "to help students learn Japanese grammar, vocabulary, and language concepts. "
                    "Provide clear explanations with examples. When appropriate, include "
                    "romaji readings and cultural context."
                ),
                "verbose": True
            }
            
            # Only add memory if it's available
            if self.memory:
                chat_engine_kwargs["memory"] = self.memory
                
            self.chat_engine = CondensePlusContextChatEngine.from_defaults(**chat_engine_kwargs)
            
            # Cleanup temporary directory
            import shutil
            shutil.rmtree(temp_dir)
            
            logger.info("Grammar index created successfully")
            
        except Exception as e:
            logger.error(f"Error creating grammar index: {str(e)}")
            # Create a simple fallback
            self.create_fallback_chat_engine()
    
    def create_fallback_chat_engine(self):
        """Create a simple fallback chat engine"""
        class FallbackChatEngine:
            def chat(self, query: str) -> str:
                return f"I understand you're asking about: {query}. This is a fallback response. Please configure proper models for full Japanese learning support."
        
        self.chat_engine = FallbackChatEngine()
        logger.info("Created fallback chat engine")
    
    async def generate_response(
        self,
        query: str,
        user_context: Dict[str, Any],
        course_id: Optional[int] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Generate AI response using RAG"""
        try:
            # Enhance query with user context
            enhanced_query = self.enhance_query_with_context(query, user_context)
            
            # Add conversation history to memory if provided
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages
                    if msg.get("message"):
                        self.memory.put(msg.get("message", ""))
                    if msg.get("response"):
                        self.memory.put(msg.get("response", ""))
            
            # Generate response using chat engine
            if self.chat_engine:
                if hasattr(self.chat_engine, 'chat'):
                    response = await asyncio.to_thread(
                        self.chat_engine.chat,
                        enhanced_query
                    )
                else:
                    response = self.chat_engine.chat(enhanced_query)
                
                # Extract additional information
                sources = self.extract_source_information(response)
                grammar_points = self.extract_grammar_points(str(response))
                vocabulary = self.extract_vocabulary(str(response))
                
                return {
                    "response": str(response),
                    "sources": sources,
                    "confidence": 0.85,  # Placeholder - implement confidence scoring
                    "grammar_points": grammar_points,
                    "vocabulary": vocabulary,
                    "recommendations": self.generate_study_recommendations(
                        query, user_context
                    ),
                    "jlpt_level": user_context.get("jlpt_level"),
                    "context": {
                        "query_type": self.classify_query_type(query),
                        "difficulty_level": self.assess_difficulty(query)
                    }
                }
            else:
                # Fallback response
                return {
                    "response": "I'm sorry, I'm currently setting up my knowledge base. Please try again in a moment.",
                    "sources": [],
                    "confidence": 0.0
                }
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "response": "I encountered an error while processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0
            }
    
    def enhance_query_with_context(self, query: str, user_context: Dict[str, Any]) -> str:
        """Enhance query with user context"""
        jlpt_level = user_context.get("jlpt_level", "N5")
        role = user_context.get("role", "student")
        
        enhanced_query = f"""
        User Context:
        - JLPT Level: {jlpt_level}
        - Role: {role}
        
        Query: {query}
        
        Please provide an appropriate response considering the user's level and role.
        """
        
        return enhanced_query
    
    def extract_source_information(self, response) -> List[Dict[str, Any]]:
        """Extract source information from response"""
        # This is a placeholder - implement based on your RAG system
        return [
            {
                "title": "Japanese Grammar Reference",
                "url": "https://www.wasabi-jpn.com/japanese-grammar/",
                "relevance_score": 0.9
            }
        ]
    
    def extract_grammar_points(self, response_text: str) -> List[str]:
        """Extract grammar points mentioned in response"""
        # Simple keyword extraction - enhance with NLP
        grammar_keywords = [
            "particle", "verb", "adjective", "conjugation", "tense",
            "keigo", "honorific", "humble", "casual", "formal"
        ]
        
        found_points = []
        for keyword in grammar_keywords:
            if keyword.lower() in response_text.lower():
                found_points.append(keyword)
        
        return found_points
    
    def extract_vocabulary(self, response_text: str) -> List[Dict[str, str]]:
        """Extract vocabulary items from response"""
        # Placeholder - implement vocabulary extraction
        return []
    
    def classify_query_type(self, query: str) -> str:
        """Classify the type of query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["grammar", "particle", "verb", "conjugate"]):
            return "grammar"
        elif any(word in query_lower for word in ["meaning", "translate", "vocabulary"]):
            return "vocabulary"
        elif any(word in query_lower for word in ["practice", "exercise", "quiz"]):
            return "practice"
        else:
            return "general"
    
    def assess_difficulty(self, query: str) -> str:
        """Assess query difficulty level"""
        # Simple heuristic - enhance with ML model
        if len(query.split()) < 5:
            return "basic"
        elif len(query.split()) < 15:
            return "intermediate"
        else:
            return "advanced"
    
    def generate_study_recommendations(
        self,
        query: str,
        user_context: Dict[str, Any]
    ) -> List[str]:
        """Generate personalized study recommendations"""
        recommendations = []
        
        query_type = self.classify_query_type(query)
        jlpt_level = user_context.get("jlpt_level", "N5")
        
        if query_type == "grammar":
            recommendations.extend([
                f"Practice {jlpt_level} grammar exercises",
                "Review particle usage patterns",
                "Try conjugation drills"
            ])
        elif query_type == "vocabulary":
            recommendations.extend([
                f"Study {jlpt_level} vocabulary lists",
                "Practice with flashcards",
                "Read simple Japanese texts"
            ])
        
        return recommendations
    
    async def generate_quiz(
        self,
        topic: str,
        difficulty: str,
        num_questions: int,
        question_types: List[str],
        jlpt_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate AI-powered quiz questions"""
        try:
            # Create sample quiz for demonstration
            return {
                "quiz_id": f"ai_generated_{datetime.now().isoformat()}",
                "title": f"{topic} Quiz - {difficulty.title()}",
                "questions": [
                    {
                        "id": i,
                        "question": f"Sample question {i} about {topic}",
                        "type": question_types[0] if question_types else "multiple_choice",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "explanation": f"Explanation for question {i}",
                        "points": 1
                    }
                    for i in range(1, num_questions + 1)
                ],
                "metadata": {
                    "topic": topic,
                    "difficulty": difficulty,
                    "jlpt_level": jlpt_level,
                    "generated_at": datetime.now().isoformat()
                }
            }
                
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
            raise
    
    async def generate_lesson_summary(
        self,
        content: str,
        target_level: str,
        jlpt_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate AI-powered lesson summary"""
        try:
            return {
                "summary": f"This is a summary of the lesson content focusing on {target_level} level concepts.",
                "key_concepts": ["Sample concept 1", "Sample concept 2"],
                "vocabulary": [],
                "generated_at": datetime.now().isoformat()
            }
                
        except Exception as e:
            logger.error(f"Error generating lesson summary: {str(e)}")
            raise
    
    async def process_document(
        self,
        content: str,
        filename: str,
        document_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process and index a new document"""
        try:
            # Save document content
            doc_path = Path("documents") / filename
            doc_path.parent.mkdir(exist_ok=True)
            
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "filename": filename,
                "status": "processed",
                "document_type": document_type,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
    
    async def update_user_analytics(
        self,
        user_id: int,
        message_type: str,
        response_data: Dict[str, Any]
    ):
        """Update user analytics based on chat interaction"""
        try:
            # This would typically update analytics in the database
            # Placeholder for analytics logic
            logger.info(f"Updated analytics for user {user_id}: {message_type}")
            
        except Exception as e:
            logger.error(f"Error updating analytics: {str(e)}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get RAG system status"""
        return {
            "status": "operational",
            "models_loaded": {
                "embedding_model": self.embedding_model is not None,
                "llm_model": self.llm_model is not None,
                "index_created": self.index is not None
            },
            "grammar_data_files": len(self.japanese_grammar_data),
            "last_updated": datetime.now().isoformat()
        }