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

# Enum for shift
class Shift(enum.Enum):
    morning = "morning"
    evening = "evening"
    
# Institute model
class Institute(Base):
    __tablename__ = 'institutes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    users = relationship("User", back_populates="institute")
    departments = relationship("Department", back_populates="institute")
    semesters = relationship("Semester", back_populates="institute")
    classes = relationship("Class", back_populates="institute")
    subjects = relationship("Subject", back_populates="institute")
    teachers = relationship("Teacher", back_populates="institute")
    students = relationship("Student", back_populates="institute")
    timetables = relationship("Timetable", back_populates="institute")

# User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # Store hashed password
    role = Column(Enum(UserRole), default=UserRole.manager)
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
    total_classes = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    institute = relationship("Institute", back_populates="departments")
    semesters = relationship("Semester", back_populates="department")
    classes = relationship("Class", back_populates="department")
    subjects = relationship("Subject", back_populates="department")
    students = relationship("Student", back_populates="department")
    timetables = relationship("Timetable", back_populates="department")

# Semester model
class Semester(Base):
    __tablename__ = 'semesters'

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey('departments.id'))
    name = Column(String)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    institute = relationship("Institute", back_populates="semesters")
    department = relationship("Department", back_populates="semesters")
    timetables = relationship("Timetable", back_populates="semester")
    subjects = relationship("Subject", back_populates="semester")  

# Class model
class Class(Base):
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    name = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    institute = relationship("Institute", back_populates="classes")
    department = relationship("Department", back_populates="classes")
    timetables = relationship("Timetable", back_populates="class_")

# Subject model
class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))
    semester_id = Column(Integer, ForeignKey('semesters.id'))
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    institute = relationship("Institute", back_populates="subjects")
    department = relationship("Department", back_populates="subjects")
    semester = relationship("Semester", back_populates="subjects")
    timetables = relationship("Timetable", back_populates="subject")

# Teacher model
class Teacher(Base):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    password = Column(String)
    subject = Column(String)
    role = Column(Enum(UserRole), default=UserRole.teacher)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    institute = relationship("Institute", back_populates="teachers")
    timetables = relationship("Timetable", back_populates="teacher")

# Student model
class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.student)
    department_id = Column(Integer, ForeignKey('departments.id'))  
    shift = Column(Enum(Shift))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    institute = relationship("Institute", back_populates="students")
    department = relationship("Department", back_populates="students")

# Timetable model
class Timetable(Base):
    __tablename__ = 'timetables'

    id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    class_id = Column(Integer, ForeignKey('classes.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    day = Column(String)  
    class_time = Column(Time)
    semester_id = Column(Integer, ForeignKey('semesters.id'))
    shift = Column(Enum(Shift))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    institute = relationship("Institute", back_populates="timetables")
    department = relationship("Department", back_populates="timetables")
    semester = relationship("Semester", back_populates="timetables")
    class_ = relationship("Class", back_populates="timetables") 
    subject = relationship("Subject", back_populates="timetables")
    teacher = relationship("Teacher", back_populates="timetables")
