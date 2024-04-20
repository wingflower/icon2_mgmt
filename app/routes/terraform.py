from datetime import datetime

from fastapi import APIRouter
from starlette.responses import Response
from starlette.requests import Request
from inspect import currentframe as frame

router = APIRouter(prefix="/terraform")


@router.get("/")
async def test():
    current_time = datetime.utcnow()
    return Response(f"Terraform API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")