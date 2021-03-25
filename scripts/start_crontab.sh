#/bin/bash

python3="/Users/wangjunhao/venv/siteparse3_env/bin/python3"
BASEDIR="$(dirname "$PWD")"
logfile="${BASEDIR}/logs"
cd $BASEDIR
nohup ${python3} -m scripts.crontabs.countHotWords > ${logfile}/count_hot_words_crontab.log  2>&1 &