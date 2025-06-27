from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database.db import session_manager
from app.config.env import env
from app.core.auth.services.middleware_auth import AuthMiddleware
from app.core.versions.route_handler import handle_routing


def init_app(init_db=True):
    app: FastAPI = FastAPI(title="mediguard project")
    origins = [
    
        "http://localhost:5173",
        "http://localhost.tiangolo.com",
        "https://localhost.tiangolo.com",
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:5150",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Add middleware before the lifespan context
    app.add_middleware(AuthMiddleware, db_session=session_manager)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            if init_db:
                session_manager.init(env["database_url"])
                async with session_manager.connect() as connection:
                  

                    await session_manager.create_all(connection)
                    # await session_manager.drop_all(connection)
            yield
        finally:
            if session_manager._engine is not None:
                await session_manager.close()

    app.router.lifespan_context = lifespan
    handle_routing(app=app)
    return app
