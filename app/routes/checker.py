from typing import List
from datetime import datetime
from random import randint

from fastapi import APIRouter, Depends, WebSocket
from starlette.responses import Response
from starlette.requests import Request
from starlette.responses import JSONResponse

from sqlalchemy.orm import Session
from inspect import currentframe as frame

from app.database.conn import db
from app.database.schema import CheckUrls
from app.models.check_models import AddCheckUrl, GetCheckUrl
from app.utils.check_utils import url_running

import json

router = APIRouter(prefix="/check")


@router.get("/")
async def test():
    current_time = datetime.utcnow()
    return Response(f"Checker API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")


@router.get('/list', response_model=List[GetCheckUrl])
async def get_list(request: Request):
    connections_info = CheckUrls.filter().all()
    if not connections_info:
        return JSONResponse(status_code=400, content=dict(msg="No data"))
    return connections_info


@router.websocket("/check/ws")
async def market_data(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print(str(randint(1, int(data))))
        await websocket.send_text(str(randint(1, int(data))))


@router.get("/url", response_model=List[GetCheckUrl])
async def url_checker():
    check_urls_info = CheckUrls.filter(access_type="public").all()
    if not check_urls_info:
        return JSONResponse(status_code=400, content=dict(msg="No data"))
    for check_url in check_urls_info:
        check_url.running = await url_running(check_url.url)
    return check_urls_info


@router.post("/url/register", status_code=201, response_model=GetCheckUrl)
async def add_check_url(params: AddCheckUrl, session: Session = Depends(db.session)):
    """

    :param params:
    :param session:
    :return:
    """
    is_exist = await is_url_exist(url=params.url)
    if not params.name or not params.url:
        return JSONResponse(status_code=400, content=dict(msg="Name, url must be provided'"))
    if is_exist:
        return JSONResponse(status_code=400, content=dict(msg="CHECK_URL_NOT_EXISTS"))
    rs_check_url = CheckUrls.create(session, auto_commit=True,
                                    name=params.name,
                                    url=params.url,
                                    access_type=params.access_type,
                                    memo=params.memo)
    return rs_check_url


@router.delete('/url/register/{url_id}')
async def del_check_url(request: Request, url_id: int):
    is_exist = await is_url_exist(id=url_id)
    if not is_exist:
        return JSONResponse(status_code=400, content=dict(msg="CHECK_URL_KEY_NOT_EXISTS"))
    CheckUrls.filter(id=url_id).delete(auto_commit=True)


async def is_url_exist(**kwargs):
    get_service = CheckUrls.get(**kwargs)
    if get_service:
        return True
    return False
