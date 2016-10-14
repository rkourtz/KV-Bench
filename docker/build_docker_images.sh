#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BUILDDIR="$DIR/build"
IMAGEDIR="$DIR/images"
if [ "$1" == "--force" ];
then
	FORCE_BUILD=1
else
	FORCE_BUILD=0
fi

for image in `find $BUILDDIR -mindepth 1 -maxdepth 1 -type d -exec basename {} \;`
do
	imagefile="${IMAGEDIR}/${image}.tar"
  imagebuilddir="${BUILDDIR}/${image}"
	if [ $FORCE_BUILD -eq 1 ] || [ ! -f $imagefile ];
	then
		echo "Building: $image"
		cd $imagebuilddir
		docker build -t ${image}:latest .
		docker save ${image}:latest > $imagefile
	else
		echo "Loading: $image"
		docker load -i $imagefile
	fi
done

