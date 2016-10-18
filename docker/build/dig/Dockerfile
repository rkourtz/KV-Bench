FROM	alpine:latest

RUN apk update
RUN apk add curl tar gzip
RUN curl -L https://github.com/sequenceiq/docker-alpine-dig/releases/download/v9.10.2/dig.tgz|tar -xzv -C /usr/local/bin/

ENTRYPOINT ["/usr/local/bin/dig"]
CMD "-h"
