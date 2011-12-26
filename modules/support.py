# -*- coding: UTF-8 -*-
#
#      support.py
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

import gtk, gobject
import os, subprocess, ctypes, re
import globs


def get_desktop_width_n_height():
    """Get the Curr Viewport Num Assuming Compiz is Running"""
    get_property("_NET_WORKAREA", glob.root, glob.XA_CARDINAL)
    return glob.ret_pointer[2], glob.ret_pointer[3]

def is_window_in_curr_viewport(desktop_width, desktop_height, win_id):
    """Get the Curr Viewport Num Assuming Compiz is Running"""
    x, y, width, height, root = get_geom(win_id)
    if x < 0 or x >= desktop_width or y < 0 or y >= desktop_height: return False
    else: return True

def get_geom(win):
    """
    Status XQueryTree(display, w, root_return, parent_return, children_return, nchildren_return)
       Display *display;
       Window w;
       Window *root_return;
       Window *parent_return;
       Window **children_return;
       unsigned int *nchildren_return;
    """
    root_return = ctypes.c_ulong()
    parent_return = ctypes.c_ulong()
    children_return = ctypes.c_ulong()
    nchildren_return = ctypes.c_uint()

    glob.x11.XQueryTree(glob.disp,win,ctypes.byref(root_return),ctypes.byref(parent_return),
       ctypes.byref(children_return),ctypes.byref(nchildren_return))

    # undecorated windows have root as parent...
    if (glob.root!=parent_return.value):
        win=parent_return

    xwa = globs.XWindowAttributes()
    glob.x11.XGetWindowAttributes(glob.disp, win,ctypes.byref(xwa))

    get_property("_NET_FRAME_EXTENTS",win,glob.XA_CARDINAL)
    if bool(glob.ret_pointer)==False:
        l,r,t,b = (0,0,0,0)
    else:
        l,r,t,b = glob.ret_pointer[0], glob.ret_pointer[1], glob.ret_pointer[2], glob.ret_pointer[3]

    return xwa.x-l,xwa.y-t,xwa.width+(l+r),xwa.height+(t+b),xwa.root

def get_property(prop_name, window, data_type):  #128*256 longs (128kb) should be good enough...
    """   gets an x property puts in global return variables
          property name, window, return data type atom   """
    prop_atom = glob.x11.XInternAtom(glob.disp, prop_name, False)
    glob.x11.XGetWindowProperty(glob.disp, window, prop_atom, 0, 128*256, False, data_type,
                           ctypes.byref(glob.ret_type), ctypes.byref(glob.ret_format), ctypes.byref(glob.num_items),
                           ctypes.byref(glob.bytes_after), ctypes.byref(glob.ret_pointer))

def get_icon(win):
    """   this returns a gtk.gdk.pixbuf of the windows icon
          converts argb into rgba in the process   """
    get_property("_NET_WM_ICON", win, glob.XA_CARDINAL)
    if not glob.ret_pointer : return None
    w = glob.ret_pointer[0]
    h = glob.ret_pointer[1]
    s = w*h
    buff = ""
    i = 0
    while i<s:
        argb = glob.ret_pointer[i+2]
        i += 1
        buff = buff + ("%c" % ((argb >> 16) & 0xff))
        buff = buff + ("%c" % ((argb >> 8) & 0xff))
        buff = buff + ("%c" % (argb & 0xff))
        buff = buff + ("%c" % ((argb >> 24) & 0xff))
    pxbuf = gtk.gdk.pixbuf_new_from_data(buff, gtk.gdk.COLORSPACE_RGB, True, 8, w, h, w*4)
    return pxbuf

def get_min_size(win):
    """ returns the minimum window size and its resize increment """
    supplied_return = ctypes.c_long(0)
    glob.x11.XGetWMNormalHints(glob.disp, win, ctypes.byref(glob.size_hints_return),
                               ctypes.byref(supplied_return))

def client_msg(win, msg, d0, d1, d2, d3, d4):
    """   sends a client message event used to change window properties   """
    event = globs.XClientMessageEvent()
    event.type = 33 #ClientMessage
    event.serial = 0
    event.send = True
    event.msgtype = glob.x11.XInternAtom(glob.disp, msg, False)
    event.window = win
    event.format = 32
    event.data0 = d0
    event.data1 = d1
    event.data2 = d2
    event.data3 = d3
    event.data4 = d4
    # mask is SubstructureRedirectMask | SubstructureNotifyMask (20&19)
    if not glob.x11.XSendEvent(glob.disp,glob.root,False, 1<<20 | 1<<19,ctypes.byref(event)):
        print "can't send message ", msg # DEBUG

