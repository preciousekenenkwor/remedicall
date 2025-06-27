from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database.db import get_db
from app.core.auth.services.middleware_auth import response_message
from app.core.auth.services.service_auth import AuthService
from app.core.auth.services.service_token import TokenService
from app.core.auth.types.type_auth import (
    ChangePasswordT,
    CreateUserT,
    ForgotPasswordT,
    LoginT,
    ResetPasswordT,
    VerifyEmailT,
    VerifyEmailTokenT,
    VerifyResetTokenT,
)
from app.core.user.services.user_service import UserService
from app.utils.logger import log

auth_router = APIRouter()


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: CreateUserT,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Create a new user account and automatically send email verification

    - **email**: Valid email address
    - **password**: Must be 8+ characters with uppercase, lowercase, number, and special character
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **user_type**: Type of user account
    """
    auth_service = AuthService(db)
    try:
        # Create the user
        result = await auth_service.create_user(user_data)


        # Automatically send email verification after successful registration
        if result and hasattr(result, "id"):
            log.logs.info(f"User {result.id} registered successfully")
            try:
                verification_data: VerifyEmailT = {"email": result.email}
                await auth_service.send_email_verification(
                    verification_data, background_tasks
                )
            except Exception as e:
                # Log the error but don't fail the registration
                # User can request verification email later
                print(f"Failed to send verification email: {e}")

        # Remove password from response
        user_dict = result.__dict__.copy() if hasattr(result, "__dict__") else {}
        user_dict.pop("password", None)
        user_dict.pop("_sa_instance_state", None)
        tokens = await TokenService.generate_auth_token(result.id, db=db)

        return {
            "success": True,
            "message": "User created successfully. Verification email sent.",
            "data": {'user':user_dict,'tokens':tokens},
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_message(
                error="Registration failed - " + str(e),
                success_status=False,
                message="An error occurred during registration",
            ),
        )


@auth_router.post("/login")
async def login_user(
    login_data: LoginT, db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Authenticate user login

    - **email**: Email address or username
    - **password**: User password
    """
    auth_service = AuthService(db)
    try:
        result = await auth_service.login_user(login_data)
        return {
            "success": True,
            "message": result["message"],
            "data": {"user": result["user"], "tokens": result["tokens"]},
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_message(
                error="Login failed",
                success_status=False,
                message="An error occurred during login",
            ),
        )


@auth_router.post("/send-verification-email")
async def send_verification_email(
    verification_data: VerifyEmailT,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),

) -> Dict[str, Any]:
    """
    Send email verification code

    - **user_id**: ID of the user to verify
    """
    auth_service = AuthService(db)
    try:
        result = await auth_service.send_email_verification(
            verification_data, background_tasks
        )
        return {
            "success": result["success_status"],
            "message": result["message"],
            "data": result["data"],
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_message(
                error="Failed to send verification email",
                success_status=False,
                message="An error occurred while sending verification email",
            ),
        )


@auth_router.post("/verify-email")
async def verify_email(
    verification_data: VerifyEmailTokenT,
    db: AsyncSession = Depends(get_db),
   
) -> Dict[str, Any]:
    """
    Verify email address with OTP

    - **user_id**: ID of the user
    - **token**: OTP token received via email
    """
    auth_service = AuthService(db)
    try:
        result = await auth_service.verify_email(verification_data)
        return {
            "success": result["success_status"],
            "message": result["message"],
            "data": result["data"],
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_message(
                error="Email verification failed",
                success_status=False,
                message="An error occurred during email verification",
            ),
        )


