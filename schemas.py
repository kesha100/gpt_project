from pydantic import BaseModel
from typing import Optional



class SignUpModel(BaseModel):
    id:Optional[int]
    username:str
    email:str
    password:str
    is_staff:Optional[bool]

class Config:
    orm_mode=True

class Settings(BaseModel):  
    auth_jwt_key: str='2e00290adfdca70fa4d2d4cbdd0573f3313b7de555730f7dd5000dc63f6d2156'

class LoginModel(BaseModel):
    username:str
    password:str