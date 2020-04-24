echo 'Restarting siteparse3 service ...'
bash ./stop.sh >/dev/null
bash ./start.sh >/dev/null
echo 'Restarted siteparse3 service'
