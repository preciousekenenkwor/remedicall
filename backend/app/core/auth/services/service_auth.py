from typing import Any, Dict, Optional

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import env
from app.config.config import TokenType
from app.core.auth.services.middleware_auth import response_message
from app.core.auth.services.service_token import TokenService
from app.core.auth.types.type_auth import (
    ForgotPasswordT,
    LoginT,
    ResetPasswordT,
    VerifyEmailT,
    VerifyEmailTokenT,
    VerifyResetTokenT,
)
from app.core.user.model.user_model import UserModel
from app.core.user.services.user_service import UserService
from app.utils import password_hash
from app.utils.convert_sqlalchemy_dict import sqlalchemy_obj_to_dict
from app.utils.logger import log
from app.utils.mailer import SMTPMailer
from app.utils.regex import email_regex, password_regex
from app.utils.types_utils.response_types import ResponseMessage


class AuthService(UserService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.db = db

   

    async def login_user(self, data: LoginT) -> Dict[str, Any]:
        """Authenticate user login"""
        try:
            # Find user by email or username
            user_data = None
            if email_regex.match(data["email"]):
                user_data = await self.get_user({"email": data["email"]})
            else:
                user_data = await self.get_user({"username": data["email"]})

            if not user_data or user_data is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response_message(
                        error="Invalid credentials",
                        success_status=False,
                        message="Invalid email/username or password",
                    ),
                )

           

            # Verify password
            if not password_hash.PassHash().verify_me(
                password=data["password"], hashed_password=user_data.password
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response_message(
                        error="Invalid credentials",
                        success_status=False,
                        message="Invalid email/username or password",
                    ),
                )

            # Generate authentication tokens
            tokens = await TokenService.generate_auth_token(    user_id=user_data.id, db=self.db)

            # Remove password from user object
            user_dict = sqlalchemy_obj_to_dict(user_data)
            if isinstance(user_dict, dict):
                user_dict.pop("password", None)

            return {"user": user_dict, "tokens": tokens, "message": "Login successful"}

        except HTTPException:
            raise
        except Exception as e:
            log.logs.error(f"Error during login: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response_message(
                    error="Internal server error",
                    success_status=False,
                    message="An unexpected error occurred",
                ),
            )

    async def send_email_verification(
        self, data: VerifyEmailT, background_tasks: BackgroundTasks
    )  -> ResponseMessage:
        """Send email verification token"""
        try:
            # Get user
            user_data = await self.get_user_by_email(data["email"])
            if not user_data or user_data is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_message(
                        error="User not found",
                        success_status=False,
                        message="User account not found",
                    ),
                )

            user = user_data

            # Generate OTP token
            otp_token = TokenService.generate_otp_token()
            log.logs.info(f"Generated OTP token: {otp_token}")

            # Save token to database
            await TokenService.save_token(
                data={
                    "user_id": user.id,
                    "token": str(otp_token),
                    "type": TokenType.VERIFY_EMAIL.value,
                    "expires": 30,  # 30 minutes
                    "blacklisted": False,
                },
                db=self.db,
            )

            # Send email if mail service is enabled
            if env.env["mail"]["use_mail_service"]:
                log.logs.info("Sending verification email")
                mailer = SMTPMailer(
                    background_tasks=background_tasks,
                    receiver_emails=[user.email],
                    template_name="verify_email.html",
                    subject="Verify Your Email Address",
                    template_data={
                        "name": getattr(user, "name", user.email),
                        "otp": otp_token,
                        "expiry_hours": 0.5,  # 30 minutes
                        "website_name": "MediGuard",
                    },
                    background=False,
                )
                await mailer.send_mail()

            return response_message(
                success_status=True,
                message="Verification email sent successfully",
                data="Please check your email for the verification code",
            )

        except HTTPException:
            raise
        except Exception as e:
            log.logs.error(f"Error sending verification email: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response_message(
                    error="Internal server error",
                    success_status=False,
                    message="Failed to send verification email",
                ),
            )

    async def verify_reset_password_token(
        self,
        data: VerifyResetTokenT,  # Expected: {"email": str, "token": str}
    )  -> ResponseMessage :
        """Verify password reset token"""
        try:
            email = data.get("email")
            token = data.get("token")

            log.logs.info(f"Email: {email}, Token: {token}")

            if not email or not token:
                return response_message(
                    success_status=False,
                    message="Validation failed",
                    error="Email and token are required",
                )

            # Find user by email
            user_data = await self.get_user_by_email( email)

            if not user_data:
                return response_message(
                    success_status=False,
                    message="Invalid token",
                    error="Invalid or expired reset token",
                )

            user = user_data

            # Verify the OTP token
            token_data = await TokenService.verify_otp_token(
                token=token, user_id=user.id, type=TokenType.RESET_PASSWORD, db=self.db
            )

            if token_data:
                return response_message(
                    success_status=True,
                    message="Token verified successfully",
                    data={"valid": True, "user_id": user.id, "email": user.email},
                )
            else:
                return response_message(
                    success_status=False,
                    message="Invalid token",
                    error="Invalid or expired reset token",
                )

        except HTTPException as e:
            # Extract error details from HTTPException
            error_detail = e.detail
            if isinstance(error_detail, dict):
                return response_message(
                    success_status=False,
                    message=error_detail.get("message", "Invalid token"),
                    error=error_detail.get("error", "Token verification failed"),
                )
            else:
                return response_message(
                    success_status=False,
                    message="Invalid token",
                    error="Token verification failed",
                )
        except Exception as e:
            log.logs.error(f"Error in verify reset password token: {e}")
            return response_message(
                success_status=False,
                message="Invalid token",
                error="Token verification failed",
            )

    async def verify_email(self, data: VerifyEmailTokenT) ->ResponseMessage:
        """Verify user email with OTP token"""
        try:
            # Verify OTP token
            user = await self.get_user_by_email(data["email"])
            
            if  not user or user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_message(
                        error="User not found",
                        success_status=False,
                        message="User account not found",
                    )
                )
            token_data = await TokenService.verify_otp_token(
                db=self.db,
                user_id=user.id,
                token=data["token"],
                type=TokenType.VERIFY_EMAIL,
            )

            if token_data:
                # Update user verification status
                stmt = (
                    update(UserModel)
                    .where(UserModel.id == user.id)
                    .values(email_verified=True)
                )
                await self.db.execute(stmt)
                await self.db.commit()

                return response_message(
                    success_status=True,
                    message="Email verified successfully",
                    data="Your email has been verified",
                )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response_message(
                    error="Invalid token",
                    success_status=False,
                    message="Invalid or expired verification token",
                ),
            )

        except HTTPException:
            raise
        except Exception as e:
            log.logs.error(f"Error verifying email: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response_message(
                    error="Internal server error",
                    success_status=False,
                    message="Failed to verify email",
                ),
            )

    async def forgot_password(
        self, data: ForgotPasswordT, background_tasks: BackgroundTasks
    ) -> ResponseMessage:
        """Send password reset token"""
        try:
            # Find user by email
            user_data = await self.get_user({"email": data["email"]})

            # Always return success message for security (don't reveal if email exists)
            success_message = (
                "If you have an account, a password reset email has been sent"
            )

            if user_data and user_data:
                user = user_data

                # Generate reset token
                reset_token = TokenService.generate_otp_token()

                # Save token to database
                await TokenService.save_token(
                    data={
                        "user_id": user.id,
                        "token": str(reset_token),
                        "type": TokenType.RESET_PASSWORD.value,
                        "expires": 30,  # 30 minutes
                        "blacklisted": False,
                    },
                    db=self.db,
                )

                # Send email if mail service is enabled
                if env.env["mail"]["use_mail_service"]:
                    mailer = SMTPMailer(
                        background_tasks=background_tasks,
                        receiver_emails=[user.email],
                        template_name="reset_password.html",
                        subject="Reset Your Password",
                        template_data={
                            "name": getattr(user, "name", user.email),
                            "otp": reset_token,
                            "expiry_hours": 0.5,  # 30 minutes
                        },
                        background=True,
                    )
                    await mailer.send_mail()

            return response_message(
                success_status=True, message="Reset email sent", data=success_message
            )

        except Exception as e:
            log.logs.error(f"Error in forgot password: {e}")
            # Still return success for security
            return response_message(
                success_status=True,
                message="Reset email sent",
                data="If you have an account, a password reset email has been sent",
            )

    async def reset_password(self, data: ResetPasswordT) -> ResponseMessage:
        """Reset user password with token verification"""
        try:
            email = data.get("email")
            token = data.get("token")
            new_password = data.get("new_password")
            
            if not email or not token or not new_password:
                return response_message(
                    success_status=False,
                    message="Validation failed",
                    error="Email, token, and new password are required"
                )

            # Find user by email
            user_data = await self.get_user({"email": email})
            
            if not user_data:
                return response_message(
                    success_status=False,
                    message="Invalid request",
                    error="Invalid reset token"
                )

            user = user_data

            # Verify the OTP token (this will also blacklist it)
            token_data = await TokenService.verify_otp_token(
                token=token,
                user_id=user.id,
                type=TokenType.RESET_PASSWORD,
                db=self.db
            )

            if token_data:
                # Hash the new password
                hashed_password = password_hash.PassHash().hash_me(new_password)
                
                # Update user password
                update_stmt = (
                    update(UserModel)
                    .values(password=hashed_password)
                    .where(UserModel.id == user.id)
                )
                await self.db.execute(update_stmt)
                await self.db.commit()

                return response_message(
                    success_status=True,
                    message="Password reset successful",
                    data="Your password has been reset successfully"
                )
            else:
                return response_message(
                    success_status=False,
                    message="Invalid or expired reset token",
                    error="Invalid reset token"
                )

        except HTTPException as e:
            # Extract error details from HTTPException
            error_detail = e.detail
            if isinstance(error_detail, dict):
                return response_message(
                    success_status=False,
                    message=error_detail.get("message", "Invalid token"),
                    error=error_detail.get("error", "Password reset failed")
                )
            else:
                return response_message(
                    success_status=False,
                    message="Invalid token",
                    error="Password reset failed"
                )
        except Exception as e:
            log.logs.error(f"Error in reset password: {e}")
            return response_message(
                success_status=False,
                message="Password reset failed",
                error="An error occurred while resetting password"
            )

    async def change_password(self, data: Dict[str, Any]) -> ResponseMessage:
        """Change user password (requires current password)"""
        try:
            # Get user
            user_data = await self.get_user_by_id(data["user_id"])
            if not user_data or user_data is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response_message(
                        error="User not found",
                        success_status=False,
                        message="User account not found",
                    ),
                )

            user = user_data

            # Verify current password
            if not password_hash.PassHash().verify_me(
                password=data["current_password"], hashed_password=user.password
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response_message(
                        error="Invalid current password",
                        success_status=False,
                        message="Current password is incorrect",
                    ),
                )

            # Validate new password
            if not password_regex.match(data["new_password"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response_message(
                        error="Invalid password format",
                        success_status=False,
                        message="Password must be 8+ characters with uppercase, lowercase, number, and special character",
                    ),
                )

            # Hash new password and update
            hashed_password = password_hash.PassHash().hash_me(data["new_password"])
            stmt = (
                update(UserModel)
                .where(UserModel.id == data["user_id"])
                .values(password=hashed_password)
            )
            await self.db.execute(stmt)
            await self.db.commit()

            return response_message(
                success_status=True,
                message="Password changed successfully",
                data="Your password has been updated",
            )

        except HTTPException:
            raise
        except Exception as e:
            log.logs.error(f"Error changing password: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response_message(
                    error="Internal server error",
                    success_status=False,
                    message="Failed to change password",
                ),
            )

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh authentication tokens"""
        try:
            tokens = await TokenService.refresh_auth_token(refresh_token, db=self.db)
            return {"tokens": tokens, "message": "Tokens refreshed successfully"}
        except Exception as e:
            log.logs.error(f"Error refreshing token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=response_message(
                    error="Invalid refresh token",
                    success_status=False,
                    message="Unable to refresh tokens",
                ),
            )

    async def logout(self, refresh_token: str) -> ResponseMessage:
        """Logout user by blacklisting refresh token"""
        try:
            await TokenService.verify_token(
                token=refresh_token, type=TokenType.REFRESH_TOKEN, db=self.db
            )
            return response_message(
                success_status=True,
                message="Logged out successfully",
                data="You have been logged out",
            )
        except Exception as e:
            log.logs.error(f"Error during logout: {e}")
            # Still return success even if token is invalid
            return response_message(
                success_status=True,
                message="Logged out successfully",
                data="You have been logged out",
            )





    

    # Helper methods
    async def _get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email address"""
        stmt = select(UserModel).filter(UserModel.email == email)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, "db") and self.db:
            # Don't close here as it might be managed by dependency injection
            pass
