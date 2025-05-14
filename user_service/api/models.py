from pydantic import BaseModel
from typing import Optional

class User_sc(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    password:Optional[str]

class Token(BaseModel):
    access_token: str
    token_type: str