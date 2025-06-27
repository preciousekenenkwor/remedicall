from app.core.auth.routes.auth_route import auth_router
from app.core.user.routes.user_route import user_router
from app.core.versions.types_route import RouterData

routesV1: list[RouterData] = [
    {
        "api_route": auth_router,
        "path": "auth",
        "tags": ["auth"],
    },
    {
        "api_route": user_router,
        "path": "user",
        "tags": ["user"],
    },
    
]

