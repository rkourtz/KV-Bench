#!/bin/bash
set -e
if [ -z "$CONSUL_ADDRESS" ];
then
	echo "ERROR: You must pass in an environment variable CONSUL_ADDRESS"
	exit 2
fi
service_name=`hostname | awk -F "-" '{print $1}'`
for dir in /etc/consul.d /var/run/consul /var/log/consul;
do
  if [ ! -d "${dir}" ];
  then
    mkdir ${dir}
  fi
done
echo "{\"service\": {\"name\": \"${service_name}\", \"tags\": [], \"port\": 80}}" > /etc/consul.d/service.json
consul agent -pid-file=/var/run/consul/agent.pid -retry-join=${CONSUL_ADDRESS} -config-dir=/etc/consul.d -data-dir=/tmp/consul -dc=${DATACENTER} -node=$(hostname) &> /var/log/consul/agent.log &

