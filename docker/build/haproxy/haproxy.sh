#!/bin/bash

[ -f /run/haproxy.pid ] && pkill -9 -F /run/haproxy.pid
/usr/sbin/haproxy -D -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid 
