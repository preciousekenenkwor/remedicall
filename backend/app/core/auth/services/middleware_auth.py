# middleware/auth.py
from typing import Any, Optional

from fastapi import Request
from fastapi.security import HTTPBearer
from sqlalchemy.future import select as sa_select
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config.database.db import DatabaseSessionManager
from app.core.auth.services.service_token import TokenService
from app.core.user.model.user_model import UserModel
from app.utils.convert_sqlalchemy_dict import sqlalchemy_obj_to_dict
from app.utils.logger import log
from app.utils.types_utils.response_types import ResponseMessage, response_message

security = HTTPBearer()

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db_session: DatabaseSessionManager):
        super().__init__(app)
        self.db = db_session
        # self.crud_service = CrudService(db=db_session, model=TokenModel) # type: ignore
        self.token_service = TokenService

    async def get_current_user(self, token: str) -> Optional[ResponseMessage]:
        # print("token", token)
        try:
            
            token_result: str = await self.token_service.verify_jwt_token(token=token )
       
            
            if not token_result:
                return ResponseMessage(
                    data=None, 
                    doc_length=0, 
                    error="Invalid or expired token", 
                    message="Unauthorized", 
                    success_status=False
                )
            
            user_service = UserServices(self.db)
        
            user = await user_service.get_one({"id":token_result}) 
            if not user or not user.get('data'):
                return ResponseMessage(
                    data=None, 
                    doc_length=0, 
                    error="User not found", 
                    message="Unauthorized", 
                    success_status=False
                )
                
            return user
        except Exception as e:
            print("error", e)
   
            log.logs.error(f"Error getting user: {e}")
            return None

   
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if self.should_skip_auth(request.url.path):
            return await call_next(request)
            
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                # Instead of raising, return a JSONResponse directly
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=401,
                    content=response_message(
                        error="Missing authorization header",
                        success_status=False,
                        message="Unauthorized"
                    )
                )

            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                # Return response instead of raising
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=401,
                    content=response_message(
                        error="Invalid authentication scheme",
                        success_status=False,
                        message="Unauthorized"
                    )
                )

            # Rest of your auth logic...
            current_user_response = await self.get_current_user(token)
            if not current_user_response or "data" not in current_user_response:
                # Return response instead of raising
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=401,
                    content=response_message(
                        error="Invalid or expired token",
                        success_status=False,
                        message="Unauthorized"
                    )
                )
                
            # Add user to request state
            request.state.user = current_user_response
            
            # Pass to the next middleware or route handler
            return await call_next(request)
            
        except Exception as e:
            log.logs.error(f"Authentication error: {str(e)}")
            # Return error response instead of raising
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content=response_message(
                    error=str(e),
                    success_status=False,
                    message="Authentication failed"
                )
            )
    # def should_skip_auth(self, path: str) -> bool:
    #     """Define paths that should skip authentication"""
    #     public_paths = {
    #         "/docs",
    #         "/redoc",
    #         "/openapi.json",
    #         "/api/v1/auth/login",
      
    #         "/api/v1/auth/signup",
    #         "/auth/register",
            
            
            
    #     }
    #     return any(path.startswith(public_path) for public_path in public_paths)
    def should_skip_auth(self, path: str) -> bool:
        """Define paths that should skip authentication"""
        # Exact match paths
        exact_paths = {
            "/",  # Home route exactly
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/verify-email",
            "/api/v1/auth/send-verification-email",
            "/api/v1/auth/reset-password",
            "/api/v1/auth/verify-reset-password",
            "/api/v1/auth/forgot-password",
            
            "/api/v1/auth/refresh-token",
            "/api/v1/auth/logout"
        }
        
        # Prefix paths that include all sub-paths
        prefix_paths = {
            "/docs",
            "/redoc",
            "/openapi.json",
        }
        
        # Check for exact matches first
        if path in exact_paths:
            return True
            
        # Then check for prefix matches
        return any(path.startswith(prefix_path) for prefix_path in prefix_paths)


class UserServices:
    def __init__(self, db: DatabaseSessionManager):
        self.db = db
        self.model = UserModel

    async def get_one(self, data: dict[str, Any], select: Optional[list[str]] = None) -> ResponseMessage:
        async with self.db.session() as session:  # Obtain an AsyncSession
            try:
                query = sa_select(self.model).filter_by(**data)

                if select:
                    include_fields = [field for field in select if not field.startswith('-')]
                    exclude_fields = [field[1:] for field in select if field.startswith('-')]

                    if include_fields:
                        fields_to_select = [getattr(self.model, field) for field in include_fields]
                        query = sa_select(*fields_to_select).filter_by(**data)
                    else:
                        all_fields = set(self.model.__table__.columns.keys())
                        fields_to_select = [getattr(self.model, field) for field in all_fields if field not in exclude_fields]
                        query = sa_select(*fields_to_select).filter_by(**data)

                # Execute the query with AsyncSession
                result = await session.execute(query)
                db_item_selected = result.scalar()

                # Convert to dict for JSON serialization
                result_dict = sqlalchemy_obj_to_dict(db_item_selected)
                if isinstance(result_dict, dict) and "password" in result_dict:
                    del result_dict["password"]
                
                return response_message(
                    data=result_dict, 
                    doc_length=1, 
                    error=None, 
                    message="Data fetched successfully", 
                    success_status=True
                )
            except Exception as e:
                log.logs.error(f"Error executing query: {e}")
                return response_message(
                    data=None, 
                    doc_length=0, 
                    error=str(e), 
                    message="Error fetching data", 
                    success_status=False
                )