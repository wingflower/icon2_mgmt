from datetime import datetime
from enum import Enum

from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import EmailStr, IPvAnyAddress


class Connection(BaseModel):
    name: str = None

    class Config:
        orm_mode = True


class AddConnection(Connection):
    path: str = None
    pw: str = None
    memo: str = None


class GetConnection(AddConnection):
    id: int = None
    created_at: datetime = None


class ConnectionType(str, Enum):
    vm: str = "vm"
    aws: str = "aws"
    gcp: str = "gcp"
