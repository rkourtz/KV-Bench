#!/bin/bash
set -e
# Always run this first
/consul_init.sh

# Add application specific stuff here
consul-template -consul ${CONSUL_ADDRESS}:8500 -template "/templates/haproxy.cfg.ctmpl:/etc/haproxy/haproxy.cfg:/haproxy.sh" > /var/log/consul/template.log &

# Follow the logs in stdout
tail -f `find /var/log/ -type f`

