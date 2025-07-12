from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Dict, Any

class ManageRequest(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    email: str
    cuisine_type: str
    open_time: str
    close_time: str