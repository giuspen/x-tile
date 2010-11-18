#!/bin/sh

cd ..

intltool-extract --type=gettext/glade glade/x-tile.glade

xgettext --language=Python --keyword=_ --keyword=N_ --output=locale/x-tile.pot x-tile modules/tilings.py modules/core.py modules/cons.py glade/x-tile.glade.h
