from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends
from starlette.responses import Response

from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse
from inspect import currentframe as frame

from app.models.machines_models import AddMachine, GetMachine
from app.database.conn import db
from app.database.schema import Machines, ICONNetworks, ICONServices

router = APIRouter(prefix="/machine")


@router.get("/")
async def test():
    current_time = datetime.utcnow()
    return Response(f"Machine Keys API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")


@router.get('/list', response_model=List[GetMachine])
async def get_list(request: Request):
    machines_info = Machines.filter().all()
    if not machines_info:
        return JSONResponse(status_code=400, content=dict(msg="No data"))
    for machine in machines_info:
        machine.network_info = ICONNetworks.get(id=machine.network_id)
        machine.service_info = ICONServices.get(id=machine.service_id)
    return machines_info


@router.post("/register", status_code=201, response_model=GetMachine)
async def add_machine(params: AddMachine, session: Session = Depends(db.session)):
    """
    `Register key of machine`\n
    :param params:
    :param session:
    :return:
    """
    is_exist = await is_machine_exist(name=params.name, ip=params.ip)
    if not params.name or not params.region or not params.ip:
        return JSONResponse(status_code=400, content=dict(msg="Name, ip, region must be provided'"))
    if is_exist:
        return JSONResponse(status_code=400, content=dict(msg="MACHINE_NOT_EXISTS"))
    rs_machine = Machines.create(session, auto_commit=True,
                                 name=params.name,
                                 region=params.region,
                                 instance_id=params.instance_id,
                                 ip=params.ip,
                                 network_id=params.network_id,
                                 service_id=params.service_id,
                                 memo=params.memo)
    return rs_machine


@router.delete('/register/{key_id}')
async def del_machine(request: Request, machine_id: int):
    is_exist = await is_machine_exist(id=machine_id)
    if not is_exist:
        return JSONResponse(status_code=400, content=dict(msg="MACHINE_KEY_NOT_EXISTS"))
    Machines.filter(id=machine_id).delete(auto_commit=True)


async def is_machine_exist(**kwargs):
    get_service = Machines.get(**kwargs)
    if get_service:
        return True
    return False
