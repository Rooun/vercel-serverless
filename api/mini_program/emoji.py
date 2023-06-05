import os
import time
import datetime
from api.common import auth
from api.common import postgres
from flask import Blueprint, Flask, send_file, request, jsonify, make_response, render_template

mp_emoji_module = Blueprint('mp_emoji', __name__, url_prefix='/api/v1/mp/emoji')


@mp_emoji_module.route('list', methods=['GET'])
@auth.auth_required
def mp_emoji_list():
    emojis = []
    emoji_path = os.path.join(os.getcwd(), "static", "emojis")
    for _, _, files in os.walk(emoji_path):
        emoji = files

    return jsonify({'code': 0, 'data': emoji, 'msg': ''})
    


@mp_emoji_module.route('source/<name>', methods=['GET'])
@auth.auth_required
def mp_emoji_source(name):
    emoji_path = os.path.join(os.getcwd(), "static", "emojis", name)
    if os.path.exists(emoji_path):
        return send_file(emoji_path)

    return jsonify({'code': 404, 'msg': 'page does not exist'})