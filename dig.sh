#!/bin/bash
ARGS=$@
vagrant ssh -c "docker run -t --rm dig $ARGS"
