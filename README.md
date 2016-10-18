# KV store playground

#Setup
* Install (vagrant)[http://www.vagrantup.com]
* Clone this repo
* Build the environment
  * `./start.sh`
* Start some "services"
  * This will start 2x service "0" and 1x service 1
  `./service.sh start 0 0 1`
* See the running containers
  * `./service.sh ls`
  <pre>consul0:	172.17.0.2	0.0.0.0	8400, 8300, 8600, 8500
service0-0:	172.17.0.3	192.168.33.50	10000
service0-1:	172.17.0.4	192.168.33.50	10001
service1-0:	172.17.0.5	192.168.33.50	10100</pre>
* Make sure they can see each other
  * `curl http://192.168.33.50:10100`
<pre>I am service1-0 at 172.17.0.5
Service consul
    Node consul0 172.17.0.2
Service service0
    Node service0-0 172.17.0.3
    Node service0-1 172.17.0.4
Service service1
    Node service1-0 172.17.0.5</pre>
