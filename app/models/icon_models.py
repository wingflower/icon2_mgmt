from typing import List
from datetime import datetime
from enum import Enum

from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import EmailStr, IPvAnyAddress

from app.models.connections_models import AddConnection
from app.models.user_models import UserMe


class ICON(BaseModel):
    name: str = None

    class Config:
        from_attributes = True
        # orm_mode = True


class AddICONNetwork(ICON):
    connection_id: int
    tag_env: str = None
    tag_role: str = None
    memo: str = None


class GetICONNetwork(AddICONNetwork):
    connection_info: AddConnection = None
    network_type: str = None
    created_at: datetime = None


class AddICONService(ICON):
    dns: str = None
    access_type: str = None
    memo: str = None


class GetICONService(AddICONService):
    user_info: List[UserMe] = []
    created_at: datetime = None


class ICONType:
    network: str = "network"
    service: str = "service"
    api: str = "api"


class AddICONNodeKey(ICON):
    network_id: int = None
    machine_id: int = None
    memo: str = None


class GetICONNodeKey(AddICONNodeKey):
    key_info: str = None
    created_at: datetime = None


class GetICONDictResponse(BaseModel):
    response: dict = None


class GetICONListResponse(BaseModel):
    response: list = None


class ICONAPIParams(BaseModel):
    network_name: str = None
    wallet_addr: str = None
    score_addr: str = None
    wallet_pk: str = None
    wallet_file: str = None
    wallet_pw: str = None
    endpoint: str = None
    icx: int = None
    wallet_from: str = None
    wallet_to: str = None
    delegation: list = None
    bonderlist: list = None
    bond: list = None
    prep_cnt: int = 100
    tx_hash: str = None
    register_proposal: dict = None
    vote_proposal: dict = None


class ICONNetwork:
    mainnet: str = "mainnet"
    lisbonnet: str = "lisbonnet"
    berlinnet: str = "berlinnet"
    sejongnet: str = "sejongnet"
