#!/bin/sh

FOLDER="$(cd $(dirname $0); pwd)"

for pack in `cat $FOLDER/apt-packs.txt`
do
    PYTHON=python2.4 apt-get -y --force-yes install $pack
done
