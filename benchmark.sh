#!/bin/bash
set -e 

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ ! -d "$DIR/python" ];
then
  cd $DIR
  virtualenv python
  pip install -r requirements.txt
fi

source $PWD/python/bin/activate

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

python $DIR/benchmark.py $PLATFORM

vagrant destroy

