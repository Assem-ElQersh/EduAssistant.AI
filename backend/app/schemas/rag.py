from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    sessionID: int

class ChatResponse(BaseModel):
    response: str

class DocumentUpload(BaseModel):
    filename: str
    document_type: str 
