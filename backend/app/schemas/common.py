from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Envelope(BaseModel, Generic[T]):
    """Every API response uses this shape: {success, data, message}."""

    success: bool = True
    data: Optional[T] = None
    message: str = ""
