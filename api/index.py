import urllib3
from flask import Flask, jsonify
# from common.log import logger
# from auth.auth import auth_module
# from common.cache import cache_module
# from mini_program.emoji import mp_emoji_module
# from mini_program.coffee import mp_coffee_module
# from mini_program.chatgpt import mp_chatgpt_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
# CORS(app, supports_credentials=True)
# app.register_blueprint(auth_module)
# app.register_blueprint(cache_module)
# app.register_blueprint(mp_emoji_module)
# app.register_blueprint(mp_coffee_module)
# app.register_blueprint(mp_chatgpt_module)


@app.route('/api/v1', methods=['HEAD'])
def v1_head():
    return jsonify({'code': 0, 'data': {}, 'msg': 'test'})
    
@app.route('/api/v1', methods=['GET'])
def v1_get():
    api_info = """
    <h2>host:</h2>
    <p>http://welostyou.host<p/>

    <br/>
    <h2>cache:</h2>
    <p><b>/api/v1/cache/get/aaa</b></p>
    <p>GET (Auth)<p/>
    <br/>
    <p><b>/api/v1/cache/set</b></p>
    <p>POST (Auth)<p/>
    <div>{"aaa":"123"}</div>

    <br/>
    <h2>chatgpt:</h2>
    <p><b>/api/v1/mp/chatgpt/appsecret</b></p>
    <p>GET (Auth)<p/>
    <br/>
    <p><b>/api/v1/mp/chatgpt/used/list?page=1&page_size=20&order_by=create_at&order=ASC</b></p>
    <p>GET (Auth)<p/>
    <br/>
    <p><b>/api/v1/mp/chatgpt/used</b></p>
    <p>POST (Auth)<p/>
    <div>{"openid":"1", "nickname":"2", "data": "3"}</div>

    <br/>
    <h2>emoji:</h2>
    <p><b>/api/v1/mp/emoji/list</b></p>
    <p>GET (Auth)<p/>
    <br/>
    <p><b>/api/v1/mp/emoji/source/:name</b></p>
    <p>GET (Auth)<p/>


    <div style="display:flex;flex-direction:row;">
    </div>
    
    """
    return api_info

if __name__ == '__main__':
    # logger.info("Server Start")

    # 调试
    app.run(host='0.0.0.0', port=2000, debug=True, threaded=True)

    # 生产
    # server = pywsgi.WSGIServer(('0.0.0.0', 2000), app)
    # server.serve_forever()
