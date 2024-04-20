from datetime import datetime

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from starlette.responses import Response
from starlette.requests import Request
from inspect import currentframe as frame

from app.models.aws_models import (
    ChangeEC2State, ChangeELBState, ChangeEIPState,
    ChangeSGState, ChangeS3State
)
from app.database.conn import db
from app.database.schema import Machines, ICONNetworks, Connections
from app.utils.aws_utils import (
    get_session, control_ec2, control_elb,
    control_eip, control_sg, control_s3
)

router = APIRouter(prefix="/aws")


@router.get("/")
async def test():
    current_time = datetime.utcnow()
    return Response(f"AWS API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")


@router.post("/ec2/control/{ec2_cmd}", response_model=None)
async def ec2_state(request: Request, ec2_cmd: str, ec2_info: ChangeEC2State, session: Session = Depends(db.session)):
    rg_ids = dict()
    network_info = ICONNetworks.get(name=ec2_info.network)
    connection_info = Connections.get(id=network_info.connection_id)
    machines = Machines.filter(network_info=network_info.id).all()
    rg_ids['connection'] = get_session(connection_info.name)
    for machine in machines:
        if rg_ids.get(machine.region):
            rg_ids[machine.region].append(machine.instance_id)
        else:
            rg_ids[machine.region] = [machine.instance_id]
    control_ec2(ec2_cmd, ec2_info, rg_ids)


@router.post("/elb/control/{elb_cmd}", response_model=None)
async def elb_state(request: Request, elb_cmd: str, elb_info: ChangeELBState, session: Session = Depends(db.session)):
    rg_ids = dict()
    network_info = ICONNetworks.get(name=elb_info.network)
    connection_info = Connections.get(id=network_info.connection_id)
    machines = Machines.filter(network_info=network_info.id).all()
    rg_ids['connection'] = get_session(connection_info.name)
    for machine in machines:
        if rg_ids.get(machine.region):
            rg_ids[machine.region].append(machine.instance_id)
        else:
            rg_ids[machine.region] = [machine.instance_id]
    control_elb(elb_cmd, elb_info, rg_ids)


@router.post("/eip/control/{eip_cmd}", response_model=None)
async def eip_state(request: Request, eip_cmd: str, eip_info: ChangeEIPState, session: Session = Depends(db.session)):
    rg_ids = dict()
    rg_ids['connection'] = get_session(eip_info.connection)
    control_eip(rg_ids)


@router.post("/sg/control/{sg_cmd}", response_model=None)
async def sg_state(request: Request, sg_cmd: str, sg_info: ChangeSGState, session: Session = Depends(db.session)):
    rg_ids = dict()
    network_info = ICONNetworks.get(name=sg_info.network)
    connection_info = Connections.get(id=network_info.connection_id)
    machines = Machines.filter(network_info=network_info.id).all()
    rg_ids['connection'] = get_session(connection_info.name)
    for machine in machines:
        if rg_ids.get(machine.region):
            rg_ids[machine.region].append(machine.instance_id)
        else:
            rg_ids[machine.region] = [machine.instance_id]
    control_sg(sg_cmd, sg_info, rg_ids)


@router.post("/s3/control/{s3_cmd}", response_model=None)
async def s3_state(request: Request, s3_cmd: str, s3_info: ChangeS3State, session: Session = Depends(db.session)):
    rg_ids = dict()
    rg_ids['connection'] = get_session(s3_info.connection)
    control_s3(s3_cmd, rg_ids)
