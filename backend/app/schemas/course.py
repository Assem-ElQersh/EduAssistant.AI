from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CourseBase(BaseModel):
    name: str
    description: str
    num_students: int
    instructor_id: int

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    pass

class CourseResponse(CourseBase):
    class Config:
        from_attributes = True


class CourseEnroll(BaseModel):
    studentID: int
    courseID: int

class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    
    class Config:
        from_attributes = True
