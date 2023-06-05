import os
import time
import logging

# '[ %(asctime)s ] %(levelname)s : %(funcName)s | %(message)s'
# '%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s'

log_path = os.path.join(os.getcwd(), 'logs')
formatter = logging.Formatter('%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s')
rq = time.strftime('%Y%m%d', time.localtime(time.time()))

if not os.path.exists(log_path):
    os.makedirs(log_path)

log_name = log_path + '/service-' + rq + '.log'

filehandler = logging.FileHandler(log_name, mode='a')
filehandler.setLevel(logging.INFO)
filehandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(filehandler)