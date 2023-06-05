import time
import json
import requests
import datetime
from api.common import auth
from api.common import postgres
from flask import Blueprint, Flask, send_file, request, jsonify, make_response, render_template

mp_coffee_module = Blueprint('mp_coffee', __name__, url_prefix='/api/v1/mp/coffee')


@mp_coffee_module.route('jscode2session', methods=['GET'])
def mp_coffee_jscode2session():
    args = request.args
    if 'js_code' not in args:
        return jsonify({'code': 400, 'data': {}, 'msg': 'Input parameter error'})
    
    url = "https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code".format(
        "wxb4257570e3a24598", "6d22c6762e8cfbf3abe1dc354f874ca3", args["js_code"]
    )
    response = requests.get(url)
    if response.status_code == 200:
        return jsonify({'code': 0, 'data': response.json(), 'msg': ''})
    else:
        return jsonify({'code': 500, 'data': response.json(), 'msg': 'Server error'})


@mp_coffee_module.route('labels', methods=['GET'])
@auth.auth_required
def mp_coffee_get_labels():
    username = auth.get_jwt_username(request.headers.get('Authorization'))
    for row in postgres.select_to_array("SELECT labels FROM mp_coffee WHERE openid = '{}'".format(username)):
        return jsonify({'code': 0, 'data': json.loads(row[0]), 'msg': ''})

    labels = [{
        "id": 0,
        "width": 40,
        "height": 30,
        "name": '空白标签',
        "canvas": { "id":'render-lable-0', "width": 0, "height": 0 },
        "items": [],
    }]
    data = {}
    data['openid'] = username
    data['labels'] = json.dumps(labels)
    data['create_at'] = datetime.datetime.utcfromtimestamp(time.time())
    postgres.insert('mp_coffee', [x for x in data], [("'{}'").format(x) for x in data.values()])
    return jsonify({'code': 0, 'data': labels, 'msg': ''})


@mp_coffee_module.route('labels', methods=['POST'])
@auth.auth_required
def mp_coffee_edit_labels():
    jsonData = request.get_json()
    if ('labels' not in jsonData):
        return jsonify({'code': 400, 'data': {}, 'msg': 'Input parameter error'})

    username = auth.get_jwt_username(request.headers.get('Authorization'))
    is_ok = postgres.exec('UPDATE mp_coffee SET labels = \'{}\' WHERE openid = \'{}\''.format(json.dumps(jsonData['labels']), username))
    if (is_ok):
        return jsonify({'code': 0, 'data': '', 'msg': ''})
    else:
        return jsonify({'code': 500, 'data': '', 'msg': 'error'})