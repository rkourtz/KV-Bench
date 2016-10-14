#!/bin/bash
set -e
# Always run this first
/consul_init.sh

# Add application specific stuff here
export IPADDRESS=`ifconfig eth0 | awk '/inet addr/{print substr($2,6)}'`
consul-template -consul ${CONSUL_ADDRESS}:8500 -template "/usr/share/nginx/html/index.html.ctmpl:/usr/share/nginx/html/index.html" &> /var/log/consul/template.log &
nginx

# Follow the logs in stdout
tail -f `find /var/log/ -type f`

