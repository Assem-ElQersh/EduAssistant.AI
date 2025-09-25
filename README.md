# AI Educational Platform - Competition Submission

## Overview
An AI-powered educational platform focused on Japanese language learning with comprehensive features for both students and educators.

## Core Features

### For Students
- **AI-Powered Learning Support**: On-demand explanations, summaries, and personalized study recommendations
- **Practice & Self-Assessment**: AI-generated quizzes, exercises, and practice questions
- **Assignment & Lesson Access**: View lessons, submit assignments, and receive real-time AI feedback

### For Educators
- **AI-Assisted Content Creation**: Generate exam questions, quizzes, and lesson summaries
- **Performance Analytics Dashboard**: Actionable insights into student progress and performance trends
- **Weakness Identification**: Identify struggling concepts for targeted intervention
- **Simplified Assignment & Resource Management**: Unified space for lessons, assignments, and announcements

## Technology Stack

### Backend
- **FastAPI**: High-performance API framework
- **PostgreSQL**: Primary database
- **RAG System**: Advanced retrieval-augmented generation with memory
- **LlamaIndex**: Document processing and embeddings
- **Authentication**: JWT-based auth system

### Frontend
- **React + TypeScript**: Modern UI framework
- **Tailwind CSS**: Styling
- **Recharts**: Analytics visualization
- **React Router**: Navigation

## Project Structure
```
CodeBase/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── public/
└── rag-system/
    ├── data/
    ├── models/
    └── pipeline/
```

## Getting Started

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Features Implementation Status
- [x] Basic project structure
- [ ] Authentication system
- [ ] RAG system with Japanese grammar
- [ ] Analytics dashboard
- [ ] Quiz generation
- [ ] Assignment management
- [ ] Performance tracking
