from common import auth
from flask import Blueprint, Flask, send_file, request, jsonify, make_response, render_template

cache_module = Blueprint('cache', __name__, url_prefix='/api/v1/cache')

ALL_CACHE = {}


@cache_module.route('get/<key>', methods=['GET'])
@auth.auth_required
def v1_cache_get(key):
    if key in ALL_CACHE:
        return jsonify({'code': 0, 'data': ALL_CACHE[key], 'msg': ''})

    return jsonify({'code': 404, 'data': {}, 'msg': ''})

@cache_module.route('set', methods=['POST'])
@auth.auth_required
def v1_cache_set():
    json = request.get_json()
    for key, value in json.items():
        ALL_CACHE[key] = value
        
    return jsonify({'code': 0, 'data': key, 'msg': ''})