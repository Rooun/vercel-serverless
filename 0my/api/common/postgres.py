import json
import psycopg2
from api.common.log import logger

POSTGRES_SERVER = ['welostyou.host', "30010"]

def connect():
    global POSTGRES_SERVER
    try:
        return psycopg2.connect(database="postgres", user="postgres", password="hello.954", host=POSTGRES_SERVER[0], port=POSTGRES_SERVER[1])
    except Exception as e:
        err = str(e)
        if "could not connect to server" in err:
            logger.error("Database connect fail: {}:{}".format(POSTGRES_SERVER[0], POSTGRES_SERVER[1]))
        else:
            logger.error("Database connect fail: {}".format(err))

        return ""

def exec(command):
    conn = connect()
    if (conn == ""): return
    cursor = conn.cursor()
    try:
        cursor.execute(command)
    
    except Exception as e:
        logger.error("ERROR CMD: " + command)
        return False
    
    conn.commit()
    cursor.close()
    conn.close()
    return True

def select_to_array(command):
    rows = []
    conn = connect()
    if (conn == ""): return
    cursor = conn.cursor()
    try:
        cursor.execute(command)
        rows = cursor.fetchall()
    
    except Exception as e:
        if ("does not exist" in str(e)):
            logger.error(str(e).splitlines()[0])
        else:
            logger.error(str(e))
    
    conn.commit()
    cursor.close()
    conn.close()
    return rows

def select_to_dict(command):
    jsonRows = []
    conn = connect()
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
            logger.error(str(e).splitlines()[0])
        else:
            logger.error(str(e))
    
    conn.commit()
    cursor.close()
    conn.close()
    return jsonRows

def insert(tablename, column, value):
    column = ','.join(column) if (list == type(column)) else column
    value = ','.join(value) if (list == type(value)) else value
    sqlcmd = "INSERT INTO {}({}) VALUES({})".format(tablename, column, value)
    return exec(sqlcmd)

