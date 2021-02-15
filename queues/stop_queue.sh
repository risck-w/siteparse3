#!/bin/bash
echo "Stopping crontabs..."
PID=`ps -ef | grep "queue.py"| grep -v grep | awk '{print $2}'`
if [[ "" !=  "$PID" ]]; then
  echo "killing $PID"
  kill -9 $PID
fi
echo "crontabs service stoped."