import argparse
import docker
import json
import re
import subprocess
import sys
from terminaltables import AsciiTable


class main(object):

    def __init__(self):
        self.config_file = "config.json"
        self.clients = []
        try:
            with open(self.config_file) as fh:
                cfg = json.load(fh)
                self.docker_addresses = cfg['docker_addresses']
                self.consul_addresses = cfg['consul_addresses']
        except IOError as e:
            print "Can't open config file %s. Did you run start.py?" % self.config_file
            raise

        for ipaddress in self.docker_addresses:
            self.clients.append(
                docker.Client(base_url="tcp://%s:2375" % ipaddress))

    def containers(self, all=False):
        containers = []
        for client in self.clients:
            containers = containers + client.containers(all=all)
        return containers

    def ls(self, args = None):
        print args
        containers = {}
        for container in cls.containers(all=True):
            for name in container['Names']:
                sanitized_name = name.strip("/")
                containers[sanitized_name] = {"ip": container["NetworkSettings"][
                    "Networks"]["bridge"]["IPAddress"], "ports": [], "host_ip": ""}
                for port in container['Ports']:
                    if "PublicPort" in port.keys():
                        containers[sanitized_name]['ports'].append(
                            str(port['PublicPort']))
                        containers[sanitized_name]['host_ip'] = port['IP']
        table_data = [["ContainerName", "ContainerIp", "HostIp", "HostFwdPorts"]]
        for name in sorted(containers.keys()):
            if args == None or args.regex == None or re.match(args.regex, name):  
                if args == None or not args.quiet:
                    table_data.append([name, containers[name]['ip'], containers[name]['host_ip'], ", ".join(sorted(containers[name]['ports']))])
                else:
                    print name
        if args == None or not args.quiet:
            print AsciiTable(table_data).table

    def start_service_container(self, serviceid, image="consulagent:latest", command=None):
        if not isinstance(serviceid, int):
            raise AttributeError(
                "serviceid should be in integer, not \"%s\"" % serviceid)
        services = {}
        if serviceid not in services:
            services[serviceid] = []
        for container in self.containers(all=True):
            for name in container['Names']:
                if "service" in name:
                    this_service_id, containerid = map(
                        lambda x: int(x), name.replace("/service", "").split("-"))
                    if this_service_id not in services:
                        services[this_service_id] = []
                    services[this_service_id].append(containerid)
        least_loaded_client = self.clients[0]
        for client in self.clients:
            if len(client.containers(all=True)) < len(least_loaded_client.containers(all=True)):
                least_loaded_client = client
        if len(services[serviceid]) == 0:
            container_id = 0
        else:
            container_id = max(services[serviceid]) + 1
        container_name = "service%i-%i" % (serviceid, container_id)
        service_base_port = 20000 + serviceid * 100 + container_id
        host_ip = least_loaded_client.base_url.split(":")[1].strip("//")
        host_port_dict = {80: (host_ip, service_base_port)}
        host_config = least_loaded_client.create_host_config(
            port_bindings=host_port_dict)
        environment = {"CONSUL_ADDRESS": self.consul_addresses[0]}
        least_loaded_client.create_container(
            image=image, command=command, environment=environment, hostname=container_name, name=container_name, host_config=host_config)
        least_loaded_client.start(container_name)

    def remove_container(self, name):
        for client in self.clients:
            for container in client.containers(all=True):
                for myname in container['Names']:
                    if myname.strip("/") == name:
                        if container['State'] == "running":
                            try:
                                client.stop(myname)
                            except docker.errors.NotFound:
                                # what the fuck is this?
                                force = True
                            else:
                                force = False
                        client.remove_container(myname, force=force)

    def execute_command(self, command, sudo_user=None):
        if sudo_user != None:
            command = "sudo -n -u %s %s" % (sudo_user, command)
        p = subprocess.Popen(
            [command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        exit_code = p.returncode
        return (exit_code, stdout, stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Start, stop, list running containers')
    parser.add_argument(
        "--debug", dest="debug", action="store_true", help="Verbosity", default=False)
    subparsers = parser.add_subparsers(dest="action")
    list_parser = subparsers.add_parser('ls', help='List running containers')
    list_parser.add_argument('-q', '--quiet', dest="quiet", action="store_true", help="Output only the container names")
    list_parser.add_argument('regex', nargs='?', help="Only show hosts matching this regex [optional]")
    start_parser = subparsers.add_parser(
        'start', help='start containers of some service')
    start_parser.add_argument('services', nargs='+')
    remove_parser = subparsers.add_parser('remove', help='Remove Containers')
    remove_parser.add_argument('container_names', nargs='+')
    args = parser.parse_args()
    cls = main()
    if args.action == "start":
        for id in args.services:
            serviceid = int(id)
            cls.start_service_container(serviceid)
        cls.ls()
    elif args.action == "remove":
        for name in args.container_names:
            cls.remove_container(name)
    else:
        # ls
        cls.ls(args)
