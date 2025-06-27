from enum import Enum
from typing import TypedDict

from fastapi import APIRouter


class RouterData(TypedDict):
    path:str
    tags:list[str|Enum]

    api_route:APIRouter