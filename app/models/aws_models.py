from datetime import datetime
from enum import Enum

from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import EmailStr, IPvAnyAddress


class EC2(BaseModel):
    ip_addr: str = None
    profile: str = None
    tag_env: str = None
    tag_role: str = None


class ChangeEC2State(EC2):
    network: str = None
    state: str = None


class ChangeELBState(BaseModel):
    state: str = None


class ChangeEIPState(BaseModel):
    connection: str = None
    state: str = None


class ChangeSGState(BaseModel):
    state: str = None


class ChangeS3State(BaseModel):
    connection: str = None
    state: str = None