# -*- coding: utf-8 -*-
import time
import json

from termcolor import cprint
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.wallet.wallet import KeyWallet
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.builder.transaction_builder import (
    TransactionBuilder,
    DeployTransactionBuilder,
    CallTransactionBuilder,
    MessageTransactionBuilder
)

from app.utils.base_utils import jequest, dump


TINT_VALUE = 10**18
ZERO_ADDRESS = "cx0000000000000000000000000000000000000000"
ONE_ADDRESS = "cx0000000000000000000000000000000000000001"
STEP_LIMIT = 20000000000


def print_payload(payload):
    print(" - PAYLOAD : \n", payload)
    dump(payload)


def is_success(res):
    if res['status_code'] == 200 and res['result'].get('result'):
        return {"response": res}
    else:
        return {'response': res}


def get_icon(params):
    if params.get("pk"):
        icon = IconAPI(
            params.get("endpoint"),
            int(params.get("nid"), 16),
            wallet_pk=params.get("wallet_pk")
        )
    else:
        icon = IconAPI(
            params.get("endpoint"),
            int(params.get("nid"), 16),
            wallet_file=params.get("wallet_file"),
            wallet_passwd=params.get("wallet_password"),
        )
    return icon


class IconAPI:
    def __init__(self, end_point, nid, wallet_file=None, wallet_pk=None, wallet_passwd=None, new_wallet=False):
        self.end_point = end_point
        self.wallet = self.get_wallet(wallet_file, wallet_pk, wallet_passwd, new_wallet)
        self.icon_service = IconService(HTTPProvider(end_point, 3))
        self.nid = nid

    def get_wallet(self, wallet_file=None, wallet_pk=None, wallet_passwd=None, new_wallet=False, debug=False):
        if new_wallet:
            wallet = KeyWallet.create()
            wallet.store(wallet_file, wallet_passwd)
        else:
            if wallet_file is None:
                if wallet_pk:
                    wallet = KeyWallet.load(bytes.fromhex(wallet_pk))
                else:
                    if debug:
                        cprint('No wallet file(or pk) & password', 'red')
            else:
                wallet = KeyWallet.load(wallet_file, wallet_passwd)
        return wallet

    @staticmethod
    def get_payload(method=None):
        return {
            "id": 1234,
            "jsonrpc": "2.0",
            "method": method
        }

    def get_tx(self, _from, _to, value=1, step_limit=STEP_LIMIT):
        tx = TransactionBuilder() \
            .from_(_from) \
            .to(_to) \
            .value(int(value)*TINT_VALUE) \
            .step_limit(step_limit) \
            .nid(self.nid) \
            .nonce(100) \
            .version(3) \
            .timestamp(int(time() * 10 ** 6)) \
            .build()
        return tx

    def get_dtx(self, _from, _to, content_type, content, params, step_limit=STEP_LIMIT):
        dtx = DeployTransactionBuilder() \
            .from_(_from) \
            .to(_to) \
            .step_limit(step_limit) \
            .nid(self.nid) \
            .nonce(100) \
            .content_type(content_type) \
            .content(content) \
            .params(params) \
            .build()
        return dtx

    def get_ctx(self, _from, _to, method, value, params={}, step_limit=STEP_LIMIT):
        ctx = CallTransactionBuilder() \
            .from_(_from) \
            .to(_to) \
            .step_limit(step_limit) \
            .nid(self.nid) \
            .nonce(100) \
            .method(method) \
            .value(value) \
            .params(params) \
            .build()
        return ctx

    def get_mtx(self, _from, _to, msg, step_limit=STEP_LIMIT):
        mtx = MessageTransactionBuilder() \
            .from_(_from) \
            .to(_to) \
            .step_limit(step_limit) \
            .nid(self.nid) \
            .nonce(100) \
            .data(msg) \
            .build()
        return mtx

    def get_signature(self, tx):
        signed_transaction = SignedTransaction(tx, self.wallet)
        return signed_transaction.signed_transaction_dict

    @staticmethod
    def get_last_block(debug=False):
        payload = IconAPI.get_payload('icx_getLastBlock')
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_block_height(bh, debug=False):
        payload = IconAPI.get_payload('icx_getBlockByHeight')
        payload["params"] = {
            "height": bh
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_block_hash(bh, debug=False):
        payload = IconAPI.get_payload('icx_getBlockByHash')
        payload["params"] = {
            "hash": bh
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_total_supply(debug=False):
        payload = IconAPI.get_payload('icx_getTotalSupply')
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_balance(addr, debug=False):
        payload = IconAPI.get_payload('icx_getBalance')
        payload["params"] = { "address": addr }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_tx_result(tx, debug=False):
        payload = IconAPI.get_payload('icx_getTransactionResult')
        payload["params"] = { "txHash": tx }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_score_api(address=None, debug=False):
        payload = IconAPI.get_payload('icx_getScoreApi')
        payload["params"] = {
            "address": address
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_rep(debug=False):
        payload = IconAPI.get_payload("rep_getList")
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_main_preps(debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ZERO_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getMainPReps",
                "params": {}
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_sub_preps(debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ZERO_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getSubPReps",
                "params": {}
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_iiss_info(debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ZERO_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getIISSInfo",
                "params": {}
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_network_info(debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ZERO_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getNetworkInfo",
                "params": {}
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_service_config(debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ONE_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getServiceConfig",
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def debug_get_trace(tx, debug=False):
        payload = IconAPI.get_payload('debug_getTrace')
        payload["params"] = { "txHash": tx }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_prep(addr, debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ZERO_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getPRep",
                "params": {
                    "address": addr
                }
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_preps(debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ZERO_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getPReps",
                "params": {}
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_prep_term(debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ZERO_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getPRepTerm",
                "params": {}
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_stake(addr, debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ZERO_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getStake",
                "params": {
                    "address": addr
                }
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_delegation(addr, debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ZERO_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getDelegation",
                "params": {
                    "address": addr
                }
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_bonder_list(addr, debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ZERO_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getBonderList",
                "params": {
                    "address": addr
                }
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_bond(addr, debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ZERO_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getBond",
                "params": {
                    "address": addr
                }
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_version(debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ONE_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getVersion"
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_revision(debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ONE_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getRevision"
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_iscore(addr, debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ZERO_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "queryIScore",
                "params": {
                    "address": addr
                }
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_proposal(p_id, debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ONE_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getProposal",
                "params": {
                    "id": p_id
                }
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_proposals(params, debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ONE_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getProposals",
                "params": {
                    "type": params["proposal_type"],
                    "status": params["status"]
                }
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_score_status(address, debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ONE_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getScoreStatus",
                "params": {
                    "address": address
                }
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_step_price(debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ONE_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getStepPrice"
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_step_costs(debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ONE_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getStepCosts"
            }
        }
        if debug:
            print_payload(payload)
        return payload

    @staticmethod
    def get_max_step_limit(contextType="invoke", debug=False):
        payload = IconAPI.get_payload('icx_call')
        payload['params'] = {
            "to": ONE_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getMaxStepLimit",
                "params": {
                    "contextType": contextType
                }
            }
        }
        if debug:
            print_payload(payload)
        return payload

    def tx_result(self, tx_hash, debug=False):
        payload = IconAPI.get_payload('icx_getTransactionResult')
        payload['params'] = {
            "txHash": tx_hash
        }
        if debug:
            print_payload(payload)
        return payload

    def send_icx(self, icx, _to, debug=False):
        tx = self.get_tx(
            self.wallet.get_address(), _to, icx
        )
        signed_dict = self.get_signature(tx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload

    def score_install(self, debug=False):
        tx = self.get_ctx(
            self.wallet.get_address(), ZERO_ADDRESS, 'icx_sendTransaction'
        )
        signed_dict = self.get_signature(tx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload

    def score_call(self, _to, method, value, params, debug=False):
        tx = self.get_ctx(
            self.wallet.get_address(), _to, method, value, params
        )
        signed_dict = self.get_signature(tx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload

    def send_msg(self, msg=1, debug=False):
        mtx = self.get_mtx(
            self.wallet.get_address(), msg
        )
        signed_dict = self.get_signature(mtx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload

    def register(self, name, country, city, email, website, details, endpoint, value=None, debug=False):
        ctx = self.get_ctx(
            self.wallet.get_address(), ZERO_ADDRESS, 'registerPRep', value,
            {
                "name": name,
                "country": country,
                "city": city,
                "email": email,
                "website": website,
                "details": details,
                "p2pEndpoint": endpoint,
            }
        )
        signed_dict = self.get_signature(ctx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload

    def unregister(self, value=None, debug=False):
        ctx = self.get_ctx(
            self.wallet.get_address(), ZERO_ADDRESS, 'unregisterPRep', value,
            {}
        )
        signed_dict = self.get_signature(ctx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload

    def set_prep(self, name, country, city, email, website, details, endpoint, value=None, debug=False):
        ctx = self.get_ctx(
            self.wallet.get_address(), ZERO_ADDRESS, 'setPRep', value,
            {
                "name": name,
                "country": country,
                "city": city,
                "email": email,
                "website": website,
                "details": details,
                "p2pEndpoint": endpoint,
            }
        )
        signed_dict = self.get_signature(ctx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload

    def set_bonder_list(self, addr_list, value=None, debug=False):
        ctx = self.get_ctx(
            self.wallet.get_address(), ZERO_ADDRESS, 'setBonderList', value,
            {'bonderList': addr_list}
        )
        signed_dict = self.get_signature(ctx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload

    def set_stake(self, amount, value=None, debug=False):
        ctx = self.get_ctx(
            self.wallet.get_address(), ZERO_ADDRESS, 'setStake', value,
            {"value": int(amount) * TINT_VALUE}
        )
        signed_dict = self.get_signature(ctx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload

    def set_delegation(self, delegation_dict, value=None, debug=False):
        delegation_params = list()
        for to, amount in delegation_dict.items():
            delegation_params.append(
                {
                    "address": to,
                    "value": str(amount)
                }
            )
        ctx = self.get_ctx(
            self.wallet.get_address(), ZERO_ADDRESS, 'setDelegation', value,
            {
                "delegations": delegation_params
            }
        )
        signed_dict = self.get_signature(ctx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload

    def set_bond(self, bond_list, value=None, debug=False):
        ctx = self.get_ctx(
            self.wallet.get_address(), ZERO_ADDRESS, 'setBond', value,
            {
                "bonds": bond_list
            }
        )
        signed_dict = self.get_signature(ctx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload

    def claim_iscore(self, value=None, debug=False):
        ctx = self.get_ctx(
            self.wallet.get_address(), ZERO_ADDRESS, 'claimIScore', value,
            {}
        )
        signed_dict = self.get_signature(ctx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload

    def register_proposal(self, params, debug=False):
        tx = self.get_ctx(
            self.wallet.get_address(), ONE_ADDRESS, 'registerProposal', params["value"],
            {
                "title": params["title"],
                "description": params["desc"],
                "type": params["proposal_type"],
                "value": f"0x{bytes.hex(json.dumps(params['value']).encode())}"
            }
        )
        signed_dict = self.get_signature(tx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload

    def cancel_proposal(self, p_id, value=None, debug=False):
        tx = self.get_ctx(
            self.wallet.get_address(), ONE_ADDRESS, 'cancelProposal', value,
            {
                "id": p_id
            }
        )
        signed_dict = self.get_signature(tx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload

    def vote_proposal(self, params, value=None, debug=False):
        tx = self.get_ctx(
            self.wallet.get_address(), ONE_ADDRESS, 'voteProposal', value,
            {
                "id": params["proposal_id"],
                "vote": params["vote"]
            }
        )
        signed_dict = self.get_signature(tx)
        payload = IconAPI.get_payload('icx_sendTransaction')
        payload['params'] = signed_dict
        if debug:
            print_payload(payload)
        return payload
