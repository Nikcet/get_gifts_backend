from pydantic import BaseModel, validator
from typing import Optional

class Gift(BaseModel):
    id: str
    name: str
    cost: float
    link: str
    photo: Optional[str]
    is_reserved: bool
    user_id: str
    
    
    @validator('cost')
    def check_cost(cls, value):
        if not isinstance(value, float) :
            raise ValueError('Cost must be a valid number')
        return value

class User(BaseModel):
    id: str
    username: str
    password: str
    