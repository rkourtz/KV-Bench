import docker
import json
import subprocess
import sys


class main(object):

    def __init__(self):
        self.clients = []
        self.consul_addresses = []
        for ipaddress in sys.argv[1:]:
            self.clients.append(
                docker.Client(base_url="tcp://%s:2375" % ipaddress))
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
                        print "%s: %s" % (consul_name, ipaddress)
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
                print "%s: %s" % (consul_name, ipaddress)
                self.consul_addresses.append(ipaddress)
        config = {"docker_addresses": sys.argv[
            1:], "consul_addresses": self.consul_addresses}
        with open("config.json", "w") as fh:
            fh.write(json.dumps(config, indent=2))

    def execute_command(self, command, sudo_user=None):
        if sudo_user != None:
            command = "sudo -n -u %s %s" % (sudo_user, command)
        p = subprocess.Popen(
            [command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        exit_code = p.returncode
        return (exit_code, stdout, stderr)

if __name__ == "__main__":
    main()
