from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import JSONResponse  
from pydantic import BaseModel, EmailStr
from typing import List, Annotated,Dict
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.middleware.cors import CORSMiddleware
# import bcrypt
import random
import pandas as pd
import string
from passlib.context import CryptContext
from io import BytesIO
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContactMessage(BaseModel):
    name: str
    phone: str
    email: str
    message: str

class InstituteCreate(BaseModel):
    name: str
    # total_semesters: int
    admin_name: str
    admin_email: EmailStr
    admin_password: str
    admin_phone_number: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ManagerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    institute_id: int  # Link to the specific institute

class InstituteRequest(BaseModel):
    institute_id: int

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    role: str  # You can also define this as an Enum if you have specific roles

class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    phone: str

class TeacherCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    subject: str
    institute_id: int

class UpdateTeacherRequest(BaseModel):
    institute_id: int
    teacher_id: int
    name: str
    email: str
    phone_number: str
    subject: str

class TimetableEntry(BaseModel):
    class_name: str
    subject: str
    teacher: str
    time: str

class TimetableRequest(BaseModel):
    institute_id: int
    department_id: int
    semester_id: int
    timetable: Dict[str, List[TimetableEntry]]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def send_email(contact: ContactMessage):
    sender_email = "universalsmarttimetable@gmail.com" 
    sender_password = "kyif abme qpyf wrsg"  
    receiver_email = "sameergulsher0000@gmail.com"

    # Create the email content
    subject = f"Message from {contact.name}"
    body = f"Name: {contact.name}\nNumber: {contact.phone}\nEmail: {contact.email}\nMessage: {contact.message}"

    # Set up the email server
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the Gmail SMTP server and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465 ) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

#for admin
def generate_dummy_password(length=8):
    """Generate a random dummy password of a given length."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def send_dummy_password_email(receiver_email: str, dummy_password: str):
    sender_email = "universalsmarttimetable@gmail.com"  # Replace with your Gmail address
    sender_password = "kyif abme qpyf wrsg"  # Replace with your App Password

    # Create the email content
    subject = "Your Dummy Password"
    body = f"Your new dummy password is: {dummy_password}"

    # Set up the email server
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the Gmail SMTP server and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465 ) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

#for managers
def manager_generate_dummy_password(length=8):
    """Generate a random dummy password of a given length."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def manager_send_dummy_password_email(receiver_email: str, dummy_password: str, manager_name: str):
    sender_email = "universalsmarttimetable@gmail.com"  # Replace with your Gmail address
    sender_password = "kyif abme qpyf wrsg"  # Replace with your App Password

    # Create the email content
    subject = "Welcome to the Institute - Manager Role Assigned"
    body = f"Dear {manager_name},\n\nYou have been added as a manager to the institute account.\n" \
           f"Your login details are as follows:\n" \
           f"Email: {receiver_email}\n" \
           f"Dummy Password: {dummy_password}\n\n" \
           f"Please log in and change your password as soon as possible.\n\nBest regards,\nThe Institute Team"

    # Set up the email server
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the Gmail SMTP server and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465 ) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def teacher_send_email(to_email, password):
    sender_email = "universalsmarttimetable@gmail.com"
    sender_password = "kyif abme qpyf wrsg"  # Be careful with your passwords; ideally use environment variables
    subject = "Access to View Timetable"
    body = f"You have been given access to view the timetable. Your credentials are:\nEmail: {to_email}\nPassword: {password}"
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
        return False


@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}

#Contact us api
@app.post("/send-message/")
def send_message(contact: ContactMessage):
    if send_email(contact):
        return {"status": "success", "message": "Email sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send email")

#api for registering an admin
@app.post("/register-institute/")
def register_institute(institute_data: InstituteCreate, db: Session = Depends(get_db)):
    # Check if the admin user already exists
    existing_admin = db.query(models.User).filter(models.User.email == institute_data.admin_email).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin user already exists")

    # Create the institute
    new_institute = models.Institute(
        name=institute_data.name,
    )
    db.add(new_institute)
    db.commit()
    db.refresh(new_institute)

    # Hash the password
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(institute_data.admin_password)
    print(f"Hashed Password: {hashed_password}")  # Debugging

    # Create the admin user
    new_admin = models.User(
        institute_id=new_institute.id,
        name=institute_data.admin_name,
        email=institute_data.admin_email,
        password=hashed_password,
        role=models.UserRole.admin,
        phone_number=institute_data.admin_phone_number
    )
    print(new_admin.__dict__)  # Debugging

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {"status": "success", "message": "Institute and admin user created successfully"}

