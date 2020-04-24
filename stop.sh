echo "Stopping siteparse3 ..."
PID=`ps -ef | grep "siteparse_main.py" | grep -v grep | awk '{print $2}'`
if [[ "" != "$PID" ]]; then
  echo "killing siteparse3"
  kill -9 $PID
fi
echo "siteparse service stoped"
