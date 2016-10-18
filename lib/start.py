import consul
import docker
import json
import os
import subprocess
import sys
import time

class main(object):

    def __init__(self):
        self.clients = []
        self.consul_addresses = []
        self.docker_addresses = sys.argv[1:]
        self.haproxy_addresses = []
        for ipaddress in sys.argv[1:]:
            self.clients.append(
                docker.Client(base_url="tcp://%s:2375" % ipaddress))
        self.start_consul()
        time.sleep(20) # give consul a bit to start up
        self.start_haproxy()
                
        config = {"docker_addresses": sys.argv[1:], 
                  "consul_addresses": self.consul_addresses,
                  "haproxy_addresses": self.haproxy_addresses}
        with open("config.json", "w") as fh:
            fh.write(json.dumps(config, indent=2))
        # prime the kv store
        ipaddress =self.docker_addresses[0]
        client = consul.Consul(host=ipaddress, port=8500)
        kv_start = {
            "env/foo": "/bar",
            "service/haproxy/maxconn": 10
            }
        for key in kv_start.keys():
            client.kv.put(key=key, value=str(kv_start[key])) # values must be strings
        self.print_status()
        
    def print_status(self):
        print "Consul addresses (Internal to Docker):"
        for idx, address in enumerate(self.consul_addresses):
            print "  - consul%i: %s" %(idx, address)
        print "HAProxy addresses (Internal to Docker):"
        for idx, address in enumerate(self.haproxy_addresses):
            print "  - haproxy%i: %s" %(idx, address)
        print "Web ui (accessible from your machine):"
        print "  - http://%s:8500/ui/" % self.docker_addresses[0]
    
    def start_consul(self):
        for idx, client in enumerate(self.clients):
            consul_running = False
            consul_name = "consul%i" % idx
            existing_containers = client.containers(all=True)
            for container in existing_containers:
                if "/%s" % consul_name in container["Names"]:
                    if container["State"] == "running":
                        consul_running = True
                        ipaddress = client.inspect_container(
                            consul_name)["NetworkSettings"]["Networks"]["bridge"]["IPAddress"]
                        self.consul_addresses.append(ipaddress)
                    else:
                        client.remove_container(consul_name)
            if not consul_running:
                client.pull("consul", "latest")
                consul_ports = [8300, 8400, 8500, 8600]
                host_port_dict = {}
                host_ip = client.base_url.split(":")[1].strip("//")
                for port in consul_ports:
                    host_port_dict[port] = (host_ip, port)
                if len(self.consul_addresses) == 0:
                    command = "agent -ui -server -bind 0.0.0.0 -bootstrap-expect=%i -client 0.0.0.0" % len(
                        self.clients)
                else:
                    command_args = [
                        "agent -ui -server -bind 0.0.0.0 -client 0.0.0.0"]
                    for address in self.consul_addresses:
                        command_args.append("--retry-join %s" % address)
                    command = " ".join(command_args)
                print "Creating %s" % consul_name
                container = client.create_container(
                    image="consul", command=command, hostname=consul_name, name=consul_name, host_config=client.create_host_config(port_bindings=host_port_dict))
                client.start(consul_name)
                ipaddress = client.inspect_container(
                    consul_name)["NetworkSettings"]["Networks"]["bridge"]["IPAddress"]
                if ipaddress not in self.consul_addresses:
                    self.consul_addresses.append(ipaddress)

    def start_haproxy(self):
        for idx, client in enumerate(self.clients):
            haproxy_running = False
            haproxy_name = "haproxy%i" % idx
            existing_containers = client.containers(all=True)
            for container in existing_containers:
                if "/%s" % haproxy_name in container["Names"]:
                    if container["State"] == "running":
                        haproxy_running = True
                        ipaddress = client.inspect_container(
                            haproxy_name)["NetworkSettings"]["Networks"]["bridge"]["IPAddress"]
                        self.haproxy_addresses.append(ipaddress)
                    else:
                        client.remove_container(haproxy_name)
            if not haproxy_running:
                 
                host_port_dict = {}
                host_ip = client.base_url.split(":")[1].strip("//")
                for port in [1936] + range(10000, 10010):
                    host_port_dict[port] = (host_ip, port)
                print "Creating %s" % haproxy_name
                command = None
                environment = {"CONSUL_ADDRESS": self.consul_addresses[0]}
                container = client.create_container(
                    image="haproxy", command=command, environment=environment, hostname=haproxy_name, name=haproxy_name, host_config=client.create_host_config(port_bindings=host_port_dict))
                client.start(haproxy_name)
                ipaddress = client.inspect_container(
                    haproxy_name)["NetworkSettings"]["Networks"]["bridge"]["IPAddress"]
                if ipaddress not in self.haproxy_addresses:
                    self.haproxy_addresses.append(ipaddress)
                
    def execute_command(self, command, sudo_user=None):
        if sudo_user != None:
            command = "sudo -n -u %s %s" % (sudo_user, command)
        p = subprocess.Popen(
            [command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        exit_code = p.returncode
        return (exit_code, stdout, stderr)

if __name__ == "__main__":
    if len(sys.argv[1:]) == 0:
        print "You must pass as parameters a list of the docker host addresses."
        print "Example: %s 192.168.33.50 192.168.33.51" % sys.argv[0]
        shell_wrapper = "%s.sh" % ".".join(os.path.basename(sys.argv[0]).split(".")[:-1]) 
        print "You probably don't want to run this file directly- use the shell wrapper %s" % shell_wrapper
        sys.exit(1)
    main()
