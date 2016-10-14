#!/bin/bash
set -e 
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# SETUP DEVELOPMENT ENVIRONMENT
# python
if [ ! -d "$DIR/python" ];
then
  cd $DIR
  virtualenv python
  source $PWD/python/bin/activate
  pip install -r requirements.txt
else
  source $PWD/python/bin/activate
fi

which vagrant &>/dev/null || echo "You must install vagrant (www.vagrantup.com) to continue" || exit 1
vagrant plugin list | grep vagrant-alpine &> /dev/null || vagrant plugin install vagrant-alpine

if [ "$1" == "--debug" ];
then
	DEBUG=$1
	shift
fi 
PLATFORM=$1
if [ "${#PLATFORM}" -eq 0 ];
then
  echo "You must choose a KV store. Choices:"
  for kv in `find -H $DIR -type f -name Vagrantfile`;
  do
    basename `dirname ${kv}`
  done
  exit 1
fi
cd $DIR/$PLATFORM
vagrant up

python $DIR/benchmark.py $DEBUG $PLATFORM

vagrant destroy --force

