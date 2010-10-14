#!/bin/sh

FOLDER="$(cd $(dirname $0); pwd)"

cd $FOLDER/../biblioteca_digital/

python2.4 $FOLDER/../biblioteca_digital/bootstrap.py
$FOLDER/../biblioteca_digital/bin/buildout -v
