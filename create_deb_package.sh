#!/bin/sh

mkdir x-tile_pkg
cd x-tile_pkg
mkdir DEBIAN
mkdir usr
mkdir usr/bin
mkdir -p usr/lib/bonobo/servers
mkdir usr/share
mkdir usr/share/applications
mkdir usr/share/locale
mkdir usr/share/pixmaps
mkdir usr/share/x-tile
mkdir usr/share/x-tile/glade
mkdir usr/share/x-tile/modules

cp ../deb/control DEBIAN/
cp ../deb/postinst DEBIAN/

cp ../x-tile usr/bin/

cp ../linux/x-tile.server usr/lib/bonobo/servers/

cp ../linux/x-tile.desktop usr/share/applications/

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
dpkg -b x-tile_pkg
rm -r x-tile_pkg
