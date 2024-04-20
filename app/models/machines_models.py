from datetime import datetime
from enum import Enum

from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import EmailStr, IPvAnyAddress

from app.models.icon_models import AddICONNetwork, AddICONService


class Machine(BaseModel):
    name: str = None

    class Config:
        orm_mode = True


class AddMachine(Machine):
    region: str = None
    instance_id: str = None
    ip: str = None
    network_id: int = None
    service_id: int = None
    memo: str = None


class GetMachine(AddMachine):
    id: int = None
    network_info: AddICONNetwork = None
    service_info: AddICONService = None
    created_at: datetime = None
