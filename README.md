# AI Educational Platform for Japanese Language Learning

An advanced AI-powered educational platform designed to help students learn Japanese through personalized instruction, RAG-based chat assistance, and comprehensive analytics.

## 🎌 Features

### Core Functionality
- **AI Chat Assistant**: RAG-powered conversational AI for answering Japanese language questions
- **Course Management**: Create, enroll, and manage Japanese language courses
- **Interactive Lessons**: Structured lessons with vocabulary, grammar points, and kanji
- **Assignments & Quizzes**: AI-generated and teacher-created assessments
- **Progress Tracking**: Detailed analytics and learning insights
- **JLPT Preparation**: Content organized by JLPT levels (N5-N1)

### AI Capabilities
- **RAG System**: Retrieval-Augmented Generation for accurate, context-aware responses
- **Multi-Model Support**: OpenAI GPT or HuggingFace models (DialoGPT, transformers)
- **Multilingual Embeddings**: Support for Japanese text processing
- **Personalized Learning**: Adaptive content based on user level and progress
- **Weakness Identification**: Automatic detection of learning gaps

### User Roles
- **Students**: Access courses, chat with AI, track progress
- **Teachers**: Create content, grade assignments, view analytics
- **Admin**: Platform management capabilities

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI/ML Stack**:
  - LlamaIndex (v0.9.48) for RAG
  - HuggingFace Transformers
  - Sentence Transformers for embeddings
  - OpenAI API (optional)
- **Vector Storage**: ChromaDB, FAISS
- **Caching**: Redis
- **Authentication**: JWT with passlib/bcrypt

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Routing**: React Router v6
- **State Management**: Zustand
- **UI Framework**: React Bootstrap 5
- **HTTP Client**: Axios
- **Build Tool**: Vite

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional, for caching)
- Conda (recommended) or pip

## 🚀 Installation

### Backend Setup

1. **Create Conda Environment**:
```bash
cd backend
conda env create -f ../environment.yml
conda activate ai-education
```

Or using pip:
```bash
pip install -r requirements.txt
```

2. **Configure Environment Variables**:
```bash
cp env.example .env
# Edit .env with your configuration
```

Required environment variables:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_education_db
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-key-here  # Optional
HUGGINGFACE_API_KEY=your-hf-key-here  # Optional
```

3. **Initialize Database**:
```bash
# Ensure PostgreSQL is running
createdb ai_education_db

# Run migrations (tables created automatically on startup)
python main.py
```

4. **Start Backend Server**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

### Frontend Setup

1. **Install Dependencies**:
```bash
cd frontend
npm install
```

2. **Configure Environment**:
```bash
# Create .env file if needed
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env
```

3. **Start Development Server**:
```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login (returns JWT token)
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/me` - Update user profile
- `POST /api/auth/change-password` - Change password

### Course Endpoints
- `GET /api/courses` - List courses
- `POST /api/courses` - Create course (teacher only)
- `GET /api/courses/{id}` - Get course details
- `POST /api/courses/{id}/enroll` - Enroll in course

### Lesson Endpoints
- `GET /api/lessons?course_id={id}` - Get course lessons
- `POST /api/lessons` - Create lesson (teacher only)
- `POST /api/lessons/{id}/complete` - Mark lesson complete

### Assignment Endpoints
- `GET /api/assignments` - List assignments
- `POST /api/assignments` - Create assignment (teacher only)
- `POST /api/assignments/{id}/submit` - Submit assignment
- `POST /api/assignments/{id}/grade` - Grade assignment (teacher only)

### RAG/AI Endpoints
- `POST /api/rag/chat` - Chat with AI assistant
- `POST /api/rag/generate-quiz` - Generate AI quiz (teacher only)
- `POST /api/rag/feedback` - Provide chat feedback
- `GET /api/rag/conversation-history` - Get chat history

### Analytics Endpoints
- `GET /api/analytics/dashboard/student` - Student dashboard
- `GET /api/analytics/dashboard/teacher` - Teacher dashboard
- `GET /api/analytics/performance-trends` - Performance trends
- `GET /api/analytics/weaknesses` - Student weaknesses
- `POST /api/analytics/track-study-session` - Track study session

## 🔧 Configuration

### RAG System Configuration
Edit `backend/app/core/config.py`:

```python
# Embedding Model
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"

# LLM Model (OpenAI or HuggingFace)
LLM_MODEL = "gpt-3.5-turbo"  # or "microsoft/DialoGPT-medium"
HF_MODEL_NAME = "microsoft/DialoGPT-medium"

# RAG Parameters
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K_RETRIEVAL = 5
```

### Database Models

Key models include:
- **User**: User accounts with roles and preferences
- **Course**: Course information and metadata
- **Lesson**: Individual lessons with content
- **Assignment**: Homework and projects
- **Quiz**: Assessment questions
- **ChatMessage**: AI chat history
- **LearningAnalytics**: Student progress data
- **WeaknessIdentification**: Learning gap analysis

## 📁 Project Structure

```
ai-education-platform/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # API endpoints
│   │   ├── core/              # Configuration & security
│   │   ├── db/                # Database setup
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   ├── data/                  # Japanese grammar data
│   ├── main.py               # FastAPI application
│   └── requirements.txt
├── frontend/
│   ├── public/               # Static files
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   ├── stores/           # State management
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
└── environment.yml           # Conda environment
```

## 🎯 Usage Examples

### Register a New Student
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "username": "student1",
    "full_name": "Test Student",
    "password": "password123",
    "role": "student",
    "jlpt_level": "N5"
  }'
```

### Chat with AI Assistant
```bash
curl -X POST http://localhost:8000/api/rag/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain the particle は (wa)",
    "message_type": "grammar"
  }'
```

## 🔒 Security

- JWT-based authentication with bcrypt password hashing
- CORS middleware for cross-origin requests
- SQL injection protection via SQLAlchemy ORM
- Environment-based configuration for sensitive data

## 🚢 Deployment

### Production Build (Frontend)
```bash
cd frontend
npm run build
# Serves from dist/ directory
```

### Docker Deployment (Future)
```bash
docker-compose up -d
```

---
