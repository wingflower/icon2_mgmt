from dataclasses import asdict
from typing import Optional
from time import time

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from app.common.consts import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX
from app.database.conn import db
from app.common.config import conf
from app.middlewares.token_validator import access_control
from app.middlewares.trusted_hosts import TrustedHostMiddleware
from app.routes import (
    index, auth, users,
    machines, connections, checker,
    icon_networks, icon_services, icon_api, tracker,
    aws, terraform, gitlab, docker,
    configure, logsee, qa
)

API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)


def create_app():
    """

    :return:
    """
    c = conf()
    app = FastAPI()
    conf_dict = asdict(c)
    db.init_app(app, **conf_dict)

    # 미들웨어 정의
    app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=access_control)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=conf().ALLOW_SITE,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=conf().TRUSTED_HOSTS, except_path=["/health"])

    # 라우터 정의
    app.include_router(index.router)
    app.include_router(auth.router, tags=["Authentication"], prefix="/api")
    app.include_router(users.router, tags=["Users"], prefix="/api", dependencies=[Depends(API_KEY_HEADER)])
    app.include_router(machines.router, tags=["Machine"])
    app.include_router(connections.router, tags=["Connection"])
    app.include_router(checker.router, tags=["Checker"])  # Public
    app.include_router(icon_networks.router, tags=["ICON Networks"], prefix="/icon")
    app.include_router(icon_services.router, tags=["ICON Services"], prefix="/icon")
    app.include_router(icon_api.router, tags=["ICON API"], prefix="/icon")
    app.include_router(tracker.router, tags=["Tracker"])
    app.include_router(aws.router, tags=["AWS"])
    app.include_router(terraform.router, tags=["Terraform"])
    app.include_router(docker.router, tags=["Docker"])
    app.include_router(configure.router, tags=["Config"])
    app.include_router(logsee.router, tags=["Log"])
    app.include_router(gitlab.router, tags=["GitLab"])
    app.include_router(qa.router, tags=["QA"])
    return app


app = create_app()


@app.on_event("startup")
async def on_app_start():
    print("-----[Welcome]-----")


@app.on_event("shutdown")
async def on_app_stop():
    print("-----[Bye]-----")


# @app.websocket_route("/ws")
# class MessagesEndpoint(WebSocketEndpoint):
#     encoding = "text"
#     last_time = 0
#
#     async def on_connect(self, websocket):
#         await websocket.accept()
#         print(f"[{time()}] connected: {websocket.client}")
#
#     async def on_receive(self, websocket: WebSocket, data) -> None:
#         self.last_time = float(data)
#         print(self.last_time)
#
#     async def on_disconnect(self, websocket, close_code):
#         print(f"[{time()}] disconnected: {websocket.client}")
#         print("delay:", time() - self.last_time)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
