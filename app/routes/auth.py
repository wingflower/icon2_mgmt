from datetime import datetime, timedelta

import bcrypt
import jwt
from fastapi import APIRouter, Depends

# TODO:
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.common.consts import JWT_SECRET, JWT_ALGORITHM
from app.database.conn import db
from app.database.schema import Users
from app.models.user_models import SnsType, Token, UserToken, UserRegister

"""
400 Bad Request
401 Unauthorized

403 Forbidden
404 Not Found
405 Method not allowed
500 Internal Error
502 Bad Gateway 
504 Timeout
200 OK
201 Created
"""


router = APIRouter(prefix="/auth")


@router.post("/register/{sns_type}", status_code=201, response_model=Token)
async def register(sns_type: SnsType, params: UserRegister, session: Session = Depends(db.session)):
    """
    `회원가입`\n
    :param sns_type:
    :param reg_info:
    :param session:
    :return:
    """
    if sns_type == SnsType.email:
        is_exist = await is_email_exist(params.email)
        if not params.email or not params.pw:
            return JSONResponse(status_code=400, content=dict(msg="Email and PW must be provided"))
        if is_exist:
            return JSONResponse(status_code=400, content=dict(msg="EMAIL_EXISTS"))
        hash_pw = bcrypt.hashpw(params.pw.encode("utf-8"), bcrypt.gensalt())
        new_user = Users.create(session, auto_commit=True, pw=hash_pw, email=params.email)
        token = dict(Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(new_user).dict(exclude={'pw', 'marketing_agree'}),)}")
        return token
    return JSONResponse(status_code=400, content=dict(msg="NOT_SUPPORTED"))


@router.post("/login/{sns_type}", status_code=200, response_model=Token)
async def login(sns_type: SnsType, params: UserRegister):
    """
    `로그인`\n
    :param sns_type:
    :param user_info:
    :return:
    """
    if sns_type == SnsType.email:
        is_exist = await is_email_exist(params.email)
        if not params.email or not params.pw:
            return JSONResponse(status_code=400, content=dict(msg="Email and PW must be provided'"))
        if not is_exist:
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))
        user = Users.get(email=params.email)
        is_verified = bcrypt.checkpw(params.pw.encode("utf-8"), user.pw.encode("utf-8"))
        if not is_verified:
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))
        token = dict(
            Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(user).dict(exclude={'pw', 'marketing_agree'}),)}")
        return token
    return JSONResponse(status_code=400, content=dict(msg="NOT_SUPPORTED"))


async def is_email_exist(email: str):
    get_email = Users.get(email=email)
    if get_email:
        return True
    return False


def create_access_token(*, data: dict = None, expires_delta: int = None):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt
