#/bin/bash

python3="/Users/wangjunhao/venv/siteparse3_env/bin/python3"
BASEDIR="$(dirname "$PWD")"
logfile="${BASEDIR}/logs"
nohup ${python3} ./crawler_queue.py > ${logfile}/crawler_queue.log  2>&1 &