from typing import List
from datetime import datetime
from random import randint

from fastapi import APIRouter, Depends
from starlette.responses import Response
from starlette.requests import Request
from starlette.responses import JSONResponse

from sqlalchemy.orm import Session
from inspect import currentframe as frame

from app.database.conn import db
from app.models.qa_models import AddQA

import json

router = APIRouter(prefix="/logsee")


@router.get("/")
async def test():
    current_time = datetime.utcnow()
    return Response(f"LogSee API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")