def moveresize(win, x, y, w, h):
    """   moves window to the users current desktop removes states like
          maximised and fullscreen activates the window,
          raises it then finally! moves and resizes it """
    glob.x11.XSync(glob.disp, False)
    l,r,t,b=0,0,0,0
    get_property("_NET_FRAME_EXTENTS",win,glob.XA_CARDINAL)
    if bool(glob.ret_pointer)==False:
        l,r,t,b = (0,0,0,0)
    else:
        l,r,t,b = glob.ret_pointer[0], glob.ret_pointer[1], glob.ret_pointer[2], glob.ret_pointer[3]
    get_property("_NET_CURRENT_DESKTOP",glob.root,glob.XA_CARDINAL)
    cdt = glob.ret_pointer[0]
    client_msg(win, "_NET_WM_DESKTOP", cdt, 0, 0, 0, 0)
    client_msg(win,"_NET_WM_STATE",0,glob.fscreen_atom,0,0,0)
    client_msg(win,"_NET_WM_STATE",0,glob.maxv_atom,glob.maxh_atom,0,0)
    client_msg(win,"_NET_ACTIVE_WINDOW",0,0,0,0,0)
    glob.x11.XMapRaised(glob.disp,win)
    glob.x11.XSync(glob.disp, False)
    glob.x11.XMoveResizeWindow(glob.disp,win,x,y,w-(l+r),h-(t+b)) # only interior size needs deco subtracting not position
    glob.x11.XSync(glob.disp, False)

def maximize(win):
    """ moves a window to the current desktop and maximises it """
    get_property("_NET_CURRENT_DESKTOP",glob.root,glob.XA_CARDINAL)
    cdt = glob.ret_pointer[0]
    client_msg(win, "_NET_WM_DESKTOP", cdt, 0, 0, 0, 0)
    client_msg(win, "_NET_WM_STATE", 1, glob.maxv_atom, glob.maxh_atom, 0, 0) # 1 = add
    glob.x11.XSync(glob.disp, False)

def unmaximize(win):
    """ moves a window to the current desktop and 'unmaximises' it """
    get_property("_NET_CURRENT_DESKTOP", glob.root, glob.XA_CARDINAL)
    cdt = glob.ret_pointer[0]
    client_msg(win, "_NET_WM_DESKTOP", cdt, 0, 0, 0, 0)
    client_msg(win,"_NET_WM_STATE", 0, glob.maxv_atom, glob.maxh_atom, 0, 0) # 0 = remove
    glob.x11.XSync(glob.disp, False)

def desktop_size():
    """   gets the "work area" usually space between panels """
    get_property("_NET_WORKAREA", glob.root, glob.XA_CARDINAL)
    if glob.num_items.value:
        return glob.ret_pointer[0], glob.ret_pointer[1], glob.ret_pointer[2], glob.ret_pointer[3]
    return 0,0,0,0

def is_inside(p, pdim, a, adim):
    """Returns True if p <---> p+dim is between a <---> a+dim"""
    return ( (p+pdim/2 > a) and (p+pdim/2 < a+adim) )

def subtract_areas(white_area, black_area):
    """Returns the white_area without the black_area"""
    #print "white_area", white_area
    #print "black_area", black_area
    if not is_inside(black_area[0], black_area[2], white_area[0], white_area[2])\
    or not is_inside(black_area[1], black_area[3], white_area[1], white_area[3]):
        #print "not is_inside"
        return white_area
    # ignore the desktop strut
    if black_area[2] > white_area[2]/2 and black_area[3] > white_area[3]/2:
        #print "strut ignored"
        return white_area
    # we have to understand whether the panel is top, bottom, left or right
    if black_area[2] < black_area[3]:
        # width < height => this is a left or right panel
        if black_area[0] == white_area[0]:
            #print "left panel"
            white_area[0] += black_area[2]
            white_area[2] -= black_area[2]
        else:
            #print "right panel"
            white_area[2] -= black_area[2]
    else:
        # width > height => this is a top or bottom panel
        if black_area[1] == white_area[1]:
            #print "top panel"
            white_area[1] += black_area[3]
            white_area[3] -= black_area[3]
        else:
            #print "bottom panel"
            white_area[3] -= black_area[3]
    return white_area

def translate_coords(win, x, y):
    """
    Bool XTranslateCoordinates(display, src_w, dest_w, src_x, src_y, dest_x_return, 
                               dest_y_return, child_return)
      Display *display;
      Window src_w, dest_w;
      int src_x, src_y;
      int *dest_x_return, *dest_y_return;
      Window *child_return;
    """
    child_return = ctypes.c_ulong()
    dest_x_return = ctypes.c_int()
    dest_y_return = ctypes.c_int()
    glob.x11.XTranslateCoordinates(glob.disp, win, glob.root, x, y,
                                   ctypes.byref(dest_x_return),
                                   ctypes.byref(dest_y_return),
                                   ctypes.byref(child_return))
    return dest_x_return.value, dest_y_return.value

