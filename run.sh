#!/usr/bin/env bash

path=/home/pi/telegram
pid_file=$path/run.pid
pid=`cat $pid_file`
#echo "$path $pid_file $pid"

start()
{
	pid=`ps aux | grep 'record.py' | grep -v 'grep' | awk '{print $2}'`
	if [ -z "$pid" ]; then
		echo "start record ..."
		nohup /usr/bin/python3 $path/record.py > $path/nohup.log 2>&1 & echo $! > $path/run.pid
		new_pid=`cat $pid_file`
		echo "new pid: $new_pid."
	else
		echo "the record.py script is running ..."
	fi
}

stop()
{
	pid=`ps aux | grep 'record.py' | grep -v 'grep' | awk '{print $2}'`
	if [ -n "$pid" ]; then
		echo "try to kill $pid ..."
		kill $pid	
	else
		echo "seem like it is not running ..."
	fi
}

case $1 in
	start)
		#echo 'start'
		start
	;;

	stop)
		#echo 'stop'
		stop
	;;

	restart)
		#echo 'restart'
		stop
		sleep 2
		start
	;;

	*)
		echo "sorry, i can't understand what you mean, plase enter start, stop, restart"
	;;
esac
