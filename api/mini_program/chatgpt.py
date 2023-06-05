import time
import datetime
from api.common import auth
from api.common import postgres
from flask import Blueprint, Flask, send_file, request, jsonify, make_response, render_template

mp_chatgpt_module = Blueprint('mp_chatgpt', __name__, url_prefix='/api/v1/mp/chatgpt')


@mp_chatgpt_module.route('appsecret', methods=['GET'])
@auth.auth_required
def mp_chatgpt_appsecret():

    return jsonify({'code': 0, 'data': "532b7184b206f61e6bfa0129de2065b9", 'msg': ''})

@mp_chatgpt_module.route('used/list', methods=['GET'])
@auth.auth_required
def mp_chatgpt_used_list():
    args = request.args
    page, page_size, order_by, order = 1, 0, "create_at", "ASC"
    try:
        page=int(request.args["page"])
        page_size=int(request.args["page_size"])
        order_by=request.args["order_by"]
        order=request.args["order"]
    except:
        pass

    cmd = "SELECT * FROM mp_chat_datas"
    if page_size > 0:
        cmd = "{} ORDER BY {} {}".format(cmd, order_by, order)

    usedinfo = postgres.select_to_dict(cmd)

    return jsonify({'code': 0, 'data': usedinfo, 'msg': ''})
    

@mp_chatgpt_module.route('used', methods=['POST'])
@auth.auth_required
def mp_chatgpt_used():
    json = request.get_json()
    if 'openid' not in json or 'nickname' not in json or 'data' not in json:
        return jsonify({'code': 400, 'data': {}, 'msg': 'Input parameter error'})

    json['create_at'] = datetime.datetime.utcfromtimestamp(time.time())

    is_ok = postgres.insert('mp_chat_datas', [x for x in json], [("'{}'").format(x) for x in json.values()])
    if (is_ok):
        return jsonify({'code': 0, 'data': {}, 'msg': ''})
    else:
        return jsonify({'code': 500, 'data': token, 'msg': 'database error'})