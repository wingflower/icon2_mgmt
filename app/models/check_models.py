from datetime import datetime
from enum import Enum

from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import EmailStr, IPvAnyAddress


class Checker(BaseModel):
    name: str = None

    class Config:
        from_attributes = True
        # orm_mode = True


class AddCheckUrl(Checker):
    url: str = None
    access_type: str = None
    memo: str = None


class GetCheckUrl(AddCheckUrl):
    id: int = None
    running: str = None
    created_at: datetime = None
