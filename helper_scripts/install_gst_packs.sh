#!/bin/sh

FOLDER="$(cd $(dirname $0); pwd)"

for pack in `cat $FOLDER/gst-packs.txt`
do
    pack_name=`echo $pack | sed "s/http:\/\/.*\/\(.*\)\.tar\.gz$/\1/"`
    tar_gz=`echo $pack | sed "s/http:\/\/.*\/\(.*\.tar\.gz\)$/\1/"`
    wget -O /tmp/$tar_gz $pack
    tar -zxvf /tmp/$tar_gz -C /tmp
    cd /tmp/$pack_name
    if [ `pwd | grep pygtk` ]
    then
        PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH" PYTHON=python2.4 ./configure ;make; make install
    else
        PYTHON=python2.4 ./configure ;make; make install
    fi
    cd -
done

cp -Rf /usr/lib/python2.4/site-packages/gtk-2.0/* /usr/local/lib/python2.4/site-packages
ldconfig

wget -O /tmp/gst-python.tar-gz http://gstreamer.freedesktop.org/src/gst-python/gst-python-0.10.18.tar.gz
tar -zxvf /tmp/gst-python.tar.gz -C /tmp
cd /tmp/gst-python-0.10.18
PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH" PYTHON=python2.4 ./configure ;make; make install
cd -
ldconfig
