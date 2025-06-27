from fastapi import status
from fastapi.responses import JSONResponse

from app.core.app import init_app
from app.utils.types_utils.response_types import response_message

app = init_app()

# app.add_middleware(AuthMiddleware, db_session=session_manager)


# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.on_event("startup")


@app.get("/")
async def root():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_message(
            data="welcome to Mediguard API",
            success_status=True,
            message="success",
        ),
    )
