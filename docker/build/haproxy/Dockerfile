FROM	consulagent:latest

ENV CONSUL_ADDRESS ""
ENV SERVICE default

EXPOSE 1936
EXPOSE 10000-10010

RUN apt-get -y install haproxy
RUN apt-get -y clean

ADD init.sh /init.sh
ADD haproxy_template.ctmpl /templates/haproxy.cfg.ctmpl
ADD haproxy.sh /haproxy.sh

CMD /init.sh
