#!/bin/bash
set -e 
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPODIR=${DIR}
# SETUP DEVELOPMENT ENVIRONMENT
# python
if [ ! -d "$REPODIR/python" ];
then
  cd $REPODIR
  virtualenv python
  source $PWD/python/bin/activate
  pip install -r requirements.txt
else
  source ${REPODIR}/python/bin/activate
fi

which vagrant &>/dev/null || echo "You must install vagrant (www.vagrantup.com) to continue" || exit 1
vagrant plugin list | grep vagrant-alpine &> /dev/null || vagrant plugin install vagrant-alpine

cd $DIR
vagrant up
${REPODIR}/python/bin/python lib/start.py 192.168.33.50
