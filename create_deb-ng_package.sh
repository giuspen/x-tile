#!/bin/sh

mkdir x-tile-ng_pkg
cd x-tile-ng_pkg
mkdir DEBIAN
mkdir usr
mkdir usr/bin
mkdir usr/share
mkdir usr/share/applications
mkdir usr/share/locale
mkdir usr/share/pixmaps
mkdir usr/share/x-tile
mkdir usr/share/x-tile/glade
mkdir usr/share/x-tile/modules

cp ../deb-ng/control DEBIAN/

cp ../x-tile-ng usr/bin/

cp ../linux/x-tile-ng.desktop usr/share/applications/

cd ../locale
python i18n_po_to_mo.py
cd -
for dirname in ../locale/*
do
   if [ -d $dirname ]
   then
      cp -r $dirname usr/share/locale/
   fi
done

cp ../linux/x-tile.svg usr/share/pixmaps/

for filename in ../glade/*.*
do
   cp $filename usr/share/x-tile/glade/
done

for filename in ../modules/*.py
do
   cp $filename usr/share/x-tile/modules/
done

cd ..
dpkg -b x-tile-ng_pkg
rm -r x-tile-ng_pkg
