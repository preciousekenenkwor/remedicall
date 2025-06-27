import random
from datetime import datetime, timedelta
from typing import TypedDict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import env
from app.config.config import TokenType
from app.core.auth.models.model_token import TokenModel
from app.utils.logger import log
from app.utils.my_jwt import MyJwt
from app.utils.types_utils.response_types import response_message

jwt = MyJwt()
# Create HTTPBearer instance for token extraction
security = HTTPBearer()

class saveToken(TypedDict):
    token: str
    expires: int
    type: str
    user_id: str
    blacklisted: bool


class TokenService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all_tokens(self):
        """Get all tokens from database"""
        stmt = select(TokenModel)
        result = await self.db.execute(stmt)
        tokens = result.scalars().all()
        return tokens

    @staticmethod
    def generate_token(user_id: str, token_type: str, expires_in: int) -> str:
        """Generate JWT token"""
        return jwt.create_token(
            subject=user_id, token_type=token_type, expires_in=expires_in
        )

    @staticmethod
    def generate_otp_token(otp_length: int = 6) -> int:
        """Generate OTP token as an integer with fixed digits"""
        lower = 10**(otp_length - 1)
        upper = 10**otp_length - 1
        return random.randint(lower, upper)

           

    @staticmethod
    async def save_token(data: saveToken, db: AsyncSession):
        """Save token to database"""
        # Check for existing token
        stmt = select(TokenModel).where(
            TokenModel.user_id == data["user_id"], TokenModel.type == data["type"]
        )
        result = await db.execute(stmt)
        existing_token = result.scalars().first()

        # Blacklist existing token if found
        if existing_token:
            update_stmt = (
                update(TokenModel)
                .values(blacklisted=True)
                .where(TokenModel.id == existing_token.id)
            )
            await db.execute(update_stmt)

        # Set expiry time
        data["expires"] = datetime.now() + timedelta(minutes=data["expires"])  # type: ignore

        # Create and save new token
        token_data = TokenModel(**data)
        db.add(token_data)
        await db.commit()
        await db.refresh(token_data)
        return token_data

    @staticmethod
    async def verify_token(token: str, type: TokenType, db: AsyncSession):
        """Verify token and blacklist it"""
        # Verify JWT token
        token_data = jwt.verify_token(token=token)

        if not isinstance(token_data["sub"], str):
            raise HTTPException(
                status_code=400,
                detail=response_message(
                    error="Invalid token", success_status=False, message="Invalid token"
                ),
            )

        try:
            # Get token from database
            stmt = select(TokenModel).where(
                TokenModel.user_id == token_data["sub"],
                TokenModel.type == type.value,
                TokenModel.blacklisted == False,
            )
            result = await db.execute(stmt)
            db_token = result.scalars().first()

            if db_token is None:
                raise HTTPException(
                    status_code=400,
                    detail=response_message(
                        error="Invalid token",
                        success_status=False,
                        message="Invalid token",
                    ),
                )

            # Blacklist the token
            update_stmt = (
                update(TokenModel)
                .values(blacklisted=True)
                .where(TokenModel.id == db_token.id)
            )
            await db.execute(update_stmt)
            await db.commit()

            return db_token

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=response_message(
                    error=str(e), success_status=False, message="Invalid token"
                ),
            )

    @staticmethod
    async def verify_jwt_token(token: str):
        """Verify JWT token without database check"""
        token_data = jwt.verify_token(token=token)

        if not isinstance(token_data["sub"], str):
            raise HTTPException(
                status_code=400,
                detail=response_message(
                    error="Invalid token", success_status=False, message="Invalid token"
                ),
            )

        try:
            # Check if token has expired
            token_time = token_data["exp"]

            if datetime.fromtimestamp(token_time) < datetime.now():
                raise HTTPException(
                    status_code=400,
                    detail=response_message(
                        error="Token expired",
                        success_status=False,
                        message="Invalid token",
                    ),
                )

            return token_data["sub"]

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=response_message(
                    error=str(e), success_status=False, message="Invalid token"
                ),
            )

    @staticmethod
    async def verify_otp_token(
        token: str, user_id: str, type: TokenType, db: AsyncSession
    ):
        """Verify OTP token"""
        try:
            # Get OTP token from database
            log.logs.info(f'{user_id} {type.value} {token}' )
            stmt = select(TokenModel).where(
                TokenModel.user_id == user_id,
                TokenModel.type == type.value,
                TokenModel.blacklisted == False,
                TokenModel.token == token,
            )
            result = await db.execute(stmt)
            token_data = result.scalars().first()

            log.logs.info(f'token_data: , {token_data} {user_id}' )
            if token_data is None:
                raise HTTPException(
                    status_code=400,
                    detail=response_message(
                        error="Invalid token",
                        success_status=False,
                        message="Invalid token",
                    ),
                )

            # Check if token has expired
            expires_dt = token_data.expires
            if isinstance(expires_dt, str):
                from dateutil import parser
                expires_dt = parser.parse(expires_dt)
            if expires_dt < datetime.now():
                raise HTTPException(
                    status_code=400,
                    detail=response_message(
                        error="Token expired",
                        success_status=False,
                        message="Token has expired, request a new one",
                    ),
                )

            # Blacklist the token
            update_stmt = (
                update(TokenModel)
                .values(blacklisted=True)
                .where(TokenModel.id == token_data.id)
            )
            await db.execute(update_stmt)
            await db.commit()

            return token_data

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=response_message(
                    error=str(e),
                    success_status=False,
                    message="Invalid or expired verification token",
                ),
            )

    @staticmethod
    async def generate_auth_token(user_id: str, db: AsyncSession):
        """Generate access and refresh tokens"""
        access_expiry_time = env.env["jwt"]["jwt_access_expiry_time"]
        refresh_expiry_time = env.env["jwt"]["jwt_refresh_expiry_time"]

        access_token = jwt.create_token(
            subject=user_id,
            token_type=TokenType.ACCESS_TOKEN.value,
            expires_in=access_expiry_time,
        )
        refresh_token = jwt.create_token(
            subject=user_id,
            token_type=TokenType.REFRESH_TOKEN.value,
            expires_in=refresh_expiry_time,
        )
        log.logs.info(f"Access token expiry time: {access_token}")
        log.logs.info(f"Refresh token expiry time: {refresh_token}")

        # Save refresh token to database
        await TokenService.save_token(
            data={
                "token": refresh_token,
                "expires": refresh_expiry_time,
                "type": TokenType.REFRESH_TOKEN.value,
                "user_id": user_id,
                "blacklisted": False,
            },
            db=db,
        )

        return {
            "access": {
                "token": access_token,
                "expires": datetime.now() + timedelta(minutes=access_expiry_time),
            },
            "refresh": {
                "token": refresh_token,
                "expires": datetime.now() + timedelta(minutes=refresh_expiry_time),
            },
        }

    @staticmethod
    async def refresh_auth_token(refresh_token: str, db: AsyncSession):
        """Refresh authentication tokens"""
        # Verify refresh token
        token_data = await TokenService.verify_token(
            token=refresh_token, type=TokenType.REFRESH_TOKEN, db=db
        )

        # Generate new tokens
        new_tokens = await TokenService.generate_auth_token(
            user_id=token_data.user_id, db=db
        )
        return new_tokens
    @staticmethod
    async def get_refresh_token(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> str:
        """
        Extract refresh token from Authorization header
        Expected format: Authorization: Bearer <refresh_token>
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=response_message(
                    error="Missing token",
                    success_status=False,
                    message="Authorization token is required",
                ),
            )

        if not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=response_message(
                    error="Invalid token format",
                    success_status=False,
                    message="Token cannot be empty",
                ),
            )

        return credentials.credentials
