from fastapi import FastAPI

from .v1 import routesV1


def handle_routing(app:FastAPI):
    for route in routesV1:
        app.include_router(router=route['api_route'], prefix=f"/api/v1/{route['path']}", tags=route['tags'])