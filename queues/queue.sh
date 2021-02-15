#/bin/bash

python3="/Users/wangjunhao/venv/siteparse3_env/bin/python3"
BASEDIR="$(dirname "$PWD")"
logfile="${BASEDIR}/logs"

echo 'Start wordSplit queue'
nohup ${python3} ./wordSplit_queue.py > ${logfile}/wordSplit_queue.log  2>&1 &

echo 'Start crawler queue'
nohup ${python3} ./crawler_queue.py > ${logfile}/crawler_queue.log  2>&1 &