#admin login api
@app.post("/admin-login/")
def admin_login(login_data: AdminLogin, db: Session = Depends(get_db)):
    # Query the user by email
    admin_user = db.query(models.User).filter(models.User.email == login_data.email).first()
    # Check if the user exists
    if not admin_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    # Check if the password is correct
    # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # login_password = pwd_context.hash(login_data.password)
    # if not pwd_context.verify(login_password, admin_user.password):
    #     raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # If the credentials are valid, return a success message
    return {"status": "success", "message": "Login successful", "user_id": admin_user.id, "role": admin_user.role, "institute_id":admin_user.institute_id} ### Summary of the API for Admin Login

@app.post("/forgot-password/")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Check if the admin user exists with the provided email
    admin_user = db.query(models.User).filter(models.User.email == request.email).first()
    
    if not admin_user:
        raise HTTPException(status_code=404, detail="Email not found")

    # Generate a dummy password
    dummy_password = generate_dummy_password()

    # Send the dummy password to the user's email
    if send_dummy_password_email(request.email, dummy_password):
        # Optionally, you can update the user's password in the database
        admin_user.password = dummy_password
        db.commit()
        return {"status": "success", "message": "Dummy password sent to your email"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send email")

@app.post("/add-manager/")
def add_manager(manager_data: ManagerCreate, db: Session = Depends(get_db)):
    # Check if the institute exists
    institute = db.query(models.Institute).filter(models.Institute.id == manager_data.institute_id).first()
    if not institute:
        raise HTTPException(status_code=404, detail="Institute not found")

    dummy_password = manager_generate_dummy_password()

    # Create the manager user
    new_manager = models.User(
        name=manager_data.name,
        email=manager_data.email,
        phone_number=manager_data.phone,
        role=models.UserRole.manager,  # Assuming UserRole is an Enum and has a 'manager' role
        institute_id=manager_data.institute_id,  # Associate with the correct institute
        password=dummy_password  # Store the dummy password directly (hashed later)
    )

    db.add(new_manager)
    db.commit()
    db.refresh(new_manager)

    if manager_send_dummy_password_email(manager_data.email, dummy_password, manager_data.name):
        # Hash the dummy password before storing it in the database
        new_manager.password = dummy_password
        db.commit()  # Commit the changes to the database
    else:
        raise HTTPException(status_code=500, detail="Failed to send email to the manager")

    return {"status": "success", "message": "Manager added successfully", "manager_id": new_manager.id}

@app.post("/users/", response_model=List[UserResponse])
def get_users_by_institute(request: InstituteRequest, db: Session = Depends(get_db)):
    # Query the database for all users associated with the specified institute
    users = db.query(models.User).filter(models.User.institute_id == request.institute_id).all()
    
    # If no users are found, return an empty list
    if not users:
        return []

    # Convert the users to the response model
    return [UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone_number,
        role=user.role  # Assuming role is stored as a string
        ) for user in users]

@app.put("/update-user/{user_id}/")
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    # Query the user by ID
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    # Check if the user exists
    if not user:
        raise HTTPException(status_code=404, detail="User  not found")

    # Update user fields
    user.name = user_data.name
    user.email = user_data.email
    user.phone_number = user_data.phone

    # Commit the changes to the database
    db.commit()
    db.refresh(user)

    return {"status": "success", "message": "User  updated successfully", "user_id": user.id}

@app.delete("/delete-user/{user_id}/")
def delete_user(user_id: int, institute_id: int, db: Session = Depends(get_db)):
    # Query the user by ID
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    # Check if the user exists
    if not user:
        raise HTTPException(status_code=404, detail="User  not found")

    # Check if the user belongs to the specified institute
    if user.institute_id != institute_id:
        raise HTTPException(status_code=403, detail="User  does not belong to this institute")

    # Check if the user is an admin
    if user.role == models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin users cannot be deleted")

    # Delete the user
    db.delete(user)
    db.commit()

    return {"status": "success", "message": "User  deleted successfully"}


