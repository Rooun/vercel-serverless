import jwt
import time

JWT_KEY= 'root@zhaojiakun.com&&looham.com:/home'

def get_token(username):
    global JWT_KEY
    token_data = {
        'username': username,
        'brower_version': request.user_agent.browser + request.user_agent.version,
        'datetime': str(time.strftime("%Y-%m-%d"))
    }
    token = jwt.encode(token_data, JWT_KEY, algorithm='HS256')
    token = str(token, encoding = "utf-8")
    return token

