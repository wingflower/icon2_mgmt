from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends
from starlette.responses import Response
from starlette.requests import Request
from starlette.responses import JSONResponse

from sqlalchemy.orm import Session
from inspect import currentframe as frame

from datetime import datetime, timedelta

import time

from app.database.conn import db
from app.database.schema import ICONNodeKeys, ICONNetworks
from app.models.icon_models import (
    AddICONNodeKey, GetICONNodeKey, ICONNetwork,
    GetICONDictResponse, GetICONListResponse, ICONAPIParams
)
from app.utils.icon_api_utils import (
    is_success, IconAPI,
    get_icon
)
from app.utils.base_utils import (
    jequest
)


HEAD = {'content-type': 'application/json'}
router = APIRouter(prefix="/api")


def _hex_to_int(s):
    hex_int = round(int(s, 16)/10**18, 8)
    if hex_int == 0:
        return int(s, 16)
    return hex_int


@router.post("/")
async def test():
    current_time = datetime.utcnow()
    return Response(f"ICON API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")


@router.post("/wallet/info", response_model=GetICONDictResponse)
async def wallet_info(request: Request, params: ICONAPIParams):
    rs_dict = dict()
    rs_dict["balance"] = is_success(
        jequest(params.endpoint, method="post", payload=IconAPI.get_balance(params.wallet_addr))
    )
    rs_dict["stake"] = is_success(
        jequest(params.endpoint, method="post", payload=IconAPI.get_stake(params.wallet_addr))
    )
    rs_dict["delegation"] = is_success(
        jequest(params.endpoint, method="post", payload=IconAPI.get_delegation(params.wallet_addr))
    )
    rs_dict["bonder_list"] = is_success(
        jequest(params.endpoint, method="post", payload=IconAPI.get_bonder_list(params.wallet_addr))
    )
    rs_dict["bond"] = is_success(
        jequest(params.endpoint, method="post", payload=IconAPI.get_bond(params.wallet_addr))
    )
    return rs_dict



@router.post("/wallet/list", response_model=List[GetICONNodeKey])
async def get_wallet_list(request: Request, params: ICONAPIParams):
    icon_node_keys = ICONNodeKeys.filter(network=params.network_name)
    return icon_node_keys


@router.post("/balance", response_model=GetICONDictResponse)
async def balance(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_balance(params.wallet_addr, debug=True)
    ))
    return res


@router.post("/balance/send", response_model=GetICONDictResponse)
async def send_icx(request: Request, params: ICONAPIParams):
    icon = get_icon(vars(params))
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=icon.send_icx(params.icx, params.wallet_to)
    ))
    return res


@router.post("/stake", response_model=GetICONDictResponse)
async def stake(request: Request,params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_stake(params.wallet_addr)
    ))
    return res


@router.post("/stake/set", response_model=GetICONDictResponse)
async def set_stake(request: Request, params: ICONAPIParams):
    icon = get_icon(vars(params))
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=icon.set_stake(params.icx)
    ))
    return res


@router.post("/delegation", response_model=GetICONDictResponse)
async def delegation(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_delegation(params.wallet_addr)
    ))
    return res


@router.post("/delegation/set", response_model=GetICONDictResponse)
async def set_delegation(request: Request, params: ICONAPIParams):
    icon = get_icon(vars(params))
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=icon.set_delegation(params.delegation)
    ))
    return res


@router.post("/bonders", response_model=GetICONDictResponse)
async def bonder_list(request: Request,params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_bonder_list(params.wallet_addr)
    ))
    return res


@router.post("/bonders/set", response_model=GetICONDictResponse)
async def set_bonder_list(request: Request, params: ICONAPIParams):
    icon = get_icon(vars(params))
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=icon.set_bonder_list(params.bonderlist)
    ))
    return res


@router.post("/bond", response_model=GetICONDictResponse)
async def bond(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_bond(params.wallet_addr)
    ))
    return res


@router.post("/bond/set", response_model=GetICONDictResponse)
async def set_bond(request: Request, params: ICONAPIParams):
    icon = get_icon(vars(params))
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=icon.set_bond(params.bond)
    ))
    return res


@router.post("/iscore", response_model=GetICONDictResponse)
async def iscore(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_iscore(params.wallet_addr)
    ))
    return res


@router.post("/claim", response_model=GetICONDictResponse)
async def claim_iscore(request: Request, params: ICONAPIParams):
    icon = get_icon(vars(params))
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=icon.claim_iscore()
    ))
    return res


@router.post("/block", response_model=GetICONDictResponse)
async def last_block(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_last_block()
    ))
    return res


@router.post("/block/{bh}", response_model=GetICONDictResponse)
async def block(request: Request, bh: int, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_block_hash(bh)
    ))
    return res


@router.post("/prep", response_model=GetICONDictResponse)
async def prep(request: Request, addr: str, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_prep(params.wallet_addr)
    ))
    return res


@router.post("/preps", response_model=GetICONDictResponse)
async def preps(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_preps()
    ))
    return res


@router.post("/preps/main", response_model=GetICONDictResponse)
async def main_preps(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_main_preps()
    ))
    return res


