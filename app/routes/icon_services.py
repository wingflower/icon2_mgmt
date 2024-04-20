from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends
from starlette.responses import Response

from sqlalchemy.orm import Session
from starlette.responses import Response
from starlette.requests import Request
from starlette.responses import JSONResponse
from inspect import currentframe as frame

from app.database.conn import db
from app.database.schema import ICONServices, Users
from app.models.icon_models import AddICONService, GetICONService

router = APIRouter(prefix="/service")


@router.get("/")
async def test():
    current_time = datetime.utcnow()
    return Response(f"ICON Services (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")


@router.get('/list', response_model=List[GetICONService])
async def get_list(request: Request):
    icon_services_info = ICONServices.filter().all()
    if not icon_services_info:
        return JSONResponse(status_code=400, content=dict(msg="No data"))
    for icon_service in icon_services_info:
        icon_service.user_info = Users.filter(service_id=icon_service.id).all()
    return icon_services_info


@router.post("/register", status_code=201, response_model=GetICONService)
async def add_icon_service(params: AddICONService, session: Session = Depends(db.session)):
    """
    `Register key of machine`\n
    :return:
    :param params:
    :param session:
    :return:
    """
    is_exist = await is_network_exist(name=params.name)
    if not params.name:
        return JSONResponse(status_code=400, content=dict(msg="Name must be provided'"))
    if is_exist:
        return JSONResponse(status_code=400, content=dict(msg="MACHINE_KEY_NOT_EXISTS"))
    rs_network = ICONServices.create(session, auto_commit=True,
                                     name=params.name,
                                     dns=params.dns,
                                     access_type=params.access_type,
                                     memo=params.memo)
    return rs_network


@router.delete('/register/{service_id}')
async def del_icon_service(request: Request, service_id: int):
    is_exist = await is_network_exist(id=service_id)
    if not is_exist:
        return JSONResponse(status_code=400, content=dict(msg="ICON_SERVICE_NOT_EXISTS"))
    ICONServices.filter(id=service_id).delete(auto_commit=True)


async def is_network_exist(**kwargs):
    get_email = ICONServices.get(**kwargs)
    if get_email:
        return True
    return False
