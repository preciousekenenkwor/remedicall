from pydantic import BaseModel, EmailStr

# User Registration
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str

# User Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# User Response
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_verified: bool

    class Config:
        orm_mode = True

# JWT Token Response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Email Verification Code (for registration)
class VerificationCode(BaseModel):
    email: EmailStr
    code: str

# Forgot Password Reset Code Verification
class ResetPasswordVerify(BaseModel):
    email: EmailStr
    code: str

# Reset Password (enter new password after verification)
class ResetPassword(BaseModel):
    email: EmailStr
    code: str
    new_password: str