@app.post("/add-teachers-file/")
async def add_teachers(
    institute_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        print(f"Processing file: {file.filename}, Institute ID: {institute_id}")

        if file.filename.endswith(('.xls', '.xlsx', '.csv')):
            # Read the file content
            file_content = BytesIO(file.file.read())
            file_content.seek(0)  # Reset file pointer if necessary

            if file.filename.endswith('.csv'):
                df = pd.read_csv(file_content)
            else:
                df = pd.read_excel(file_content)

            # Normalize column names by stripping whitespaces
            df.columns = df.columns.str.strip()

            print("Uploaded file data:", df.head())
            print("Columns:", df.columns)

            # Validate required columns
            required_columns = ['Name', 'Email', 'Phone', 'Subject']
            for col in required_columns:
                if col not in df.columns:
                    raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

            print("File validation passed.")

            success_emails = []
            failed_emails = []

            for _, row in df.iterrows():
                # Extract data from the row
                name = row['Name']
                email = row['Email']
                phone = row['Phone']
                subject = row['Subject']

                # Generate a random password for the user
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

                # Send email to teacher
                email_sent = teacher_send_email(email, password)

                if email_sent:
                    # Create Teacher entry if email is sent successfully
                    teacher = models.Teacher(
                        institute_id=institute_id,
                        name=name,
                        email=email,
                        phone_number=phone,
                        password=password,  # Store a hashed password in a real app
                        subject=subject,
                        role="teacher"  # Assuming the role is set to 'teacher'
                    )

                    # Add teacher to the session
                    db.add(teacher)
                    success_emails.append(email)
                else:
                    failed_emails.append(email)

            # Commit all changes to the database
            db.commit()

            print("Data saved successfully.")

            return JSONResponse(content={
                "success": True,
                "message": "File processed and data saved successfully.",
                "emails_sent": success_emails,
                "emails_failed": failed_emails
            })

        else:
            raise HTTPException(status_code=400, detail="Invalid file type. Only .xls, .xlsx, or .csv files are allowed.")
    
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()  # Rollback in case of error
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teachers/")
def get_teachers(institute_id: int, db: Session = Depends(get_db)):
    try:
        # Query teachers by institute_id
        teachers = db.query(models.Teacher).filter(models.Teacher.institute_id == institute_id).all()

        # Check if no teachers are found
        if not teachers:
            raise HTTPException(status_code=404, detail="No teachers found for the given institute ID.")

        # Format the data for the frontend
        teachers_data = [
            {
                "id": teacher.id,
                "name": teacher.name,
                "email": teacher.email,
                "phone_number": teacher.phone_number,
                "subject": teacher.subject,
                "role": teacher.role.value,  # Enum value
                "created_at": teacher.created_at,
                "updated_at": teacher.updated_at
            }
            for teacher in teachers
        ]

        return {
            "success": True,
            "data": teachers_data,
            "message": "Teachers retrieved successfully."
        }

    except Exception as e:
        print(f"Error fetching teachers: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching teachers.")
    
@app.put("/update-teacher/")
def update_teacher(request: UpdateTeacherRequest, db: Session = Depends(get_db)):
    try:
        # Fetch the teacher by ID and validate the institute
        teacher = db.query(models.Teacher).filter(
            models.Teacher.id == request.teacher_id,
            models.Teacher.institute_id == request.institute_id
        ).first()

        if not teacher:
            raise HTTPException(
                status_code=404,
                detail="Teacher not found for the provided institute and teacher ID."
            )

        # Update the teacher's details
        teacher.name = request.name
        teacher.email = request.email
        teacher.phone_number = request.phone_number
        teacher.subject = request.subject
        db.commit()

        return {
            "success": True,
            "message": "Teacher updated successfully.",
            "data": {
                "id": teacher.id,
                "name": teacher.name,
                "email": teacher.email,
                "phone_number": teacher.phone_number,
                "subject": teacher.subject,
                "institute_id": teacher.institute_id
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-departments-file/")
async def add_departments(
    institute_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        print(f"Processing file: {file.filename}, Institute ID: {institute_id}")

        if file.filename.endswith(('.xls', '.xlsx', '.csv')):
            # Read the file content
            file_content = BytesIO(file.file.read())
            file_content.seek(0)  # Reset file pointer if necessary

            if file.filename.endswith('.csv'):
                df = pd.read_csv(file_content)
            else:
                df = pd.read_excel(file_content)

            # Normalize column names by stripping whitespaces
            df.columns = df.columns.str.strip()

            print("Uploaded file data:", df.head())
            print("Columns:", df.columns)

            # Validate required columns
            required_columns = ['Departments', 'Total No of Classes', 'Class Names']
            for col in required_columns:
                if col not in df.columns:
                    raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

            print("File validation passed.")

            success_departments = []
            failed_departments = []

            for _, row in df.iterrows():
                try:
                    # Extract data from the row
                    department_name = row['Departments']
                    total_classes = int(row['Total No of Classes'])
                    class_names = row['Class Names']

                    # Check if department already exists for this institute
                    existing_department = db.query(models.Department).filter(
                        models.Department.name == department_name,
                        models.Department.institute_id == institute_id
                    ).first()

                    # Create Department entry
                    department = models.Department(
                        institute_id=institute_id,
                        name=department_name,
                        total_classes=total_classes
                    )
                    db.add(department)
                    db.flush()  # Ensure the department ID is available for the Class records

                    # Create Class entries
                    class_names_list = [name.strip() for name in class_names.split(',')]
                    for class_name in class_names_list:
                        class_entry = models.Class(
                            department_id=department.id,
                            institute_id=institute_id,
                            name=class_name
                        )
                        db.add(class_entry)

                    success_departments.append(department_name)

                except Exception as e:
                    print(f"Failed to process department '{row['Department']}': {e}")
                    failed_departments.append(row['Department'])

            # Commit all changes to the database
            db.commit()

            print("Departments and classes saved successfully.")

            return JSONResponse(content={
                "success": True,
                "message": "File processed and data saved successfully.",
                "departments_added": success_departments,
                "departments_failed": failed_departments
            })

        else:
            raise HTTPException(status_code=400, detail="Invalid file type. Only .xls, .xlsx, or .csv files are allowed.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()  # Rollback in case of error
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/add-semesters-and-subjects-file/")
async def add_semesters_and_subjects(
    institute_id: int = Form(...),
    department_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a file containing semesters and subjects and store them in the database.
    """
    try:
        print(f"Processing file: {file.filename}, Institute ID: {institute_id}, Department ID: {department_id}")

        if file.filename.endswith(('.xls', '.xlsx', '.csv')):
            # Read the file content
            file_content = BytesIO(file.file.read())
            file_content.seek(0)  # Reset file pointer

            if file.filename.endswith('.csv'):
                df = pd.read_csv(file_content)
            else:
                df = pd.read_excel(file_content)

            # Normalize column names
            df.columns = df.columns.str.strip().str.replace(" ", "_")

            print("Normalized Columns:", df.columns)

            # Validate required columns
            required_columns = ['semester_number', 'subjects']
            for col in required_columns:
                if col not in df.columns:
                    raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

            print("File validation passed.")

            success_semesters = []
            failed_semesters = []

            for _, row in df.iterrows():
                try:
                    semester_name = str(row['semester_number'])
                    subjects = row['subjects']

                    # Check if the semester already exists for this department and institute
                    existing_semester = db.query(models.Semester).filter(
                        models.Semester.name == semester_name,
                        models.Semester.department_id == department_id,
                        models.Semester.institute_id == institute_id
                    ).first()

                    
                    # Create Semester entry
                    semester = models.Semester(
                        institute_id=institute_id,
                        department_id=department_id,
                        name=semester_name
                    )
                    db.add(semester)
                    db.flush()  # Ensure the semester ID is available for the Subject records

                    # Create Subject entries
                    subject_list = [subject.strip() for subject in subjects.split(',')]
                    for subject_name in subject_list:
                        subject = models.Subject(
                            semester_id=semester.id,
                            department_id=department_id,
                            institute_id=institute_id,
                            name=subject_name
                        )
                        db.add(subject)

                    success_semesters.append(semester_name)
                    print(f"Semester '{success_semesters}' processed successfully.")
                except Exception as e:
                    print(f"Failed to process semester '{row['semester_number']}': {e}")
                    failed_semesters.append(row['semester_number'])

            # Commit all changes to the database
            db.commit()

            print("Semesters and subjects saved successfully.")

            return JSONResponse(content={
                "success": True,
                "message": "File processed and data saved successfully.",
                "semesters_added": success_semesters,
                "semesters_failed": failed_semesters
            })

        else:
            raise HTTPException(status_code=400, detail="Invalid file type. Only .xls, .xlsx, or .csv files are allowed.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()  # Rollback in case of error
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-departments-and-semesters/")
def get_departments_and_semesters(institute_id: int, db: Session = Depends(get_db)):
    try:
        # Query departments for the given institute
        departments = db.query(models.Department).filter(models.Department.institute_id == institute_id).all()
        if not departments:
            raise HTTPException(status_code=404, detail="No departments found for the given institute.")

        # Build response with semesters for each department
        response_data = []
        for department in departments:
            semesters = db.query(models.Semester).filter(models.Semester.department_id == department.id).all()
            response_data.append({
                "department_id": department.id,
                "department_name": department.name,
                "semesters": [{"semester_id": semester.id, "semester_name": semester.name} for semester in semesters]
            })

        return {
            "success": True,
            "data": response_data
        }
    except Exception as e:
        print(f"Error fetching departments and semesters: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching data.")

@app.post("/create-timetable/")
async def create_timetable(
    institute_id: int = Form(...),
    department_id: int = Form(...),
    semester_id: int = Form(...),
    average_class_time: int = Form(...),
    break_time: int = Form(...),
    shift: str = Form(...),
    shift_start_time: str = Form(...),
    shift_end_time: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Parse shift start and end times
        shift_start = datetime.strptime(shift_start_time, "%H:%M")
        shift_end = datetime.strptime(shift_end_time, "%H:%M")

        # Calculate total shift time
        shift_duration = (shift_end - shift_start).seconds / 60

        # Subtract break time to get the total available time for classes
        available_time = shift_duration - break_time

        # Calculate number of classes that can fit in the available time
        num_classes = int(available_time // average_class_time)
        print(f"Number of classes per shift: {num_classes}")
        num_classes = max(num_classes, 4)
        # Fetch the subjects, teachers, and classes from the database
        subjects = db.query(models.Subject).filter(
            models.Subject.institute_id == institute_id,
            models.Subject.department_id == department_id,
            models.Subject.semester_id == semester_id
        ).all()

        teachers = db.query(models.Teacher).filter(
            models.Teacher.institute_id == institute_id
        ).all()

        # Fetch classes by department
        classes = db.query(models.Class).filter(
            models.Class.institute_id == institute_id,
            models.Class.department_id == department_id
        ).all()

        if not subjects or not teachers or not classes:
            raise HTTPException(status_code=400, detail="No subjects, teachers, or classes found for the given parameters")

        # Create timetable for 6 days a week
        timetable = {}
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

        for day in days_of_week:
            timetable[day] = []

            for _ in range(num_classes):
                # Randomly assign a subject, teacher, and class
                subject = random.choice(subjects)
                teacher = random.choice(teachers)
                class_ = random.choice(classes)

                # Add the class schedule for the day
                timetable[day].append({
                    "class_name": class_.name,  # Return class_name instead of class_id
                    "subject": subject.name,
                    "teacher": teacher.name,
                    "time": f"{shift_start.strftime('%H:%M')} - {(shift_start + timedelta(minutes=average_class_time)).strftime('%H:%M')}"
                })

                # Move the shift start time forward by the class duration + break time
                shift_start += timedelta(minutes=average_class_time + break_time)

            # Reset shift_start for the next day (assuming same start time for each day)
            shift_start = datetime.strptime(shift_start_time, "%H:%M")

        # Create timetable entries in the database
        for day, classes in timetable.items():
            for class_entry in classes:
                timetable_entry = models.Timetable(
                    institute_id=institute_id,
                    department_id=department_id,
                    semester_id=semester_id,
                    class_id=class_.id,  # Use class_id here for the database entry
                    subject_id=subject.id,
                    teacher_id=teacher.id,
                    day=day,
                    class_time=shift_start.time(),  # Ensure you are using correct time format
                    shift=shift
                )
                db.add(timetable_entry)

        db.commit()

        return {"success": True, "message": "Timetable created successfully", "timetable": timetable}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/store-timetable/")
# async def store_timetable(data: TimetableRequest, db: Session = Depends(get_db)):
#     print(f"Received data: {data}")
#     try:
#         institute_id = data.institute_id
#         department_id = data.department_id
#         semester_id = data.semester_id
#         timetable_data = data.timetable

#         # Iterate over days and their respective timetable entries
#         for day, classes in timetable_data.items():
#             for entry in classes:
#                 # Parse time range
#                 try:
#                     start_time_str, end_time_str = entry.time.split(" - ")
#                     start_time = datetime.strptime(start_time_str, "%H:%M").time()
#                     end_time = datetime.strptime(end_time_str, "%H:%M").time()
#                 except ValueError:
#                     raise HTTPException(
#                         status_code=400, 
#                         detail=f"Invalid time format in entry: {entry.time}. Use 'HH:MM - HH:MM' format."
#                     )

#                 # Fetch the subject, teacher, and class IDs from the database
#                 subject = db.query(models.Subject).filter(models.Subject.name == entry.subject).first()
#                 teacher = db.query(models.Teacher).filter(models.Teacher.name == entry.teacher).first()
#                 class_ = db.query(models.Class).filter(models.Class.name == entry.class_name).first()

#                 if not subject or not teacher or not class_:
#                     raise HTTPException(
#                         status_code=400, 
#                         detail=f"Subject '{entry.subject}', teacher '{entry.teacher}', or class '{entry.class_name}' not found in the database."
#                     )

#                 # Create a new timetable entry
#                 timetable_entry = models.Timetable(
#                     institute_id=institute_id,
#                     department_id=department_id,
#                     semester_id=semester_id,
#                     class_id=class_.id,
#                     subject_id=subject.id,
#                     teacher_id=teacher.id,
#                     day=day,
#                     class_time=start_time,
#                     shift="morning",  # Adjust shift as needed
#                     created_at=datetime.utcnow(),
#                     updated_at=datetime.utcnow()
#                 )

#                 # Add and commit the entry to the database
#                 db.add(timetable_entry)

#         db.commit()

#         return {"success": True, "message": "Timetable entries stored successfully."}

#     except HTTPException as http_ex:
#         raise http_ex
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/get-timetable/")
async def get_timetable(
    department_id: int,
    semester_id: int,
    institute_id: int,
    shift: str,
    db: Session = Depends(get_db)
):
    try:
        # Fetch timetable entries based on the provided parameters
        timetable = db.query(models.Timetable).filter(
            models.Timetable.department_id == department_id,
            models.Timetable.semester_id == semester_id,
            models.Timetable.institute_id == institute_id,
            models.Timetable.shift == shift
        ).all()

        if not timetable:
            raise HTTPException(status_code=404, detail="No timetable entries found for the given parameters")

        # Prepare the response with all the timetable data, grouped by day
        timetable_data = {}
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

        for day in days_of_week:
            timetable_data[day] = []

        for entry in timetable:
            # Fetch class name
            class_name = db.query(models.Class.name).filter(models.Class.id == entry.class_id).scalar()

            # Fetch subject name
            subject_name = db.query(models.Subject.name).filter(models.Subject.id == entry.subject_id).scalar()

            # Fetch teacher name
            teacher_name = db.query(models.Teacher.name).filter(models.Teacher.id == entry.teacher_id).scalar()

            # Prepare the timetable entry
            timetable_entry = {
                "class_name": class_name,
                "subject": subject_name,
                "teacher": teacher_name,
                "time": entry.class_time, 
            }

            # Group the entries by day
            timetable_data[entry.day].append(timetable_entry)

        # Sort timetable for each day by class_time if required
        for day in timetable_data:
            timetable_data[day].sort(key=lambda x: x['time'])

        return {
            "success": True,
            "message": "Timetable fetched successfully",
            "timetable": timetable_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
