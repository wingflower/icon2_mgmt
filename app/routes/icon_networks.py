from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends
from starlette.responses import Response

from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse
from inspect import currentframe as frame

from app.database.conn import db
from app.database.schema import ICONNetworks, Connections
from app.models.icon_models import AddICONNetwork, GetICONNetwork

router = APIRouter(prefix="/network")


@router.get("/")
async def test():
    current_time = datetime.utcnow()
    return Response(f"ICON Networks (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")


@router.get("/test", response_model=List[GetICONNetwork])
async def test():
    all_data = ICONNetworks.filter().all()
    return all_data


@router.get('/list', response_model=List[GetICONNetwork])
async def get_list(request: Request):
    icon_networks_info = ICONNetworks.filter().all()
    if not icon_networks_info:
        return JSONResponse(status_code=400, content=dict(msg="No data"))
    for icon_network in icon_networks_info:
        icon_network.connection_info = Connections.get(id=icon_network.connection_id)
    return icon_networks_info


@router.post("/register", status_code=201, response_model=GetICONNetwork)
async def add_icon_network(params: AddICONNetwork, session: Session = Depends(db.session)):
    """
    `Register key of machine`\n
    :param params:
    :param session:
    :return:
    """
    is_exist = await is_network_exist(name=params.name)
    if not params.name or not params.tag_env or not params.tag_role:
        return JSONResponse(status_code=400, content=dict(msg="Name, tag must be provided'"))
    if is_exist:
        return JSONResponse(status_code=400, content=dict(msg="ICON_NETWORK_NOT_EXISTS"))
    rs_network = ICONNetworks.create(session, auto_commit=True,
                                     name=params.name,
                                     connection_id=params.connection_id,
                                     tag_env=params.tag_env,
                                     tag_role=params.tag_role,
                                     memo=params.memo)
    return rs_network


@router.delete('/register/{network_id}')
async def del_icon_network(request: Request, network_id: int):
    is_exist = await is_network_exist(id=network_id)
    if not is_exist:
        return JSONResponse(status_code=400, content=dict(msg="ICON_NETWORK_NOT_EXISTS"))
    ICONNetworks.filter(id=network_id).delete(auto_commit=True)


async def is_network_exist(**kwargs):
    get_email = ICONNetworks.get(**kwargs)
    if get_email:
        return True
    return False
