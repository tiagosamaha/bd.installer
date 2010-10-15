#!/bin/sh

FOLDER="$(cd $(dirname $0); pwd)"

wget -O /tmp/ez_setup.py http://peak.telecommunity.com/dist/ez_setup.py
python2.4 /tmp/ez_setup.py
easy_install-2.4 pip
pip install http://pascal.iff.edu.br/pypi/PIL-1.1.6.tar.gz
pip install extractor

cd $FOLDER/../biblioteca_digital/

python2.4 $FOLDER/../biblioteca_digital/bootstrap.py
$FOLDER/../biblioteca_digital/bin/buildout -v
