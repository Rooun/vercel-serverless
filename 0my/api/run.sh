process=`ps aux | grep 'python3 server.py' | grep -v grep`;
if [ "$process" == "" ];then
    echo not running
    nohup python3 server.py > server.log 2>&1 &
else
    echo running
fi

tail -F server.log
