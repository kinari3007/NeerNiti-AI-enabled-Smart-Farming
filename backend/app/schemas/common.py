"""
Shared schema primitives used across the API.
"""
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: list | None = None


class MessageResponse(BaseModel):
    message: str
