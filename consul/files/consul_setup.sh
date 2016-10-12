#!/bin/bash
if [ ! -f '/usr/local/bin/consul' ];
then
	cd /usr/local/bin
	unzip /home/vagrant/consul.zip
	for dir in /etc/consul /opt/consul /run/consul;
	do 
		mkdir -p $dir
		chown vagrant:vagrant $dir
	done
fi
