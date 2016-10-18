# KV store playground

# Overview
* This is a collection of semi-random scripts pertaining to service discovery. 
* The scripts in the root of the repo create a Vagrant hypervisor layer and allow the user to run fake "services" in containers. They self assemble using consul as a KV store and add themselves to haproxy pools for traffic routing. 
* Because we are also using consul services can find each other using consul's DNS interface

# Notes
* Each of the services is a simple nginx server on port 80. They all connect to the consul server (the consul address is passed in as an environment variable) and dump to index.html what they percieve the landscape is.
* Each service has its port 80 forwarded to a port on the vagrant box which is addressable using the vagrant box's private IP (192.168.33.50 by default) 
  * Services are assigned a unique forwarded port from the host they are running on using the following algorithm:
    * 20000 + (service_number * 100) + instance_number
    * Examples: 
      * service0-0 will have the port number 20000 
      * service9-6 will have the port number 20906
  * HAproxy pools us a similar algorithm:
     * 10000 + service_number
  * Using `./service.sh ls` you can see these mappings
    * `curl http://192.168.33.50:20101` will show you the output of service1-1's webserver
    * `curl http://192.168.33.50:10001` will round robin over all of service 1's active webservers
    
#Setup
* Install [vagrant](http://www.vagrantup.com)
* Clone this repo
* Build the environment
  * `./start.sh`
  * This gives you a consul container (consul0) and a haproxy container (haproxy0) running.
  * Haproxy is constantly monitoring consul for changes to add to its pools.
* Start some "services"
  * This will start 3x service "0"
    * `./service.sh start 0 0 0`
* See the running containers
  * `./service.sh ls`
  <pre>+---------------+-------------+---------------+----------------------------------------------------------------------------+
| ContainerName | ContainerIp | HostIp        | HostFwdPorts                                                               |
+---------------+-------------+---------------+----------------------------------------------------------------------------+
| consul0       | 172.17.0.2  | 192.168.33.50 | 8300, 8400, 8500, 8600, 8600                                               |
| haproxy0      | 172.17.0.3  | 192.168.33.50 | 10000, 10001, 10002, 10003, 10004, 10005, 10006, 10007, 10008, 10009, 1936 |
| service0-0    | 172.17.0.4  | 192.168.33.50 | 20000                                                                      |
| service0-1    | 172.17.0.5  | 192.168.33.50 | 20001                                                                      |
| service0-2    | 172.17.0.6  | 192.168.33.50 | 20002                                                                      |
+---------------+-------------+---------------+----------------------------------------------------------------------------+</pre>
* Verify that service0 can see the others
  * `curl http://192.168.33.50:20000`
<pre>
I am service0-0 at 172.17.0.4
Service consul
  Node consul0 172.17.0.2
Service haproxy0
  Node haproxy0 172.17.0.3
Service service0
  Node service0-0 172.17.0.4
  Node service0-1 172.17.0.5
  Node service0-2 172.17.0.6


ENVIRONMENT VARIABLES

  foo /bar
</pre>
* Make sure the haproxy pool is operating correctly
  * `curl http://192.168.33.50:10000`
  <pre>
I am service0-1 at 172.17.0.5
Service consul
  Node consul0 172.17.0.2
Service haproxy0
  Node haproxy0 172.17.0.3
Service service0
  Node service0-0 172.17.0.4
  Node service0-1 172.17.0.5
  Node service0-2 172.17.0.6


ENVIRONMENT VARIABLES

  foo /bar
</pre>
* Add another service0 and 2 containers of a new service 1
  * `./service.sh start 0 1 1`
* Verify the new containers show up in haproxy
  * Using a web browser go to `http://192.168.33.50:1936/`
  * `curl http://192.168.33.50:10001`
  
## Other actions
* To test other KV stores
  * `cd sandbox`
  * `./benchmark.sh etcd`
  or
  * `./benchmark.sh consul`

