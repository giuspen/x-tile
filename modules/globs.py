# -*- coding: UTF-8 -*-
#
#      globs.py
#
#      Copyright 2009-2011
#      Giuseppe Penone <giuspen@gmail.com>,
#      Chris Camacho (chris_c) <chris_camacho@yahoo.com>.
#
#      plus many thanks to  http://tronche.com/gui/x/xlib/
#                      and  http://tripie.sweb.cz/utils/wmctrl/
#
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation; either version 2 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program; if not, write to the Free Software
#      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#      MA 02110-1301, USA.

import gtk
import ctypes, ctypes.util
import cons, support, core


class XSizeHints(ctypes.Structure):
    """ XSizeHints structure (xlib) """
    _fields_ = [("flags",ctypes.c_long),
                ("x",ctypes.c_int),        # Obsolete
                ("y",ctypes.c_int),        # Obsolete
                ("width",ctypes.c_int),    # Obsolete
                ("height",ctypes.c_int),   # Obsolete
                ("min_width",ctypes.c_int),
                ("min_height",ctypes.c_int),
                ("max_width",ctypes.c_int),
                ("max_height",ctypes.c_int),
                ("width_inc",ctypes.c_int),
                ("height_inc",ctypes.c_int),
                ("min_asp_width",ctypes.c_int),
                ("min_asp_height",ctypes.c_int),
                ("max_asp_width",ctypes.c_int),
                ("max_asp_height",ctypes.c_int),
                ("base_width",ctypes.c_int),
                ("base_height",ctypes.c_int),
                ("win_gravity",ctypes.c_int)]

class XWindowAttributes(ctypes.Structure):
    """ XWindowAttributes structure (xlib) """
    _fields_ = [  ("x",                      ctypes.c_int32),
                  ("y",                      ctypes.c_int32),
                  ("width",                  ctypes.c_int32),
                  ("height",                 ctypes.c_int32),
                  ("border_width",           ctypes.c_int32),
                  ("depth",                  ctypes.c_int32),
                  ("visual",                 ctypes.c_ulong),
                  ("root",                   ctypes.c_ulong),
                  ("class",                  ctypes.c_int32),
                  ("bit_gravity",            ctypes.c_int32),
                  ("win_gravity",            ctypes.c_int32),
                  ("backing_store",          ctypes.c_int32),
                  ("backing_planes",         ctypes.c_ulong),
                  ("backing_pixel",          ctypes.c_ulong),
                  ("save_under",             ctypes.c_int32),
                  ("colourmap",              ctypes.c_ulong),
                  ("mapinstalled",           ctypes.c_uint32),
                  ("map_state",              ctypes.c_uint32),
                  ("all_event_masks",        ctypes.c_ulong),
                  ("your_event_mask",        ctypes.c_ulong),
                  ("do_not_propagate_mask",  ctypes.c_ulong),
                  ("override_redirect",      ctypes.c_int32),
                  ("screen",                 ctypes.c_ulong) ]

class XClientMessageEvent(ctypes.Structure):
    """ XClientMessageEvent structure (xlib) """
    _fields_ = [("type", ctypes.c_int),
                ("serial", ctypes.c_long),
                ("send", ctypes.c_byte),
                ("display",ctypes.c_long),
                ("window",ctypes.c_long),
                ("msgtype",ctypes.c_long),
                ("format",ctypes.c_int),
                ("data0",ctypes.c_long),
                ("data1",ctypes.c_long),
                ("data2",ctypes.c_long),
                ("data3",ctypes.c_long),
                ("data4",ctypes.c_long)]


class GlobalsObject(object):
    """Global Variables"""

    def __init__(self):
        """Instantiate global vars"""
        support.glob = self
        # x11 reference to xlib library display and root window globals
        self.x11 = ctypes.CDLL(ctypes.util.find_library("X11"))
        self.disp = self.x11.XOpenDisplay(0)
        self.root = self.x11.XDefaultRootWindow(self.disp)
        # property atoms for moveresize
        # assigned once here so they are not recreated
        # every time moveresize is called
        self.fscreen_atom = self.x11.XInternAtom(self.disp, "_NET_WM_STATE_FULLSCREEN", False)
        self.maxv_atom = self.x11.XInternAtom(self.disp, "_NET_WM_STATE_MAXIMIZED_VERT", False)
        self.maxh_atom = self.x11.XInternAtom(self.disp, "_NET_WM_STATE_MAXIMIZED_HORZ", False)
        self.hidden_atom = self.x11.XInternAtom(self.disp, "_NET_WM_STATE_HIDDEN", False)
        self.sticky_atom = self.x11.XInternAtom(self.disp, "_NET_WM_STATE_STICKY", False)
        self.str_atom = self.x11.XInternAtom(self.disp, "UTF8_STRING", False)
        # GLOBAL returns for getwindowproperty
        self.ret_type = ctypes.c_long()
        self.ret_format = ctypes.c_long()
        self.num_items = ctypes.c_long()
        self.bytes_after = ctypes.c_long()
        self.ret_pointer = ctypes.pointer(ctypes.c_long())
        # xlib global "defines" for some standard atoms
        self.XA_CARDINAL = 6
        self.XA_WINDOW = 33
        self.XA_ATOM = 4
        # GLOBAL size hints return
        self.size_hints_return = XSizeHints()
        self.screen_index = support.get_root_screen_index()
        self.str2_atom = self.x11.XInternAtom(self.disp, "STRING", False)
        self.num_monitors = gtk.gdk.screen_get_default().get_n_monitors()

    def read_monitors_areas(self):
        """Read Monitor(s) Area(s)"""
        strut_windows = support.enumerate_strut_windows(self.disp, self.root)
        screen = gtk.gdk.screen_get_default()
        self.num_monitors = screen.get_n_monitors()
        self.monitors_areas = []
        drawing_area_size = [0, 0]
        for num_monitor in range(self.num_monitors):
            rect = screen.get_monitor_geometry(num_monitor)
            self.monitors_areas.append([rect.x, rect.y, rect.width, rect.height])
            if rect.x + rect.width > drawing_area_size[0]: drawing_area_size[0] = rect.x + rect.width
            if rect.y + rect.height > drawing_area_size[1]: drawing_area_size[1] = rect.y + rect.height
            for strut_win in strut_windows:
                self.monitors_areas[-1] = support.subtract_areas(self.monitors_areas[-1], strut_win)
        self.drawing_rect = gtk.gdk.Rectangle(0, 0, drawing_area_size[0]/cons.DRAW_SCALE, drawing_area_size[1]/cons.DRAW_SCALE)
