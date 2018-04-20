#!/bin/bash
LOG=/opt/pmacct/logs/pmacct_process.log

logaction () {
        now=`date "+%Y/%m/%d %H:%M:%S"`
        echo "$now $1" >> $LOG
}

pid=`pgrep pmacctd | head -n1 | awk '{print $1;}'`

if [ -z "$pid" ]
then
	logaction "PMacct process was killed."
	/usr/local/sbin/pmacctd -f /etc/pmacct/cacti_pmacct.conf

	pid=`pgrep pmacctd | head -n1 | awk '{print $1;}'`
	logaction "Staring PMacct process again with PID = $pid."
fi
