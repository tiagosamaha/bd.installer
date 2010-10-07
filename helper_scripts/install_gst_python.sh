#!/bin/sh

FOLDER="$(cd $(dirname $0); pwd)"

for pack in `cat $FOLDER/gst-packs.txt`
do
    wget /tmp/$pack
done
