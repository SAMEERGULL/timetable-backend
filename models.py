from sqlalchemy import Column, Integer, String, DateTime, Enum, Time, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

# Enum for user roles
class UserRole(enum.Enum):
    admin = "admin"
    manager = "manager"
    teacher = "teacher"
    student = "student"

# Institute model
class Institute(Base):
    __tablename__ = 'institutes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    total_semesters = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    users = relationship("User", back_populates="institute")
    departments = relationship("Department", back_populates="institute")
    teachers = relationship("Teacher", back_populates="institute")
    timetables = relationship("Timetable", back_populates="institute")

# User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # Store hashed password
    role = Column(Enum(UserRole), default=UserRole.manager)  # Corrected line
    phone_number = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    institute = relationship("Institute", back_populates="users")

# Department model
class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    institute = relationship("Institute", back_populates="departments")
    classes = relationship("Class", back_populates="department")
    subjects = relationship("Subject", back_populates="department")

# Class model
class Class(Base):
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey('departments.id'))
    name = Column(String)
    total_classes = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    department = relationship("Department", back_populates="classes")

# Subject model
class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey('departments.id'))
    semester = Column(Integer)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    department = relationship("Department", back_populates="subjects")

# Teacher model
class Teacher(Base):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    role = Column(Enum(UserRole), default=UserRole.teacher)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    institute = relationship("Institute", back_populates="teachers")

# Timetable model
class Timetable(Base):
    __tablename__ = 'timetable'

    id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    class_id = Column(Integer, ForeignKey('classes.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    day = Column(String)  # e.g., 'Monday', 'Tuesday', etc.
    start_time = Column(Time)
    end_time = Column(Time)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    institute = relationship("Institute", back_populates="timetables")
    user = relationship("User")
    class_ = relationship("Class")
    subject = relationship ("Subject")
    teacher = relationship("Teacher") 
# Continuing the Timetable model relationships
    teacher = relationship("Teacher")

