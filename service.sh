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
cd $DIR
${REPODIR}/python/bin/python lib/service.py $@
