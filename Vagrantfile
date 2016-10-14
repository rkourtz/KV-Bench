# -*- mode: ruby -*-
# vi: set ft=ruby :

$instance_name_prefix="docker"
$num_instances = 1

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"
  # config.vm.box_check_update = false

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  (0..$num_instances-1).each do |i|
    config.vm.define vm_name = "%s%d" % [$instance_name_prefix, i] do |config|
      config.vm.hostname = vm_name

      config.vm.provider "virtualbox" do |vb|
      #   # Display the VirtualBox GUI when booting the machine
      #   vb.gui = true
      #
      #   # Customize the amount of memory on the VM:
        vb.memory = "2048"
      end
      ip = "192.168.33.#{i+50}"
      config.vm.network :private_network, ip: ip
    end
  end 
  config.vm.provision "shell", inline: <<-SHELL
     apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
     echo deb https://apt.dockerproject.org/repo ubuntu-trusty main > /etc/apt/sources.list.d/docker.list
     apt-get update
     apt-get install linux-image-extra-$(uname -r) linux-image-extra-virtual
     apt-get install -y docker-engine
     usermod -aG docker vagrant
  SHELL
  config.vm.provision :file, :source => "files/etc/default/docker", :destination => "/tmp/docker"
  config.vm.provision "shell", inline: "mv /tmp/docker /etc/default/docker", privileged: true
  config.vm.provision "shell", inline: "service docker restart", privileged: true
  config.vm.provision "shell", inline: "/vagrant/docker/build_docker_images.sh"
end
