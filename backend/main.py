from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from utils.email_utils import send_email
import models
import schemas
import auth

# Create DB tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI()

# ✅ Add CORS configuration:
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency: DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Signup
@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered.")

    hashed_pw = auth.hash_password(user.password)
    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_pw,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate & store verification code
    code = auth.generate_verification_code()
    db.add(models.EmailVerification(email=user.email, code=code))
    db.commit()

    # ✅ Send verification email
    send_email(
        recipient=user.email,
        subject="Verify Your RemediCall Account",
        body=f"Your verification code is: {code}"
    )

    return new_user

# Verify email
@app.post("/verify-email")
def verify_email(data: schemas.VerificationCode, db: Session = Depends(get_db)):
    record = db.query(models.EmailVerification).filter(
        models.EmailVerification.email == data.email,
        models.EmailVerification.code == data.code
    ).first()

    if not record:
        raise HTTPException(status_code=400, detail="Invalid code.")

    user = db.query(models.User).filter(models.User.email == data.email).first()
    user.is_verified = True
    db.commit()

    # Delete code after verification
    db.delete(record)
    db.commit()

    return {"message": "Email verified successfully."}

# Login
@app.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()

    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified.")

    token_data = {"user_id": user.id, "email": user.email}
    token = auth.create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer"}

# Forgot Password - Send Reset Code
@app.post("/forgot-password")
def forgot_password(data: schemas.VerificationCode, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Email not found.")

    code = auth.generate_verification_code()
    db.add(models.PasswordReset(email=data.email, code=code))
    db.commit()

    # ✅ Send reset code email
    send_email(
        recipient=data.email,
        subject="RemediCall Password Reset Code",
        body=f"Your password reset code is: {code}"
    )

    return {"message": "Reset code sent."}

# Verify reset code
@app.post("/verify-reset-code")
def verify_reset_code(data: schemas.ResetPasswordVerify, db: Session = Depends(get_db)):
    record = db.query(models.PasswordReset).filter(
        models.PasswordReset.email == data.email,
        models.PasswordReset.code == data.code
    ).first()

    if not record:
        raise HTTPException(status_code=400, detail="Invalid reset code.")

    return {"message": "Code verified."}

# Reset password
@app.post("/reset-password")
def reset_password(data: schemas.ResetPassword, db: Session = Depends(get_db)):
    record = db.query(models.PasswordReset).filter(
        models.PasswordReset.email == data.email,
        models.PasswordReset.code == data.code
    ).first()

    if not record:
        raise HTTPException(status_code=400, detail="Invalid reset code.")

    user = db.query(models.User).filter(models.User.email == data.email).first()
    user.hashed_password = auth.hash_password(data.new_password)
    db.commit()

    # Delete reset code after success
    db.delete(record)
    db.commit()

    return {"message": "Password reset successfully."}
