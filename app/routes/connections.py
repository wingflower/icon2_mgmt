from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends
from starlette.responses import Response

from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse
from inspect import currentframe as frame

from app.models.connections_models import ConnectionType, AddConnection, GetConnection
from app.database.conn import db
from app.database.schema import Connections

router = APIRouter(prefix="/connection")


@router.get("/")
async def test():
    current_time = datetime.utcnow()
    return Response(f"Connections API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")


@router.get('/list', response_model=List[GetConnection])
async def get_list(request: Request):
    connections_info = Connections.filter().all()
    if not connections_info:
        return JSONResponse(status_code=400, content=dict(msg="No data"))
    return connections_info


@router.post("/register/{key_type}", status_code=201, response_model=GetConnection)
async def add_key(connection_type: ConnectionType, params: AddConnection, session: Session = Depends(db.session)):
    """
    `Register key of machine`\n
    :param connection_type:
    :param params:
    :param session:
    :return:
    """
    if connection_type == ConnectionType.aws:
        is_exist = await is_connection_exist(name=params.name)
        if not params.name or not params.path:
            return JSONResponse(status_code=400, content=dict(msg="Name, path must be provided'"))
        if is_exist:
            return JSONResponse(status_code=400, content=dict(msg="CONNECTION_NOT_EXISTS"))
        rs_connection = Connections.create(session, auto_commit=True,
                                           name=params.name,
                                           path=params.path,
                                           pw=params.pw,
                                           memo=params.memo)
        return rs_connection
    return JSONResponse(status_code=400, content=dict(msg="NOT_SUPPORTED"))


@router.delete('/register/{connection_id}')
async def del_key(request: Request, connection_id: int):
    is_exist = await is_connection_exist(id=connection_id)
    if not is_exist:
        return JSONResponse(status_code=400, content=dict(msg="CONNECTION_NOT_EXISTS"))
    Connections.filter(id=connection_id).delete(auto_commit=True)


async def is_connection_exist(**kwargs):
    get_service = Connections.get(**kwargs)
    if get_service:
        return True
    return False
