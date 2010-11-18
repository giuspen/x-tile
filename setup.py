#!/usr/bin/env python

# for linux install: "python setup.py install --prefix=/usr --exec-prefix=/usr -f"

# after the installation, run in the terminal "killall gnome-panel" in order to restart
# the gnome panel and see the changes with no need to reboot

from distutils.core import setup

import os, glob, sys, subprocess
import __builtin__
def _(transl_str):
   return transl_str
__builtin__._ = _
sys.path.append(os.path.join(os.getcwd(), "modules"))
import cons

data_files = [
                  ("lib/bonobo/servers", ["linux/x-tile.server"] ),
                  ("share/pixmaps", ["linux/x-tile.svg"] ),
                  ("share/applications", ["linux/x-tile.desktop"] ),
                  ("share/x-tile/glade", glob.glob("glade/*.*") ),
                  ("share/x-tile/modules", glob.glob("modules/*.py") )
               ]
for lang in cons.AVAILABLE_LANGS:
   if lang in ["default", "en"]: continue
   data_files.append( ("share/locale/%s/LC_MESSAGES" % lang, ["locale/%s/LC_MESSAGES/x-tile.mo" % lang] ) )

setup(
   name = "X Tile",
   description = "X Tile Gnome Applet",
   long_description = "A gnome applet for your panel (or optionally a standalone application) that allows you to select a number of windows and tile them in different ways",
   version = cons.VERSION,
   author = "Giuseppe Penone & Chris Camacho",
   author_email = "giuspen@gmail.com & chris_camacho@yahoo.com",
   url = "http://www.giuspen.com/x-tile/",
   license = "GPL",
   scripts = ["x-tile"],
   data_files = data_files
)
