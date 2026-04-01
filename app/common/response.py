from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class ResponseSchema(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None

def create_response(data: Any = None, message: str = "Operation successful", success: bool = True) -> ResponseSchema[Any]:
    return ResponseSchema(success=success, message=message, data=data)
