from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime
from app.db.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False ,unique=True, index=True)
    is_instructor = Column(Boolean, nullable=False)
    hashed_password = Column(String, nullable=False)


class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    num_students = Column(Integer, nullable=False)
    instructor_id = Column(Integer, nullable=False)


class Enrollment(Base):
    __tablename__ = 'enrollments'

    id = Column(Integer, primary_key=True, index=True)
    studentID = Column(Integer, nullable=False)
    courseID = Column(Integer, nullable=False)


class Assignment(Base):
    __tablename__ = 'assignments'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    grade = Column(Integer, nullable=False)
    attachmentID = Column(Integer, nullable=True)
    content = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=True)


class Submission(Base):
    __tablename__ = 'submissions'

    id = Column(Integer, primary_key=True, index=True)
    studentID = Column(Integer, nullable=False)
    assignmentID = Column(Integer, nullable=False)
    date_submitted = Column(DateTime, nullable=False)
    attachmentID = Column(Integer, nullable=True)
    content = Column(JSON, nullable=True)


class Grade(Base):
    __tablename__ = 'grades'

    id = Column(Integer, primary_key=True, index=True)
    submissionID = Column(Integer, nullable=False)
    grade = Column(Integer, nullable=False)


class Attachment(Base):
    __tablename__ = 'attachments'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    userID = Column(Integer, nullable=False)
    path = Column(String, unique=True, nullable=False)


class Announcement(Base):
    __tablename__ = 'announcements'

    id = Column(Integer, primary_key=True, index=True)
    courseID = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    date_announced = Column(DateTime, nullable=False)
    description = Column(String, nullable=False)
    attachmentID = Column(Integer, nullable=True)
    

class ChatSession(Base):
    __tablename__= 'chat_sessions'

    id = Column(Integer, primary_key=True, index=True)
    userID = Column(Integer, nullable=False)
    history = Column(JSON, nullable=False)