@auth_router.post("/forgot-password")
async def forgot_password(
    forgot_data: ForgotPasswordT,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Send password reset token

    - **email**: Email address of the account
    """
    auth_service = AuthService(db)
    try:
        result = await auth_service.forgot_password(forgot_data, background_tasks)
        return {
            "success": result["success_status"],
            "message": result["message"],
            "data": result["data"],
        }
    except Exception:
        # Always return success for security reasons
        return {
            "success": True,
            "message": "Reset email sent",
            "data": "If you have an account, a password reset email has been sent",
        }

# Type definition (add this to your types file)



# Auth route
@auth_router.post("/verify-reset-password")
async def verify_reset_password_token(
    verify_data: VerifyResetTokenT,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Verify password reset token

    - **email**: Email address of the account
    - **token**: 6-digit reset token received via email
    """
    auth_service = AuthService(db)
    try:
        result = await auth_service.verify_reset_password_token(verify_data)
        return {
            "success": result["success_status"],
            "message": result["message"],
            "data": result.get("data"),
            "error": result.get("error"),
        }
    except Exception as e:
        log.logs.error(f"Error in verify reset token endpoint: {e}")
        return {
            "success": False,
            "message": "Invalid token",
            "error": "Token verification failed",
        }


@auth_router.post("/reset-password")
async def reset_password(
    reset_data: ResetPasswordT, db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Reset password with token

    - **email**: Email address of the account
    - **token**: Reset token received via email
    - **password**: New password
    """
    auth_service = AuthService(db)
    try:
        result = await auth_service.reset_password(reset_data)
        return {
            "success": result["success_status"],
            "message": result["message"],
            "data": result["data"],
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_message(
                error="Password reset failed",
                success_status=False,
                message="An error occurred during password reset",
            ),
        )


@auth_router.post("/change-password")
async def change_password(
    password_data: ChangePasswordT,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(UserService.get_logged_in_user),
) -> Dict[str, Any]:
    """
    Change user password (requires authentication)

    - **current_password**: Current password
    - **new_password**: New password
    """
    auth_service = AuthService(db)
    try:
        # Create complete password data with user_id
        complete_password_data = {
            "user_id": current_user,
            "current_password": password_data["current_password"],
            "new_password": password_data["new_password"],
        }

        result = await auth_service.change_password(complete_password_data)
        return {
            "success": result["success_status"],
            "message": result["message"],
            "data": result["data"],
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_message(
                error="Password change failed",
                success_status=False,
                message="An error occurred while changing password",
            ),
        )


@auth_router.post("/refresh-token")
async def refresh_token(
    db: AsyncSession = Depends(get_db), refresh_token: str = Depends(TokenService.get_refresh_token)
) -> Dict[str, Any]:
    """
    Refresh authentication tokens

    Requires valid refresh token in Authorization header
    """
    auth_service = AuthService(db)
    try:
        result = await auth_service.refresh_token(refresh_token)
        return {"success": True, "message": result["message"], "data": result["tokens"]}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=response_message(
                error="Token refresh failed",
                success_status=False,
                message="Unable to refresh authentication tokens",
            ),
        )


@auth_router.post("/logout")
async def logout_user(
    db: AsyncSession = Depends(get_db), refresh_token: str = Depends(TokenService.get_refresh_token)
) -> Dict[str, Any]:
    """
    Logout user by invalidating refresh token

    Requires valid refresh token in Authorization header
    """
    auth_service = AuthService(db)
    try:
        result = await auth_service.logout(refresh_token)
        return {
            "success": result["success_status"],
            "message": result["message"],
            "data": result["data"],
        }
    except Exception:
        # Always return success for logout
        return {
            "success": True,
            "message": "Logged out successfully",
            "data": "You have been logged out",
        }


@auth_router.get("/me")
async def get_logged_in_user_info(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(UserService.get_logged_in_user),
) -> Dict[str, Any]:
    """
    Get current authenticated user information

    Requires valid access token in Authorization header
    """
    auth_service = AuthService(db)
    try:
        user_data = await auth_service.get_user_by_id(current_user)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response_message(
                    error="User not found",
                    success_status=False,
                    message="User account not found",
                ),
            )

        # Remove password from response
        user_dict = user_data.__dict__.copy() if hasattr(user_data, "__dict__") else {}
        user_dict.pop("password", None)
        user_dict.pop("_sa_instance_state", None)  # Remove SQLAlchemy state

        return {
            "success": True,
            "message": "User information retrieved successfully",
            "data": user_dict,
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_message(
                error="Failed to retrieve user information",
                success_status=False,
                message="An error occurred while retrieving user information",
            ),
        )


@auth_router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for authentication service
    """
    return {
        "success": True,
        "message": "Authentication service is healthy",
        "data": {"service": "auth", "status": "operational"},
    }
