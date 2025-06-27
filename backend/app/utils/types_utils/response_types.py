from typing import Any, TypedDict


# The above class is a type hint for a dictionary that specifies the structure of the dictionary.
class ResponseT(TypedDict):
    message: str
    data: dict[str, Any]
    success_status: bool




class ResponseMessage(TypedDict):
    success_status: bool
    message: str
    error: Any
    data: Any
    doc_length: int | None


def response_message(
    success_status: bool,
    message: str,
    error: Any | None = None,
    data: Any | None = None,
    doc_length: int | None = None,
) -> ResponseMessage:
    if success_status:
        return {
            "success_status": success_status,
            "message": message,
            "data": data,
            "doc_length": doc_length,
            "error": None,
        }
    else:
        return {
            "success_status": success_status,
            "message": message,
            "error": str(error),
            "doc_length": doc_length,
            "data": None,
        }
