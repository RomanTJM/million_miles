from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class CarCreate(BaseModel):
    brand: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=150)
    year: int = Field(..., ge=1900, le=2100)
    price: float = Field(..., gt=0)
    color: Optional[str] = Field(None, max_length=50)
    url: str
    description: Optional[str] = None
    external_id: Optional[str] = None
    source: str = "carsensor"


class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    color: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CarResponse(BaseModel):
    id: int
    brand: str
    model: str
    year: int
    price: float
    color: Optional[str]
    url: str
    description: Optional[str]
    source: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CarsListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[CarResponse]


class ErrorResponse(BaseModel):
    detail: str
