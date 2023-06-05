import time
import datetime
from common import auth
from common import postgres
from flask import Blueprint, Flask, send_file, request, jsonify, make_response, render_template

auth_module = Blueprint('auth', __name__, url_prefix='/api/v1')

@auth_module.route('login', methods=['POST'])
def v1_login():
    jsonData = request.get_json()
    form = request.form.to_dict()
    username, password = "", ""
    if ('username' in form and 'password' in form):
        username = form['username']
        password = form['password']

    if ('username' in jsonData and 'password' in jsonData):
        username = jsonData['username']
        password = jsonData['password']

    if username == "" or password == "":
        return jsonify({'code': 400, 'data': {}, 'msg': 'Input parameter error'})

    global jwt_key
    is_sign_up = False
    is_match = False
    for row in postgres.select_to_array("SELECT username,password FROM users WHERE username = '{}'".format(username)):
        if (row[0] == username):
            is_sign_up = True
            if (row[1] == password):
                is_match = True

    if (not is_sign_up):
        # 未注册，注册并登录
        form['roles'] = 'guest'
        form['username'] = username
        form['password'] = password
        form['create_at'] = datetime.datetime.utcfromtimestamp(time.time())
        # form['create_at'] = datetime.datetime.utcfromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%s")
        form['last_login_at'] = form['create_at']
        is_ok = postgres.insert('users', [x for x in form], [("'{}'").format(x) for x in form.values()])
        if (is_ok):
            token = auth.get_jwt_token(username)
            return jsonify({'code': 0, 'data': token, 'msg': 'successfully registered and logged in'})
        else:
            return jsonify({'code': 500, 'data': token, 'msg': 'database error'})

    if (not is_match):
        # 密码不匹配
        return jsonify({'code': 400, 'data': {}, 'msg': 'password is not correct'})

    # 登录
    form['last_login_at'] = datetime.datetime.utcfromtimestamp(time.time())
    is_ok = postgres.exec('UPDATE users SET last_login_at = \'{}\' WHERE username = \'{}\''.format(form['last_login_at'], username))
    if (is_ok):
        token = auth.get_jwt_token(username)
        return jsonify({'code': 0, 'data': token, 'msg': 'successfully registered and logged in'})
    else:
        return jsonify({'code': 500, 'data': '', 'msg': 'error'})