@router.post("/preps/sub", response_model=GetICONDictResponse)
async def sub_preps(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_sub_preps()
    ))
    return res


@router.post("/last/leader", response_model=GetICONDictResponse)
def leader(request: Request, params: ICONAPIParams):
    block = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_last_block()
    ))
    preps = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_preps()
    ))
    try:
        for prep in preps['result']['result']['preps']:
            if prep['nodeAddress'] == block['result']['result']['peer_id']:
                return prep
        return {"error": "Leader not found."}
    except:
        return {"error": "Leader not found."}


@router.post("/last/rep", response_model=GetICONDictResponse)
async def last_rep(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_rep()
    ))
    return res


@router.post("/iiss", response_model=GetICONDictResponse)
async def iiss(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_iiss_info()
    ))
    return res


@router.post("/revision", response_model=GetICONDictResponse)
async def revision(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_revision()
    ))
    return res


@router.post("/tx", response_model=GetICONDictResponse)
async def tx(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_tx_result(params.tx)
    ))
    return res


@router.post("/trace/{tx_hash}", response_model=GetICONDictResponse)
async def trace(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.debug_get_trace(params.tx)
    ))
    return res


@router.post("/supply", response_model=GetICONDictResponse)
async def total_supply(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_total_supply()
    ))
    res["min_delegation"] = round(int(res['result']['result'], 16)/10**18, 8)/500
    return res


@router.post("/term", response_model=GetICONDictResponse)
async def prep_term(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_prep_term()
    ))
    now_bh = _hex_to_int(res['response']['result']['result']['blockHeight'])
    end_bh = _hex_to_int(res['response']['result']['result']['endBlockHeight'])
    left_bh = int(end_bh) - int(now_bh)
    left_time = timedelta(seconds=left_bh*2)
    next_term = datetime.now() + left_time
    res['response']['result']['result']['block_info'] = f"{now_bh} | {end_bh} | {left_bh}"
    res['response']['result']['result']['left_time'] = str(left_time)
    res['response']['result']['result']['next_term'] = next_term.strftime('%Y-%m-%d %H:%M:%S')
    return res


@router.post("/config/network", response_model=GetICONDictResponse)
async def network(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_network_info()
    ))
    return res


@router.post("/config/version", response_model=GetICONDictResponse)
async def version(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_version()
    ))
    return res


@router.post("/config/sevice", response_model=GetICONDictResponse)
async def service_config(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_service_config()
    ))
    return res


@router.post("/score/status", response_model=GetICONDictResponse)
async def score_status(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_score_status(params.score_addr)
    ))
    return res


@router.post("/score/api", response_model=GetICONDictResponse)
async def score_api(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_score_api(params.score_addr)
    ))
    return res


@router.post("/score/call", response_model=GetICONDictResponse)
async def score_call(request: Request, params: ICONAPIParams):
    return {}


@router.post("/step/price", response_model=GetICONDictResponse)
async def step_price(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_step_price()
    ))
    return res


@router.post("/step/costs", response_model=GetICONDictResponse)
async def step_costs(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_step_costs()
    ))
    return res


@router.post("/proposal/register", response_model=GetICONDictResponse)
async def register_proposal(request: Request, params: ICONAPIParams):
    icon = get_icon(vars(params))
    rp_res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=icon.register_proposal(params.register_proposal)
    ))
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_tx_result(rp_res['result']['result'])
    ))
    return res


@router.post("/proposal/vote/all", response_model=GetICONListResponse)
async def vote_proposal(request: Request, params: ICONAPIParams):
    tx_list = list()
    rs_list = list()
    net_info = ICONNetworks.get(name=params.network_name)
    wallet_list = ICONNodeKeys.filter(network_id=net_info.id).all()
    for wallet in wallet_list:
        params.pk = wallet.pk
        sub_icon = get_icon(vars(params))
        sub_res = is_success(jequest(
            params.endpoint,
            method="post",
            payload=sub_icon.vote_proposal(params.vote_proposal)
        ))
        tx_list.append(sub_res['result']['result'])
    time.sleep(5)
    for tx in tx_list:
        rs_list.append(is_success(jequest(
            params.endpoint,
            method="post",
            payload=IconAPI.get_tx_result(tx))
        ))
    return tx_list


@router.post("/proposal/vote", response_model=GetICONDictResponse)
async def vote_proposal(request: Request, params: ICONAPIParams):
    icon = get_icon(vars(params))
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=icon.vote_proposal(params.vote_proposal)
    ))
    return res


@router.post("/proposal/cancel/", response_model=GetICONDictResponse)
async def cancel_proposal(request: Request, params: ICONAPIParams):
    icon = get_icon(vars(params))
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=icon.cancel_proposal(params.tx_hash)
    ))
    return res


@router.post("/proposal/get/", response_model=GetICONDictResponse)
async def get_proposal(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_proposal(params.tx_hash)
    ))
    return res


@router.post("/proposal/get/all", response_model=GetICONDictResponse)
async def get_proposals(request: Request, params: ICONAPIParams):
    res = is_success(jequest(
        params.endpoint,
        method="post",
        payload=IconAPI.get_proposals(params.get_proposals)
    ))
    return res