def enumerate_strut_windows(display, rootwindow):
    """Retrieve the Strut Windows (the panels)"""
    strut_windows = []
    rootr = ctypes.c_ulong()
    parent = ctypes.c_ulong()
    children = ctypes.pointer(ctypes.c_ulong())
    noOfChildren = ctypes.c_int()
    x_return = ctypes.c_int()
    y_return = ctypes.c_int()
    width_return = ctypes.c_int()
    height_return = ctypes.c_int()
    dummy = ctypes.c_int()
    get_property("_NET_WM_STRUT_PARTIAL", rootwindow, glob.XA_CARDINAL)
    if glob.num_items.value:
        glob.x11.XGetGeometry(display, rootwindow, ctypes.byref(dummy), ctypes.byref(x_return), ctypes.byref(y_return),
                              ctypes.byref(width_return), ctypes.byref(height_return), ctypes.byref(dummy), ctypes.byref(dummy) )
        struct_origin = translate_coords(rootwindow, x_return.value, y_return.value)
        strut_windows.append([struct_origin[0], struct_origin[1], width_return.value, height_return.value])
    status = glob.x11.XQueryTree(display, rootwindow, ctypes.byref(rootr), ctypes.byref(parent), ctypes.byref(children), ctypes.byref(noOfChildren) )
    if noOfChildren.value:
        for i in range(0, noOfChildren.value):
            ptr = ctypes.cast(children[i], ctypes.POINTER(ctypes.c_uint) )
            strut_windows.extend(enumerate_strut_windows(display, children[i]))
        glob.x11.XFree(children)
    return strut_windows

def get_root_screen_index():
    """Get Screen Index"""
    xwa = globs.XWindowAttributes()
    glob.x11.XGetWindowAttributes(glob.disp, glob.root,ctypes.byref(xwa))
    screen_index = glob.x11.XScreenNumberOfScreen(xwa.screen)
    return screen_index

def get_process_name(p):
    # determine executable
    # we were only using just this routine from psutils so I
    # "borrowed" ahem it....
    if p == 0: return "?"
    try:
        _exe = os.readlink("/proc/%s/exe" % p)
    except OSError:
        if not os.path.exists("/proc/%s/stat" % p): return "?"
        f = open("/proc/%s/stat" % p)
        try:
            _exe = f.read().split(' ')[1].replace('(', '').replace(')', '')
        finally:
            f.close()
    # determine name and path
    if os.path.isabs(_exe):
        path, name = os.path.split(_exe)
    else:
        path = ''
        name = _exe
    if name[0:6]=="python":
        f=open("/proc/%s/cmdline" % p)
        try:
            cmdp=f.read().split(chr(0))
        finally:
            f.close()
        name=cmdp[1]
    return name


# these could be replaced by one general purpose routine but make
# code eleswhere easier to read...

def is_window_hidden(win):
    """ is a window hidden ie "minimised" ? """
    get_property("_NET_WM_STATE", win, glob.XA_ATOM)
    for i in range(0, glob.num_items.value):
        if glob.ret_pointer[i] == glob.hidden_atom: return True
    return False

def is_window_sticky(win):
    """ is a window sticky ? """
    get_property("_NET_WM_STATE", win, glob.XA_ATOM)
    for i in range(0, glob.num_items.value):
        if glob.ret_pointer[i] == glob.sticky_atom: return True
    return False

def is_window_Vmax(win):
    """ is a window vertically maximised ? """
    get_property("_NET_WM_STATE", win, glob.XA_ATOM)
    for i in range(0, glob.num_items.value):
        if glob.ret_pointer[i] == glob.maxv_atom: return True
    return False

def is_window_Hmax(win):
    """ is a window horizontally maximised ? """
    get_property("_NET_WM_STATE", win, glob.XA_ATOM)
    for i in range(0, glob.num_items.value):
        if glob.ret_pointer[i] == glob.maxh_atom: return True
    return False

def dialog_info(message, parent=None):
    """The Info dialog"""
    dialog = gtk.MessageDialog(flags=gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                               type=gtk.MESSAGE_INFO,
                               buttons=gtk.BUTTONS_OK,
                               message_format=message)
    if parent != None: dialog.set_transient_for(parent)
    dialog.set_title(_("Info"))
    dialog.run()
    dialog.destroy()

def dialog_warning(message, parent=None):
    """The Warning dialog"""
    dialog = gtk.MessageDialog(flags=gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                               type=gtk.MESSAGE_WARNING,
                               buttons=gtk.BUTTONS_OK,
                               message_format=message)
    if parent != None: dialog.set_transient_for(parent)
    dialog.set_title(_("Warning"))
    dialog.run()
    dialog.destroy()
