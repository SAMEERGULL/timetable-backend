from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse  
from pydantic import BaseModel, EmailStr
from typing import List, Annotated
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

def send_email(to_email, password):
    sender_email = "universalsmarttimetable@gmail.com"  # Replace with your Gmail address
    sender_password = "kyif abme qpyf wrsg" 
    subject = "Access to View Timetable"
    body = f"You have been given access to view the timetable. Your credentials are:\nEmail: {to_email}\nPassword: {password}"
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465 ) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())


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
        # total_semesters=institute_data.total_semesters
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

@app.post("/add-teachers/")
async def add_teachers(institute_id: int, file: UploadFile = File(...)):
    if file.filename.endswith(('.xls', '.xlsx', '.csv')):
        # Read the file content
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)

        # Validate required columns
        required_columns = ['name', 'email', 'phone', 'subject']
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

        # Create a new database session
        db: Session = SessionLocal()

        success_emails = []
        for index, row in df.iterrows():
            name = row['name']
            email = row['email']
            phone = row['phone']
            subject = row['subject']  # Extract subject

            # Generate a random password
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            # Send email
            try:
                send_email(email, password)
                success_emails.append(email)

                # Store the teacher and user data
                teacher = models.Teacher(name=name, email=email, phone_number=phone, subject=subject, institute_id=institute_id)  # Store subject
                user = models.User(name=name, email=email, password=password, role=models.UserRole.teacher, institute_id=institute_id)

                db.add(teacher)
                db.add(user)

            except Exception as e:
                print(f"Failed to send email to {email}: {e}")

        db.commit()
        db.close()

        return JSONResponse(content={"success": True, "emails_sent": success_emails})

    raise HTTPException(status_code=400, detail="Invalid file type. Please upload .xls, .xlsx, or .csv files.")

