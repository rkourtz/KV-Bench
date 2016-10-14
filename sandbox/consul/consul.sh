#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/etcd
vagrant up
vssh core0 "docker run -d --name consul0 consul agent -ui -server -bind 0.0.0.0 -bootstrap-expect=2 -client 0.0.0.0"
first_consul

