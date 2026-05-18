from pydantic import BaseModel
from typing import Any, Optional

class APIResponse(BaseModel):
    status: str   
    message: str     
    data: Optional[Any] = None 

def success_response(message: str, data: Any = None) -> APIResponse:
    return APIResponse(
        status="success",
        message=message,
        data=data
    )

def error_response(message: str, data: Any = None) -> APIResponse:
    return APIResponse(
        status="error",
        message=message,
        data=data
    )   