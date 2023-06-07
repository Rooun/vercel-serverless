import os
import jwt
import time
import json
import urllib3
import datetime
import psycopg2
import requests
from flask import Flask, send_file, request, jsonify, make_response, render_template


app = Flask(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CACHE = {
    "tokens": {},
    "labels": {}
}


JWT_KEY= 'root@looham.com'
POSTGRES_SERVER = ['welostyou.host', "30010"]




@app.route('/', methods=['GET'])
def v1_head():
    return jsonify({'code': 0, 'data': {}, 'msg': 'test'})

@app.route('/api/v1', methods=['GET'])
def v1_get():
    return jsonify({'code': 0, 'data': {}, 'msg': 'test'})




###################################
# 授权
###################################

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



###################################
# 数据库
###################################
def PG_Connect():
    global POSTGRES_SERVER
    try:
        return psycopg2.connect(database="postgres", user="postgres", password="hello.954", host=POSTGRES_SERVER[0], port=POSTGRES_SERVER[1])
    except Exception as e:
        err = str(e)
        if "could not connect to server" in err:
            print("Database connect fail: {}:{}".format(POSTGRES_SERVER[0], POSTGRES_SERVER[1]))
        else:
            print("Database connect fail: {}".format(err))

        return ""

def PG_Exec(command):
    conn = PG_Connect()
    if (conn == ""): return
    cursor = conn.cursor()
    try:
        cursor.execute(command)
    
    except Exception as e:
        print("ERROR CMD: " + command)
        return False
    
    conn.commit()
    cursor.close()
    conn.close()
    return True

def PG_Select_to_array(command):
    rows = []
    conn = PG_Connect()
    if (conn == ""): return
    cursor = conn.cursor()
    try:
        cursor.execute(command)
        rows = cursor.fetchall()
    
    except Exception as e:
        if ("does not exist" in str(e)):
            print(str(e).splitlines()[0])
        else:
            print(str(e))
    
    conn.commit()
    cursor.close()
    conn.close()
    return rows

def PG_Select_to_dict(command):
    jsonRows = []
    conn = PG_Connect()
    if (conn == ""): return
    cursor = conn.cursor()
    try:
        cursor.execute(command)
        columns = [row[0] for row in cursor.description]
        rows = [row for row in cursor.fetchall()]

        for row in rows:
            item = {}
            for index in range(len(columns)):
                item[columns[index]] = row[index]

            jsonRows.append(item)

    except Exception as e:
        if ("does not exist" in str(e)):
            print(str(e).splitlines()[0])
        else:
            print(str(e))
    
    conn.commit()
    cursor.close()
    conn.close()
    return jsonRows

def PG_Insert(tablename, column, value):
    column = ','.join(column) if (list == type(column)) else column
    value = ','.join(value) if (list == type(value)) else value
    sqlcmd = "INSERT INTO {}({}) VALUES({})".format(tablename, column, value)
    return PG_Exec(sqlcmd)



###################################
# 公共
###################################
@app.route('/api/v1/login', methods=['POST'])
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

    if username in CACHE["tokens"]:
        return jsonify({'code': 0, 'data': json.loads(CACHE["tokens"][username]), 'msg': 'successfully registered and logged in'})

    global jwt_key
    is_sign_up = False
    is_match = False
    for row in PG_Select_to_array("SELECT username,password FROM users WHERE username = '{}'".format(username)):
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
        is_ok = PG_Insert('users', [x for x in form], [("'{}'").format(x) for x in form.values()])
        if (is_ok):
            token = get_jwt_token(username)
            CACHE["tokens"][username] = token
            return jsonify({'code': 0, 'data': token, 'msg': 'successfully registered and logged in'})
        else:
            return jsonify({'code': 500, 'data': token, 'msg': 'database error'})

    if (not is_match):
        # 密码不匹配
        return jsonify({'code': 400, 'data': {}, 'msg': 'password is not correct'})

    # 登录
    form['last_login_at'] = datetime.datetime.utcfromtimestamp(time.time())
    is_ok = PG_Exec('UPDATE users SET last_login_at = \'{}\' WHERE username = \'{}\''.format(form['last_login_at'], username))
    if (is_ok):
        token = get_jwt_token(username)
        CACHE["tokens"][username] = token
        return jsonify({'code': 0, 'data': token, 'msg': 'successfully registered and logged in'})
    else:
        return jsonify({'code': 500, 'data': '', 'msg': 'error'})



###################################
# 小程序 emoji
###################################

@app.route('/api/v1/mp/emoji/list', methods=['GET'])
@auth_required
def mp_emoji_list():
    emojis = []
    emoji_path = os.path.join(os.getcwd(), "static", "emojis")
    for _, _, files in os.walk(emoji_path):
        emoji = files

    return jsonify({'code': 0, 'data': emojis, 'msg': ''})

@app.route('/api/v1/mp/emoji/source/<name>', methods=['GET'])
@auth_required
def mp_emoji_source(name):
    emoji_path = os.path.join(os.getcwd(), "static", "emojis", name)
    if os.path.exists(emoji_path):
        return send_file(emoji_path)

    return jsonify({'code': 404, 'msg': 'page does not exist'})


###################################
# 小程序 coffee
###################################

@app.route('/api/v1/mp/coffee/jscode2session', methods=['GET'])
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

@app.route('/api/v1/mp/coffee/labels', methods=['GET'])
@auth_required
def mp_coffee_get_labels():
    username = get_jwt_username(request.headers.get('Authorization'))

    if username in CACHE["labels"]:
        return jsonify({'code': 0, 'data': json.loads(CACHE["labels"][username]), 'msg': ''})

    for row in PG_Select_to_array("SELECT labels FROM mp_coffee WHERE openid = '{}'".format(username)):
        CACHE["labels"][username] = row[0]
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
    PG_Insert('mp_coffee', [x for x in data], [("'{}'").format(x) for x in data.values()])
    CACHE["labels"][username] = labels
    return jsonify({'code': 0, 'data': labels, 'msg': ''})

@app.route('/api/v1/mp/coffee/labels', methods=['POST'])
@auth_required
def mp_coffee_edit_labels():
    jsonData = request.get_json()
    if ('labels' not in jsonData):
        return jsonify({'code': 400, 'data': {}, 'msg': 'Input parameter error'})

    username = get_jwt_username(request.headers.get('Authorization'))
    CACHE["labels"][username] = jsonData['labels']
    is_ok = PG_Exec('UPDATE mp_coffee SET labels = \'{}\' WHERE openid = \'{}\''.format(json.dumps(jsonData['labels']), username))
    if (is_ok):
        return jsonify({'code': 0, 'data': '', 'msg': ''})
    else:
        return jsonify({'code': 500, 'data': '', 'msg': 'error'})