from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

class UserLogin(BaseModel):
    email: str
    password: str

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class Post(PostBase):
    post_id: int
    post_created: datetime
    number_votes: int = 0
    user: UserOut

class PostCreate(PostBase):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class Vote(BaseModel):
    post_id: int
    dir: int = Field(..., ge=0, le=1)