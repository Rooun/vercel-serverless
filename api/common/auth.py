import jwt
import time
from flask import Blueprint, Flask, send_file, request, jsonify, make_response, render_template

JWT_KEY= 'root@zhaojiakun.com&&looham.com:/home'

# 获取jwt token
def get_jwt_token(username):
    global JWT_KEY
    token_data = {
        "alg": "HS256",
        'username': username,
        'datetime': str(time.strftime("%Y-%m-%d"))
    }
    token = jwt.encode(token_data, JWT_KEY, algorithm='HS256')
    return token

# 获取jwt username
def get_jwt_username(token):
    try:
        username = jwt.decode(token, JWT_KEY, algorithms=['HS256'])
    except:
        return ""

    return username["username"]

# 定义鉴权装饰器
def auth_required(func):
    def wrapper(*args, **kwargs):
        if 'Authorization' in request.headers:
            token = request.headers.get('Authorization')
            try:
                username = jwt.decode(token, JWT_KEY, algorithms=['HS256'])
            except:
                return '', 403

            return func(*args, **kwargs)
        else:
            return '', 403

    wrapper.__name__ = func.__name__
    return wrapper
