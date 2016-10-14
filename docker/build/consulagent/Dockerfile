FROM	ubuntu:14.04

ENV CONSUL_ADDRESS ""
ENV SERVICE default

EXPOSE 80

RUN apt-get -y update && apt-get -y install curl unzip nginx
RUN curl -o /tmp/consul.zip https://releases.hashicorp.com/consul/0.7.0/consul_0.7.0_linux_amd64.zip
RUN curl -o /tmp/consul-template.zip https://releases.hashicorp.com/consul-template/0.16.0/consul-template_0.16.0_linux_amd64.zip
RUN unzip -o -d /usr/local/bin /tmp/consul.zip
RUN unzip -o -d /usr/local/bin /tmp/consul-template.zip

ADD consul_init.sh /consul_init.sh
ADD init.sh /init.sh

RUN rm -rf /tmp/*
RUN apt-get -y remove curl unzip
RUN apt-get -y clean

ADD nginx_template.ctmpl /usr/share/nginx/html/index.html.ctmpl

CMD /init.sh
