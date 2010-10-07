#!/bin/sh

FOLDER="$(cd $(dirname $0); pwd)"

for pack in `cat $FOLDER/apt-packs.txt`
do
    apt-get -y --force-yes install $pack
done
