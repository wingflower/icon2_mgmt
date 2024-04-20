from starlette.requests import Request

from app.database.schema import Users

import requests


async def auth_level(request: Request, level: str):
    user_levels = {"s": 5, "a": 4, "b": 3, "c": 2, "d": 1, "e": 0}
    user = request.state.user
    user_info = Users.get(id=user.id)
    if user_info.level not in [lv for lv, h in user_levels if h >= user_levels[level]]:
        return False
    else:
        return True


async def url_running(url: str):
    try:
        response = requests.head(url, verify=False)
        if response.status_code == 200:
            return "on"
        else:
            return f"Status code = {response.status_code}"
    except Exception as e:
        return str(e)
