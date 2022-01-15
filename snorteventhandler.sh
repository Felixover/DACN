#!/bin/bash



log="/var/log/snort/alert_fast.txt"
blockedIPs="/usr/local/etc/snort/list/blockedIPs.txt"

inotifywait -q -m -e modify $log |
while read -r path; do
    atkIP="$(tail -1 $log | egrep -o '(([0-9]{1,3}\.){3}[0-9]{1,3})' | grep -v '192.168')"

    isexisted=""
    isexisted="$(grep -m 1 -o $atkIP $blockedIPs)"
    if [ "$isexisted" = "" ]; then
	# Iptables API source: https://github.com/Oxalide/iptables-api
        curl -i -X PUT "http://firewall.binary.local:8080/rules/DROP/FORWARD/all/*/*/0.0.0.0_0/$atkIP/"
        curl -i -X PUT "http://firewall.binary.local:8080/rules/DROP/FORWARD/all/*/*/$atkIP/0.0.0.0_0/"

        echo $atkIP >> $blockedIPs
    fi
done
