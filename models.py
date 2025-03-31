from pydantic import BaseModel, validator
from typing import Optional

class Gift(BaseModel):
    id: str
    name: str
    cost: float
    link: str
    photo: Optional[str]
    is_reserved: bool
    reserve_owner: Optional[str]
    user_id: str
    
    
    @validator('cost')
    def check_cost(cls, value):
        if not isinstance(value, float) :
            raise ValueError('Cost must be a valid number')
        return value

class User(BaseModel):
    user_id: str
    username: str
    password: Optional[str]
    