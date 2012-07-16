# -*- coding: UTF-8 -*-
#
#      core.py
#
#      Copyright 2009-2012
#      Giuseppe Penone <giuspen@gmail.com>,
#      Chris Camacho (chris_c) <codifies@gmail.com>.
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

from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GConf
import os, sys, ctypes, webbrowser, time, subprocess
try:
    from gi.repository import AppIndicator3 as appindicator
    HAS_APPINDICATOR = True
except: HAS_APPINDICATOR = False
import cons, support, tilings


class InfoModel:
    """Holds the information"""

    def __init__(self):
        """Sets up and populates the Gtk.ListStore"""
        # 0:selected, 1:window ref, 2:title, 3:pixbuf of icon, 4:selected2, 5:cell_background
        self.gconf_client = GConf.Client.get_default()
        self.liststore = Gtk.ListStore(GObject.TYPE_BOOLEAN,
                                       GObject.TYPE_ULONG,
                                       GObject.TYPE_STRING,
                                       GObject.TYPE_PYOBJECT,
                                       GObject.TYPE_BOOLEAN,
                                       GObject.TYPE_STRING)
        self.process_picklist = set()
        self.process_blacklist = set()
        self.process_whitelist = set()

    def load_model(self, appletobj):
        """Populates the Gtk.ListStore"""
        self.liststore.clear()
        clients = []
        support.get_property("_NET_CLIENT_LIST", glob.root, glob.XA_WINDOW)
        for i in range(0, glob.num_items.value):
            clients.append(glob.ret_pointer[i])
        rows_num = 0
        support.get_property("_NET_CURRENT_DESKTOP", glob.root, glob.XA_CARDINAL)
        if bool(glob.ret_pointer) == False:
            curr_workspace_num = -2
            print "DEBUG warning _NET_CURRENT_DESKTOP improperly set"
        else: curr_workspace_num = glob.ret_pointer[0] # the number of the current workspace
        screen = Gdk.Screen.get_default()
        for client in clients:
            if support.is_window_sticky(client): continue
            support.get_property("_NET_WM_DESKTOP", client, glob.XA_CARDINAL)
            if bool(glob.ret_pointer): workspace_num = glob.ret_pointer[0]
            else:
                print "DEBUG warning _NET_WM_DESKTOP improperly set"
                workspace_num = curr_workspace_num
            if self.gconf_client.get_string(cons.GCONF_ONLY_CURR_DESK % glob.screen_index) == cons.STR_TRUE\
            and (workspace_num != curr_workspace_num or not support.is_window_in_curr_viewport(glob.desktop_width, glob.desktop_height, client)):
                continue
            if self.gconf_client.get_string(cons.GCONF_NOT_MINIMIZED % glob.screen_index) == cons.STR_TRUE\
            and support.is_window_hidden(client):
                continue
            support.get_property("_NET_WM_NAME", client, glob.str_atom)
            title="???"
            if bool(glob.ret_pointer)==False:
                print "DEBUG warning _NET_WM_NAME improperly set by application"
                support.get_property("WM_NAME", client, glob.str2_atom)
                if bool(glob.ret_pointer)==False:
                    print "DEBUG warning WM_NAME not set by application"
                else:
                    title = ctypes.string_at(glob.ret_pointer)
                    print "class "+title
            else: title = ctypes.string_at(glob.ret_pointer)
            if title in cons.WINNAMES_BLACKLIST: continue
            pxb = support.get_icon(client)
            if pxb: pxb = pxb.scale_simple(24, 24, GdkPixbuf.InterpType.BILINEAR)
            support.get_property("_NET_WM_PID", client, glob.XA_CARDINAL)
            pid=0
            process_name="UNKNOWN"
            if bool(glob.ret_pointer)==False:
                print "DEBUG warning can't get PID _NET_WM_PID failed"
            else:
                pid = glob.ret_pointer[0]
                process_name = support.get_process_name(pid)
            # filter based on process name - NB beppie I'd like something better for this but dont know what!
            if len(process_name) > 6 and process_name[-6:] == "x-tile": continue
            if process_name in cons.PROCESSES_BLACKLIST: continue
            #print "win", pid, process_name
            #if pid > 0:
                #ppid = os.popen("ps -p %d -oppid=" % pid).read().strip()
                #pp_name = support.get_process_name(ppid)
                #print "pwin", ppid, pp_name
                #if pp_name in cons.PROCESSES_PARENT_BLACKLIST: continue
            if support.is_candidate_compiz_desktop(client): continue
            self.process_picklist.add(process_name)
            if process_name not in self.process_blacklist: # user filter
                if glob.num_monitors > 1:
                    win_geom = support.get_geom(win_id)
                    win_curr_monitor = screen.get_monitor_at_point(win_geom[0]+win_geom[2]/2,
                                                                   win_geom[1]+win_geom[3]/2)
                else: win_curr_monitor = 0
                if win_curr_monitor == 0: cell_background = None
                else: cell_background = 'gray'
                if process_name not in self.process_whitelist: flagged = False
                else: flagged = True
                if win_curr_monitor == 0: self.liststore.prepend([flagged, client, title, pxb, False, cell_background])
                else: self.liststore.append([flagged, client, title, pxb, False, cell_background])
                rows_num += 1
        if rows_num == 2:
            iter = self.liststore.get_iter_first()
            while iter != None:
                self.liststore[iter][0] = True
                iter = self.liststore.iter_next(iter)

    def flag_all_rows(self):
        """Flags All Rows"""
        if glob.num_monitors > 1:
            all_rows_flagged_on_monitor_1 = True
            iter = self.liststore.get_iter_first()
            while iter != None:
                if self.liststore[iter][0] == False:
                    all_rows_flagged_on_monitor_1 = False
                    break
                iter = self.liststore.iter_next(iter)
        else: all_rows_flagged_on_monitor_1 = False
        iter = self.liststore.get_iter_first()
        while iter != None:
            if not all_rows_flagged_on_monitor_1:
                self.liststore[iter][0] = True
                self.liststore[iter][4] = False
            else:
                self.liststore[iter][0] = False
                self.liststore[iter][4] = True
            iter = self.liststore.iter_next(iter)

    def unflag_all_rows(self):
        """Unflags All Rows"""
        iter = self.liststore.get_iter_first()
        while iter != None:
            self.liststore[iter][0] = False
            self.liststore[iter][4] = False
            iter = self.liststore.iter_next(iter)

    def get_checked_windows_list(self, undo_ready=False):
        """Returns the list of the checked windows"""
        checked_windows_list = [[],[]]
        if undo_ready:
            # undo_snap_vec is 0:win_id 1:is_maximized 2:x 3:y 4:width 5:height
            undo_snap_vec = []
        tree_iter = self.liststore.get_iter_first()
        while tree_iter != None:
            try :win_id = self.liststore[tree_iter][1]
            except: continue
            if self.liststore[tree_iter][0] == True:
                checked_windows_list[0].append(win_id)
            elif self.liststore[tree_iter][4] == True:
                checked_windows_list[1].append(win_id)
            if undo_ready and (self.liststore[tree_iter][0] or self.liststore[tree_iter][4]):
                if support.is_window_Vmax(win_id) or support.is_window_Hmax(win_id): is_maximized = 1
                else: is_maximized = 0
                win_geom = support.get_geom(win_id)
                undo_snap_vec.append([  str(win_id),
                                        str(is_maximized),
                                        str(win_geom[0]),
                                        str(win_geom[1]),
                                        str(win_geom[2]),
                                        str(win_geom[3])  ])
            tree_iter = self.liststore.iter_next(tree_iter)
        if undo_ready and undo_snap_vec:
            support.undo_snap_write(self.gconf_client, undo_snap_vec)
        return checked_windows_list

    def close_checked_windows(self):
        """Closes the checked windows and removes the rows from the model"""
        iter = self.liststore.get_iter_first()
        while iter != None:
            next_iter = self.liststore.iter_next(iter)
            if self.liststore[iter][0] == True or self.liststore[iter][4] == True:
                support.client_msg(self.liststore[iter][1],"_NET_CLOSE_WINDOW",0,0,0,0,0)
                glob.x11.XSync(glob.disp, False)
                self.liststore.remove(iter)
            iter = next_iter

    def row_up(self, node_iter):
        """Row up one position"""
        prev_iter = self.liststore.iter_previous(node_iter)
        if prev_iter != None: self.liststore.swap(node_iter, prev_iter)

    def row_down(self, node_iter):
        """Row down one position"""
        subseq_iter = self.liststore.iter_next(node_iter)
        if subseq_iter != None: self.liststore.swap(node_iter, subseq_iter)

    def row_delete(self, node_iter):
        """Row remove"""
        self.liststore.remove(node_iter)

    def get_model(self):
        """Returns the model"""
        return self.liststore


class GladeWidgetsWrapper:
    """Handles the retrieval of glade widgets"""

    def __init__(self, glade_file_path, gui_instance):
        try:
            self.glade_widgets = Gtk.Builder()
            self.glade_widgets.set_translation_domain(cons.APP_NAME)
            self.glade_widgets.add_from_file(glade_file_path)
            self.glade_widgets.connect_signals(gui_instance)
        except: print "Failed to load the glade file"

    def __getitem__(self, key):
        """Gives us the ability to do: wrapper['widget_name'].action()"""
        return self.glade_widgets.get_object(key)

    def __getattr__(self, attr):
        """Gives us the ability to do: wrapper.widget_name.action()"""
        new_widget = self.glade_widgets.get_object(attr)
        if new_widget is None: raise AttributeError, 'Widget %r not found' % attr
        setattr(self, attr, new_widget)
        return new_widget


class XTile:
    """The application's main window"""

    def __init__(self, store):
        """Instantiate the Glade Widgets Wrapper, create the view,
        retrieves and stores the information about the running desktop self.geometry"""
        # create a variable pointing to the instance of the InfoModel class
        self.store = store
        # system settings
        try:
            gtk_settings = Gtk.Settings.get_default()
            gtk_settings.set_property("gtk-button-images", True)
            gtk_settings.set_property("gtk-menu-images", True)
        except: pass # older gtk do not have the property "gtk-menu-images"
        os.environ['UBUNTU_MENUPROXY'] = '0' # for custom stock icons not visible in appmenu
        self.cmd_line_only = False
        # instantiate the Glade Widgets Wrapper
        self.glade = GladeWidgetsWrapper(cons.GLADE_PATH + 'x-tile.glade', self)
        # ui manager
        actions = Gtk.ActionGroup("Actions")
        actions.add_actions(cons.get_entries(self))
        self.ui = Gtk.UIManager()
        self.ui.insert_action_group(actions, 0)
        self.glade.window.add_accel_group(self.ui.get_accel_group())
        self.ui.add_ui_from_string(cons.UI_INFO)
        # menubar add
        self.glade.vbox_main.pack_start(self.ui.get_widget("/MenuBar"), False, False, 0)
        self.glade.vbox_main.reorder_child(self.ui.get_widget("/MenuBar"), 0)
        # toolbar add
        self.glade.vbox_main.pack_start(self.ui.get_widget("/ToolBar"), False, False, 0)
        self.glade.vbox_main.reorder_child(self.ui.get_widget("/ToolBar"), 1)
        self.ui.get_widget("/ToolBar").set_style(Gtk.ToolbarStyle.ICONS)
        # create the view
        self.view = Gtk.TreeView(store.get_model())
        self.view.set_headers_visible(False)
        self.renderer_checkbox = Gtk.CellRendererToggle()
        self.renderer_checkbox.set_property('activatable', True)
        self.renderer_checkbox.connect('toggled', self.toggle_active, self.store.liststore)
        self.renderer_checkbox2 = Gtk.CellRendererToggle()
        self.renderer_checkbox2.set_property('activatable', True)
        self.renderer_checkbox2.connect('toggled', self.toggle_active2, self.store.liststore)
        self.renderer_pixbuf = Gtk.CellRendererPixbuf()
        self.renderer_text = Gtk.CellRendererText()
        self.columns = [None]*4
        self.columns[0] = Gtk.TreeViewColumn("Tile", self.renderer_checkbox, active=0) # active=0 <> read from column 0 of model
        self.columns[0].add_attribute(self.renderer_checkbox, "cell-background", 5)
        self.columns[1] = Gtk.TreeViewColumn("Tile", self.renderer_checkbox2, active=4) # active=4 <> read from column 4 of model
        self.columns[1].add_attribute(self.renderer_checkbox2, "cell-background", 5)
        self.columns[2] = Gtk.TreeViewColumn("Logo", self.renderer_pixbuf)
        self.columns[2].set_cell_data_func(self.renderer_pixbuf, self.make_pixbuf)
        self.columns[2].add_attribute(self.renderer_pixbuf, "cell-background", 5)
        self.columns[3] = Gtk.TreeViewColumn("Window Description", self.renderer_text, text=2) # text=2 <> read from column 2 of model
        self.columns[3].add_attribute(self.renderer_text, "cell-background", 5)
        for n in range(4): self.view.append_column(self.columns[n])
        if glob.num_monitors < 2: self.columns[1].set_visible(False)
        self.view.set_reorderable(True) # allow drag and drop reordering of rows
        self.view.set_tooltip_text(_("Use Drag and Drop to Sort the Rows"))
        self.view.connect('button-press-event', self.on_mouse_button_clicked_list)
        self.no_toggling_signals = False
        self.viewselection = self.view.get_selection()
        self.glade.scrolledwindow.add(self.view)
        self.glade.processadddialog.connect('key_press_event', self.on_key_press_processadddialog)
        self.glade.drawingarea.connect('draw', self.on_drawing_area_draw)
        self.glade.aboutdialog.set_version(cons.VERSION)
        self.glade.window.set_title(self.glade.window.get_title() + " " + cons.VERSION)
        self.gconf_client = GConf.Client.get_default()
        self.gconf_client.add_dir("/apps/x-tile/%s" % glob.screen_index, GConf.ClientPreloadType.PRELOAD_NONE)
        self.combobox_country_lang_init()

    def combobox_country_lang_init(self):
        """Init The Programming Languages Syntax Highlighting"""
        combobox = self.glade.combobox_country_language
        self.country_lang_liststore = Gtk.ListStore(str)
        combobox.set_model(self.country_lang_liststore)
        cell = Gtk.CellRendererText()
        combobox.pack_start(cell, True)
        combobox.add_attribute(cell, 'text', 0)
        for country_lang in cons.AVAILABLE_LANGS:
            self.country_lang_liststore.append([country_lang])
        combobox.set_active_iter(self.get_combobox_country_lang_iter(self.gconf_client.get_string(cons.GCONF_LANG)))
        self.glade.combobox_country_language.connect('changed', self.on_combobox_country_language_changed)

    def get_combobox_country_lang_iter(self, country_language):
        """Returns the Language iter Given the Language Name"""
        curr_iter = self.country_lang_liststore.get_iter_first()
        while curr_iter != None:
            if self.country_lang_liststore[curr_iter][0] == country_language: break
            else: curr_iter = self.country_lang_liststore.iter_next(curr_iter)
        else: return self.country_lang_liststore.get_iter_first()
        return curr_iter

    def on_combobox_country_language_changed(self, combobox):
        """New Country Language Choosed"""
        new_iter = self.glade.combobox_country_language.get_active_iter()
        new_lang = self.country_lang_liststore[new_iter][0]
        if new_lang != self.gconf_client.get_string(cons.GCONF_LANG):
            self.country_lang = new_lang
            support.dialog_info(_("The New Language will be Available Only After Restarting X Tile"), self.glade.window)
            self.gconf_client.set_string(cons.GCONF_LANG, new_lang)
    
    def status_icon_enable(self):
        """Creates the Stats Icon"""
        if HAS_APPINDICATOR:
            self.ind = appindicator.Indicator.new("x-tile", "indicator-messages", appindicator.IndicatorCategory.APPLICATION_STATUS)
            self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)
            self.ind.set_attention_icon("indicator-messages-new")
            for icp in ["/usr/share/icons/hicolor/scalable/apps/x-tile.svg", "/usr/local/share/icons/hicolor/scalable/apps/x-tile.svg", "glade/x-tile.svg"]:
                if os.path.isfile(icp):
                    icon_path = icp
                    break
            else: icon_path = cons.APP_NAME
            self.ind.set_icon(icon_path)
            self.ind.set_menu(self.ui.get_widget("/SysTrayMenu"))
        else:
            self.status_icon = Gtk.StatusIcon()
            self.status_icon.set_from_stock("Tile Quad")
            self.status_icon.connect('button-press-event', self.on_mouse_button_clicked_systray)
            self.status_icon.set_tooltip(_("Tile the Windows Upon your X Desktop"))
    
    def on_mouse_button_clicked_systray(self, widget, event):
        """Catches mouse buttons clicks upon the system tray icon"""
        if event.button == 1: self.toggle_show_hide_main_window()
        elif event.button == 3: self.ui.get_widget("/SysTrayMenu").popup(None, None, None, event.button, event.time)
    
    def toggle_show_hide_main_window(self, *args):
        if self.win_on_screen: self.window_hide()
        else:
            self.window_position_restore()
            self.glade.window.show()
            self.reload_windows_list()
            self.win_on_screen = True
    
    def on_checkbutton_systray_docking_toggled(self, checkbutton):
        """SysTray Toggled Handling"""
        self.systray_on = checkbutton.get_active()
        if self.systray_on:
            if not HAS_APPINDICATOR:
                if "status_icon" in dir(self): self.status_icon.set_property('visible', True)
                else: self.status_icon_enable()
            else:
                if "ind" in dir(self): self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)
                else: self.status_icon_enable()
            self.ui.get_widget("/MenuBar/FileMenu/ExitApp").set_property('visible', True)
            self.glade.checkbutton_start_minimized.set_sensitive(True)
            if self.gconf_client.get_string(cons.GCONF_SYSTRAY_ENABLE % glob.screen_index) != cons.STR_TRUE:
                self.gconf_client.set_string(cons.GCONF_SYSTRAY_ENABLE % glob.screen_index, cons.STR_TRUE)
        else:
            if not HAS_APPINDICATOR:
                if not "status_icon" in dir(self): self.status_icon_enable()
                self.status_icon.set_property('visible', False)
            else:
                if not "ind" in dir(self): self.status_icon_enable()
                self.ind.set_status(appindicator.IndicatorStatus.PASSIVE)
            self.ui.get_widget("/MenuBar/FileMenu/ExitApp").set_property('visible', False)
            self.glade.checkbutton_start_minimized.set_sensitive(False)
            if self.gconf_client.get_string(cons.GCONF_SYSTRAY_ENABLE % glob.screen_index) != cons.STR_FALSE:
                self.gconf_client.set_string(cons.GCONF_SYSTRAY_ENABLE % glob.screen_index, cons.STR_FALSE)

    def on_checkbutton_start_minimized_toggled(self, checkbutton):
        """Start Minimized on SysTray Toggled Handling"""
        if checkbutton.get_active():
            if self.gconf_client.get_string(cons.GCONF_SYSTRAY_START % glob.screen_index) != cons.STR_TRUE:
                self.gconf_client.set_string(cons.GCONF_SYSTRAY_START % glob.screen_index, cons.STR_TRUE)
        else:
            if self.gconf_client.get_string(cons.GCONF_SYSTRAY_START % glob.screen_index) != cons.STR_FALSE:
                self.gconf_client.set_string(cons.GCONF_SYSTRAY_START % glob.screen_index, cons.STR_FALSE)
    
    def on_checkbutton_override_monitor_1_area_toggled(self, checkbutton):
        """Override Area 1 Checkbox was Toggled"""
        if checkbutton.get_active(): cons.OVERRIDE_1 = 1
        else:
            cons.OVERRIDE_1 = 0
            glob.read_monitors_areas()
            cons.X1 = glob.monitors_areas[0][0]
            cons.Y1 = glob.monitors_areas[0][1]
            cons.W1 = glob.monitors_areas[0][2]
            cons.H1 = glob.monitors_areas[0][3]
            self.glade.spinbutton_x1.set_value(cons.X1)
            self.glade.spinbutton_y1.set_value(cons.Y1)
            self.glade.spinbutton_w1.set_value(cons.W1)
            self.glade.spinbutton_h1.set_value(cons.H1)
        self.gconf_client.set_int(cons.GCONF_OVERRIDE_1 % glob.screen_index, cons.OVERRIDE_1)
        self.glade.vbox_override_area_1.set_sensitive(cons.OVERRIDE_1 == 1)

    def on_checkbutton_override_monitor_2_area_toggled(self, checkbutton):
        """Override Area 1 Checkbox was Toggled"""
        if checkbutton.get_active(): cons.OVERRIDE_2 = 1
        else:
            cons.OVERRIDE_2 = 0
            glob.read_monitors_areas()
            cons.X2 = glob.monitors_areas[1][0]
            cons.Y2 = glob.monitors_areas[1][1]
            cons.W2 = glob.monitors_areas[1][2]
            cons.H2 = glob.monitors_areas[1][3]
            self.glade.spinbutton_x2.set_value(cons.X2)
            self.glade.spinbutton_y2.set_value(cons.Y2)
            self.glade.spinbutton_w2.set_value(cons.W2)
            self.glade.spinbutton_h2.set_value(cons.H2)
        self.gconf_client.set_int(cons.GCONF_OVERRIDE_2 % glob.screen_index, cons.OVERRIDE_2)
        self.glade.vbox_override_area_2.set_sensitive(cons.OVERRIDE_2 == 1)

    def init_from_gconf(self):
        """Init the geometry and the spinbuttons"""
        glob.read_monitors_areas()
        self.glade.drawingarea.set_property("width-request", glob.drawing_rect[2])
        self.glade.drawingarea.set_property("height-request", glob.drawing_rect[3])
        self.custom_geoms_1 = []
        custom_geoms_str = self.gconf_client.get_string(cons.GCONF_CUSTOM_1 % glob.screen_index)
        if custom_geoms_str:
            custom_geoms_vec = custom_geoms_str.split(" ")
            for custom_geom in custom_geoms_vec:
                x, y, width, height = custom_geom.split(",")
                self.custom_geoms_1.append([int(x), int(y), int(width), int(height)])
        self.custom_geoms_2 = []
        custom_geoms_str = self.gconf_client.get_string(cons.GCONF_CUSTOM_2 % glob.screen_index)
        if custom_geoms_str:
            custom_geoms_vec = custom_geoms_str.split(" ")
            for custom_geom in custom_geoms_vec:
                x, y, width, height = custom_geom.split(",")
                self.custom_geoms_2.append([int(x), int(y), int(width), int(height)])
        if self.gconf_client.get_string(cons.GCONF_EXIT_AFTER_TILE % glob.screen_index) == None:
            self.gconf_client.set_string(cons.GCONF_EXIT_AFTER_TILE % glob.screen_index, cons.STR_TRUE)
        if self.gconf_client.get_string(cons.GCONF_NOT_MINIMIZED % glob.screen_index) == None:
            self.gconf_client.set_string(cons.GCONF_NOT_MINIMIZED % glob.screen_index, cons.STR_TRUE)
        if self.gconf_client.get_string(cons.GCONF_ONLY_CURR_DESK % glob.screen_index) == None:
            self.gconf_client.set_string(cons.GCONF_ONLY_CURR_DESK % glob.screen_index, cons.STR_FALSE)
        # systray handling
        if self.gconf_client.get_string(cons.GCONF_SYSTRAY_ENABLE % glob.screen_index) == None:
            self.gconf_client.set_string(cons.GCONF_SYSTRAY_ENABLE % glob.screen_index, cons.STR_TRUE)
        if self.gconf_client.get_string(cons.GCONF_SYSTRAY_START % glob.screen_index) == None:
            self.gconf_client.set_string(cons.GCONF_SYSTRAY_START % glob.screen_index, cons.STR_FALSE)
        if self.gconf_client.get_string(cons.GCONF_SYSTRAY_ENABLE % glob.screen_index) == cons.STR_TRUE:
            self.status_icon_enable()
            self.systray_on = True
            self.ui.get_widget("/MenuBar/FileMenu/ExitApp").set_property('visible', True)
        else:
            self.systray_on = False
            self.ui.get_widget("/MenuBar/FileMenu/ExitApp").set_property('visible', False)
        # exit after tile
        self.glade.exit_after_tile_checkbutton.set_active(self.gconf_client.get_string(cons.GCONF_EXIT_AFTER_TILE % glob.screen_index) == cons.STR_TRUE)
        # monitor 1 handling
        if self.gconf_client.get_int(cons.GCONF_OVERRIDE_1 % glob.screen_index) == 1:
            cons.OVERRIDE_1 = 1
            cons.X1 = self.gconf_client.get_int(cons.GCONF_X1 % glob.screen_index)
            cons.Y1 = self.gconf_client.get_int(cons.GCONF_Y1 % glob.screen_index)
            cons.W1 = self.gconf_client.get_int(cons.GCONF_W1 % glob.screen_index)
            cons.H1 = self.gconf_client.get_int(cons.GCONF_H1 % glob.screen_index)
            glob.monitors_areas[0] = [cons.X1, cons.Y1, cons.W1, cons.H1]
        else:
            cons.X1 = glob.monitors_areas[0][0]
            cons.Y1 = glob.monitors_areas[0][1]
            cons.W1 = glob.monitors_areas[0][2]
            cons.H1 = glob.monitors_areas[0][3]
        # monitor 2 handling
        if glob.num_monitors > 1:
            if self.gconf_client.get_int(cons.GCONF_OVERRIDE_2 % glob.screen_index) == 1:
                cons.OVERRIDE_2 = 1
                cons.X2 = self.gconf_client.get_int(cons.GCONF_X2 % glob.screen_index)
                cons.Y2 = self.gconf_client.get_int(cons.GCONF_Y2 % glob.screen_index)
                cons.W2 = self.gconf_client.get_int(cons.GCONF_W2 % glob.screen_index)
                cons.H2 = self.gconf_client.get_int(cons.GCONF_H2 % glob.screen_index)
                glob.monitors_areas[1] = [cons.X2, cons.Y2, cons.W2, cons.H2]
            else:
                cons.X2 = glob.monitors_areas[1][0]
                cons.Y2 = glob.monitors_areas[1][1]
                cons.W2 = glob.monitors_areas[1][2]
                cons.H2 = glob.monitors_areas[1][3]
        # grid parameters
        grid_rows = self.gconf_client.get_int(cons.GCONF_GRID_ROWS % glob.screen_index)
        if grid_rows: cons.GRID_ROWS = grid_rows
        grid_cols = self.gconf_client.get_int(cons.GCONF_GRID_COLS % glob.screen_index)
        if grid_cols: cons.GRID_COLS = grid_cols

        key = self.gconf_client.get_int(cons.GCONF_TOOLBAR_ICON_SIZE % glob.screen_index)
        if key not in cons.ICONS_SIZE: self.gconf_client.set_int(cons.GCONF_TOOLBAR_ICON_SIZE % glob.screen_index, 3)
        self.ui.get_widget("/ToolBar").set_property("icon-size",
              cons.ICONS_SIZE[self.gconf_client.get_int(cons.GCONF_TOOLBAR_ICON_SIZE % glob.screen_index)])

        blacklist = self.gconf_client.get_string(cons.GCONF_PROCESS_BLACKLIST % glob.screen_index)
        if blacklist not in [None, ""]:
            for element in blacklist.split():
                self.store.process_blacklist.add(element)
        whitelist = self.gconf_client.get_string(cons.GCONF_PROCESS_WHITELIST % glob.screen_index)
        if whitelist not in [None, ""]:
            for element in whitelist.split():
                self.store.process_whitelist.add(element)

        self.glade.checkbutton_override_monitor_1_area.set_active(cons.OVERRIDE_1 == 1)
        self.glade.checkbutton_override_monitor_2_area.set_active(cons.OVERRIDE_2 == 1)
        self.glade.spinbutton_x1.set_value(cons.X1)
        self.glade.spinbutton_y1.set_value(cons.Y1)
        self.glade.spinbutton_w1.set_value(cons.W1)
        self.glade.spinbutton_h1.set_value(cons.H1)
        self.glade.spinbutton_x2.set_value(cons.X2)
        self.glade.spinbutton_y2.set_value(cons.Y2)
        self.glade.spinbutton_w2.set_value(cons.W2)
        self.glade.spinbutton_h2.set_value(cons.H2)
        self.glade.vbox_override_area_1.set_sensitive(cons.OVERRIDE_1 == 1)
        self.glade.vbox_override_area_2.set_sensitive(cons.OVERRIDE_2 == 1)
        self.glade.checkbutton_override_monitor_2_area.set_sensitive(glob.num_monitors > 1)
        self.win_size_n_pos = {}
        self.win_size_n_pos['win_size'] = [self.gconf_client.get_int(cons.GCONF_WIN_SIZE_W % glob.screen_index),
                                           self.gconf_client.get_int(cons.GCONF_WIN_SIZE_H % glob.screen_index)]
        if 0 not in self.win_size_n_pos['win_size']:
            self.glade.window.resize(self.win_size_n_pos['win_size'][0], self.win_size_n_pos['win_size'][1])

    def window_position_restore(self):
        """Restore window size and position"""
        self.win_size_n_pos['win_position'] = [self.gconf_client.get_int(cons.GCONF_WIN_POSITION_X % glob.screen_index),
                                               self.gconf_client.get_int(cons.GCONF_WIN_POSITION_Y % glob.screen_index)]
        self.glade.window.move(self.win_size_n_pos['win_position'][0], self.win_size_n_pos['win_position'][1])

    def toolbar_icons_size_increase(self, *args):
        """Increase the Size of the Toolbar Icons"""
        toolbar_icon_size = self.gconf_client.get_int(cons.GCONF_TOOLBAR_ICON_SIZE % glob.screen_index)
        if toolbar_icon_size == 5:
            support.dialog_info(_("The Size of the Toolbar Icons is already at the Maximum Value"), self.glade.window)
            return
        toolbar_icon_size += 1
        self.gconf_client.set_int(cons.GCONF_TOOLBAR_ICON_SIZE % glob.screen_index, toolbar_icon_size)
        self.ui.get_widget("/ToolBar").set_property("icon-size", cons.ICONS_SIZE[toolbar_icon_size])

    def toolbar_icons_size_decrease(self, *args):
        """Decrease the Size of the Toolbar Icons"""
        toolbar_icon_size = self.gconf_client.get_int(cons.GCONF_TOOLBAR_ICON_SIZE % glob.screen_index)
        if toolbar_icon_size == 1:
            support.dialog_info(_("The Size of the Toolbar Icons is already at the Minimum Value"), self.glade.window)
            return
        toolbar_icon_size -= 1
        self.gconf_client.set_int(cons.GCONF_TOOLBAR_ICON_SIZE % glob.screen_index, toolbar_icon_size)
        self.ui.get_widget("/ToolBar").set_property("icon-size", cons.ICONS_SIZE[toolbar_icon_size])

    def toggle_active(self, cell, path, model):
        """Toggles the Active state"""
        model[path][0] = not model[path][0]
        model[path][4] = False

    def toggle_active2(self, cell, path, model):
        """Toggles the Active state"""
        model[path][4] = not model[path][4]
        model[path][0] = False

    def toggle_exit_after_tile(self, *args):
        """Toggles the flag Exit After Tile"""
        if not self.no_toggling_signals:
            if self.gconf_client.get_string(cons.GCONF_EXIT_AFTER_TILE % glob.screen_index) == cons.STR_TRUE:
                self.gconf_client.set_string(cons.GCONF_EXIT_AFTER_TILE % glob.screen_index, cons.STR_FALSE)
            else: self.gconf_client.set_string(cons.GCONF_EXIT_AFTER_TILE % glob.screen_index, cons.STR_TRUE)

    def toggle_do_not_list_minimized(self, *args):
        """Toggles the flag Do Not List Minimized Windows in List"""
        if not self.no_toggling_signals:
            if self.gconf_client.get_string(cons.GCONF_NOT_MINIMIZED % glob.screen_index) == cons.STR_TRUE:
                self.gconf_client.set_string(cons.GCONF_NOT_MINIMIZED % glob.screen_index, cons.STR_FALSE)
            else: self.gconf_client.set_string(cons.GCONF_NOT_MINIMIZED % glob.screen_index, cons.STR_TRUE)
            self.store.load_model(self)

    def toggle_only_curr_workspace(self, *args):
        """Toggles the flag Only Current Workspace Windows in List"""
        if not self.no_toggling_signals:
            if self.gconf_client.get_string(cons.GCONF_ONLY_CURR_DESK % glob.screen_index) == cons.STR_TRUE:
                self.gconf_client.set_string(cons.GCONF_ONLY_CURR_DESK % glob.screen_index, cons.STR_FALSE)
            else: self.gconf_client.set_string(cons.GCONF_ONLY_CURR_DESK % glob.screen_index, cons.STR_TRUE)
            self.store.load_model(self)

    def is_window_visible(self):
        """Returns True if the window is visible, False otherwise"""
        return self.glade.window.get_property("visible")

    def flag_all_rows(self, *args):
        """Flags All Rows"""
        self.store.flag_all_rows()

    def unflag_all_rows(self, *args):
        """Unflags All Rows"""
        self.store.unflag_all_rows()

    def make_pixbuf(self, treeviewcolumn, cell, tree_model, tree_iter, data):
        """Function to associate the pixbuf to the cell renderer"""
        try:
            pixbuf = tree_model[tree_iter][3]
            cell.set_property('pixbuf', pixbuf)
        except: pass

    def on_window_delete_event(self, widget, event, data=None):
        """Before close the application: no checks needed"""
        self.quit_application()
        return True # do not propogate the delete event

    def on_configwindow_delete_event(self, widget, event, data=None):
        """Destroy the config window"""
        self.on_configwin_close_button_clicked()
        return True # do not propogate the delete event

    def dialog_preferences(self, *args):
        """Open the Config Window"""
        if self.glade.configwindow.get_property("visible") == True: return
        self.no_toggling_signals = True
        self.glade.current_workspace_checkbutton.set_active(self.gconf_client.get_string(cons.GCONF_ONLY_CURR_DESK % glob.screen_index) == cons.STR_TRUE)
        self.glade.do_not_list_minimized_checkbutton.set_active(self.gconf_client.get_string(cons.GCONF_NOT_MINIMIZED % glob.screen_index) == cons.STR_TRUE)
        self.glade.checkbutton_systray_docking.set_active(self.gconf_client.get_string(cons.GCONF_SYSTRAY_ENABLE % glob.screen_index) == cons.STR_TRUE)
        self.glade.checkbutton_start_minimized.set_active(self.gconf_client.get_string(cons.GCONF_SYSTRAY_START % glob.screen_index) == cons.STR_TRUE)
        self.glade.show_toolbar_checkbutton.set_active(self.gconf_client.get_string(cons.GCONF_SHOW_TOOLBAR % glob.screen_index) == cons.STR_TRUE)
        self.no_toggling_signals = False
        self.glade.configwindow.show_all()

    def on_configwin_close_button_clicked(self, *args):
        """Hide the Dialog"""
        self.glade.configwindow.hide()
        cons.X1 = int(self.glade.spinbutton_x1.get_value())
        cons.Y1 = int(self.glade.spinbutton_y1.get_value())
        cons.W1 = int(self.glade.spinbutton_w1.get_value())
        cons.H1 = int(self.glade.spinbutton_h1.get_value())
        if cons.OVERRIDE_1 == 1:
            glob.monitors_areas[0] = [cons.X1, cons.Y1, cons.W1, cons.H1]
            self.gconf_client.set_int(cons.GCONF_X1 % glob.screen_index, cons.X1)
            self.gconf_client.set_int(cons.GCONF_Y1 % glob.screen_index, cons.Y1)
            self.gconf_client.set_int(cons.GCONF_W1 % glob.screen_index, cons.W1)
            self.gconf_client.set_int(cons.GCONF_H1 % glob.screen_index, cons.H1)
        if glob.num_monitors > 1:
            cons.X2 = int(self.glade.spinbutton_x2.get_value())
            cons.Y2 = int(self.glade.spinbutton_y2.get_value())
            cons.W2 = int(self.glade.spinbutton_w2.get_value())
            cons.H2 = int(self.glade.spinbutton_h2.get_value())
            if cons.OVERRIDE_2 == 1:
                glob.monitors_areas[1] = [cons.X2, cons.Y2, cons.W2, cons.H2]
                self.gconf_client.set_int(cons.GCONF_X2 % glob.screen_index, cons.X2)
                self.gconf_client.set_int(cons.GCONF_Y2 % glob.screen_index, cons.Y2)
                self.gconf_client.set_int(cons.GCONF_W2 % glob.screen_index, cons.W2)
                self.gconf_client.set_int(cons.GCONF_H2 % glob.screen_index, cons.H2)

    def on_button_row_up_clicked(self, *args):
        """Move the selected row up of one position"""
        model, iter = self.viewselection.get_selected()
        if iter == None:
            support.dialog_warning(_("No Row is Selected"), self.glade.window)
            return
        self.store.row_up(iter)

    def on_button_row_down_clicked(self, *args):
        """Move the selected row up of one position"""
        model, iter = self.viewselection.get_selected()
        if iter == None:
            support.dialog_warning(_("No Row is Selected"), self.glade.window)
            return
        self.store.row_down(iter)

    def on_button_row_delete_clicked(self, *args):
        """Remove the selected row"""
        model, iter = self.viewselection.get_selected()
        if iter == None:
            support.dialog_warning(_("No Row is Selected"), self.glade.window)
            return
        self.store.row_delete(iter)

    def on_button_add_filter_clicked(self, *args):
        """Application Filter Add"""
        self.process_add_list_exist_or_create()
        self.process_add_liststore.clear()
        for element in self.store.process_picklist:
            self.process_add_liststore.append([element])
        response = self.glade.processadddialog.run()
        self.glade.processadddialog.hide()
        if response != 1: return
        model, iter = self.process_add_treeviewselection.get_selected()
        if iter == None: return
        self.store.process_blacklist.add(model[iter][0])
        self.filter_list_update()

    def on_button_remove_filter_clicked(self, *args):
        """Application Filter Remove"""
        model, iter = self.filter_treeviewselection.get_selected()
        if iter == None:
            support.dialog_warning(_("No Application Selected!"), self.glade.window)
            return
        self.store.process_blacklist.remove(model[iter][0])
        self.filter_list_update()

    def dialog_filter(self, action):
        """Application's Filter Dialog"""
        self.filter_list_exist_or_create()
        self.filter_list_update()
        self.glade.filterdialog.run()
        self.glade.filterdialog.hide()
        if len(self.store.process_blacklist) > 0:
            self.gconf_client.set_string(cons.GCONF_PROCESS_BLACKLIST % glob.screen_index, " ".join(self.store.process_blacklist))
        else: self.gconf_client.set_string(cons.GCONF_PROCESS_BLACKLIST % glob.screen_index, "")
        self.reload_windows_list()

    def on_button_add_white_clicked(self, *args):
        """Application Whitelist Add"""
        self.process_add_list_exist_or_create()
        self.process_add_liststore.clear()
        for element in self.store.process_picklist:
            self.process_add_liststore.append([element])
        response = self.glade.processadddialog.run()
        self.glade.processadddialog.hide()
        if response != 1: return
        model, iter = self.process_add_treeviewselection.get_selected()
        if iter == None: return
        self.store.process_whitelist.add(model[iter][0])
        self.white_list_update()

    def on_button_remove_white_clicked(self, *args):
        """Application Whitelist Remove"""
        model, iter = self.white_treeviewselection.get_selected()
        if iter == None:
            support.dialog_warning(_("No Application Selected!"), self.glade.window)
            return
        self.store.process_whitelist.remove(model[iter][0])
        self.white_list_update()

    def dialog_selected_by_default(self, action):
        """Dialog to select a list of windows to be flagged by Default"""
        self.white_list_exist_or_create()
        self.white_list_update()
        self.glade.whitedialog.run()
        self.glade.whitedialog.hide()
        if len(self.store.process_whitelist) > 0:
            self.gconf_client.set_string(cons.GCONF_PROCESS_WHITELIST % glob.screen_index, " ".join(self.store.process_whitelist))
        else: self.gconf_client.set_string(cons.GCONF_PROCESS_WHITELIST % glob.screen_index, "")
        self.reload_windows_list()

    def filter_list_update(self):
        """Updates the Process Filter List"""
        self.filter_liststore.clear()
        for element in self.store.process_blacklist:
            self.filter_liststore.append([element])

    def white_list_update(self):
        """Updates the Process White List"""
        self.white_liststore.clear()
        for element in self.store.process_whitelist:
            self.white_liststore.append([element])

    def filter_list_exist_or_create(self):
        """If The List Was Never Used, this will Create It"""
        if not "filter_liststore" in dir(self):
            self.filter_liststore = Gtk.ListStore(str)
            self.filter_treeview = Gtk.TreeView(self.filter_liststore)
            self.filter_treeview.set_headers_visible(False)
            self.filter_renderer_text = Gtk.CellRendererText()
            self.filter_column = Gtk.TreeViewColumn("Application", self.filter_renderer_text, text=0)
            self.filter_treeview.append_column(self.filter_column)
            self.filter_treeviewselection = self.filter_treeview.get_selection()
            self.glade.scrolledwindow_filter.add(self.filter_treeview)
            self.glade.scrolledwindow_filter.show_all()

    def white_list_exist_or_create(self):
        """If The List Was Never Used, this will Create It"""
        if not "white_liststore" in dir(self):
            self.white_liststore = Gtk.ListStore(str)
            self.white_treeview = Gtk.TreeView(self.white_liststore)
            self.white_treeview.set_headers_visible(False)
            self.white_renderer_text = Gtk.CellRendererText()
            self.white_column = Gtk.TreeViewColumn("Application", self.white_renderer_text, text=0)
            self.white_treeview.append_column(self.white_column)
            self.white_treeviewselection = self.white_treeview.get_selection()
            self.glade.scrolledwindow_white.add(self.white_treeview)
            self.glade.scrolledwindow_white.show_all()

    def process_add_list_exist_or_create(self):
        """If The List Was Never Used, this will Create It"""
        if not "process_add_liststore" in dir(self):
            self.process_add_liststore = Gtk.ListStore(str)
            self.process_add_treeview = Gtk.TreeView(self.process_add_liststore)
            self.process_add_treeview.set_headers_visible(False)
            self.process_add_renderer_text = Gtk.CellRendererText()
            self.process_add_column = Gtk.TreeViewColumn("Application", self.process_add_renderer_text, text=0)
            self.process_add_treeview.append_column(self.process_add_column)
            self.process_add_treeviewselection = self.process_add_treeview.get_selection()
            self.process_add_treeview.connect('button-press-event', self.on_mouse_button_clicked_process_add)
            self.glade.scrolledwindow_process_add.add(self.process_add_treeview)
            self.glade.scrolledwindow_process_add.show_all()

    def on_mouse_button_clicked_process_add(self, widget, event):
        """Catches mouse buttons clicks"""
        if event.button != 1: return
        if event.type == Gdk.EventType._2BUTTON_PRESS: self.glade.processadddialog_button_ok.clicked()

    def on_key_press_processadddialog(self, widget, event):
        """Catches AnchorHandle Dialog key presses"""
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == "Return": self.glade.processadddialog_button_ok.clicked()

    def dialog_grid(self, *args):
        """Open the Grid Dialog"""
        dialog = Gtk.Dialog(title=_("Grid Details"),
                                    parent=self.glade.window,
                                    flags=Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                    buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                                    Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT) )
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        content_area = dialog.get_content_area()
        hbox_rows = Gtk.HBox()
        label_rows = Gtk.Label(label=_("Rows"))
        spinbutton_rows = Gtk.SpinButton()
        adj_rows = spinbutton_rows.get_adjustment()
        adj_rows.set_all(cons.GRID_ROWS, 1, 100, 1, 0, 0)
        hbox_rows.pack_start(label_rows, True, True, 0)
        hbox_rows.pack_start(spinbutton_rows, True, True, 0)
        hbox_cols = Gtk.HBox()
        label_cols = Gtk.Label(label=_("Columns"))
        spinbutton_cols = Gtk.SpinButton()
        adj_cols = spinbutton_cols.get_adjustment()
        adj_cols.set_all(cons.GRID_COLS, 1, 100, 1, 0, 0)
        hbox_cols.pack_start(label_cols, True, True, 0)
        hbox_cols.pack_start(spinbutton_cols, True, True, 0)
        content_area.pack_start(hbox_rows, True, True, 0)
        content_area.pack_start(hbox_cols, True, True, 0)
        def on_key_press_enter_password_dialog(widget, event):
            if Gdk.keyval_name(event.keyval) == "Return":
                button_box = dialog.get_action_area()
                buttons = button_box.get_children()
                buttons[0].clicked() # first is the ok button
        dialog.connect("key_press_event", on_key_press_enter_password_dialog)
        dialog.show_all()
        response = dialog.run()
        cons.GRID_ROWS = int(spinbutton_rows.get_value())
        cons.GRID_COLS = int(spinbutton_cols.get_value())
        dialog.destroy()
        if response != Gtk.ResponseType.ACCEPT: return
        self.gconf_client.set_int(cons.GCONF_GRID_ROWS % glob.screen_index, cons.GRID_ROWS)
        self.gconf_client.set_int(cons.GCONF_GRID_COLS % glob.screen_index, cons.GRID_COLS)
        self.tile_grid()

    def quit_application_totally(self, *args):
        """The process is Shut Down"""
        if not HAS_APPINDICATOR and "status_icon" in dir(self): self.status_icon.set_visible(False)
        self.save_win_pos_n_size()
        self.glade.window.destroy()
        Gtk.main_quit()
    
    def save_win_pos_n_size(self):
        """Destroy the window"""
        actual_win_size = list(self.glade.window.get_size())
        actual_win_pos = list(self.glade.window.get_position())
        if actual_win_size != self.win_size_n_pos['win_size']:
            self.win_size_n_pos['win_size'] = actual_win_size
            self.gconf_client.set_int(cons.GCONF_WIN_SIZE_W % glob.screen_index, self.win_size_n_pos['win_size'][0])
            self.gconf_client.set_int(cons.GCONF_WIN_SIZE_H % glob.screen_index, self.win_size_n_pos['win_size'][1])
        if actual_win_pos != self.win_size_n_pos['win_position']:
            self.win_size_n_pos['win_position'] = actual_win_pos
            self.gconf_client.set_int(cons.GCONF_WIN_POSITION_X % glob.screen_index, self.win_size_n_pos['win_position'][0])
            self.gconf_client.set_int(cons.GCONF_WIN_POSITION_Y % glob.screen_index, self.win_size_n_pos['win_position'][1])
    
    def window_hide(self):
        """Hide the Window"""
        self.save_win_pos_n_size()
        self.glade.window.hide()
        self.win_on_screen = False
    
    def quit_application(self, *args):
        """Hide the window"""
        if not self.systray_on: self.quit_application_totally()
        else: self.window_hide()

    def launch_application(self):
        """Show the main window and all child widgets"""
        self.init_from_gconf()
        self.window_position_restore()
        self.glade.window.show_all()
        if glob.is_compiz_running:
            self.glade.checkbutton_dest_workspace.set_active(False)
            self.glade.checkbutton_dest_workspace.hide()
            self.glade.spinbutton_dest_workspace.hide()
        show_toolbar = self.gconf_client.get_string(cons.GCONF_SHOW_TOOLBAR % glob.screen_index)
        if show_toolbar == None: self.gconf_client.set_string(cons.GCONF_SHOW_TOOLBAR % glob.screen_index, cons.STR_TRUE)
        elif show_toolbar == cons.STR_FALSE: self.ui.get_widget("/ToolBar").hide()
        self.win_on_screen = True
        if self.gconf_client.get_string(cons.GCONF_SYSTRAY_ENABLE % glob.screen_index) == cons.STR_FALSE:
            self.ui.get_widget("/MenuBar/FileMenu/ExitApp").set_property('visible', False)
        elif self.gconf_client.get_string(cons.GCONF_SYSTRAY_START % glob.screen_index) == cons.STR_TRUE:
            self.glade.window.hide()
            self.win_on_screen = False

    def reload_windows_list(self, *args):
        """Reloads the Windows List"""
        self.store.load_model(self)

    def close_checked_windows(self, *args):
        """Closes the Checked Windows"""
        number_of_windows = len(self.store.get_checked_windows_list())
        if number_of_windows < 1: support.dialog_warning(_('No Windows Checked'), self.glade.window)
        else: self.store.close_checked_windows()

    def maximize_checked_windows(self, *args):
        """Maximizes the Checked Windows"""
        checked_windows_lists = self.store.get_checked_windows_list(True)
        checked_windows_list = checked_windows_lists[0] + checked_windows_lists[1]
        number_of_windows = len(checked_windows_list)
        if number_of_windows < 1: support.dialog_warning(_('No Windows Checked'), self.glade.window)
        else:
            for checked_window in checked_windows_list: support.maximize(checked_window)
            self.check_exit_after_tile()

    def unmaximize_checked_windows(self, *args):
        """Unmaximizes the Checked Windows"""
        checked_windows_lists = self.store.get_checked_windows_list(True)
        checked_windows_list = checked_windows_lists[0] + checked_windows_lists[1]
        number_of_windows = len(checked_windows_list)
        if number_of_windows < 1: support.dialog_warning(_('No Windows Checked'), self.glade.window)
        else:
            for checked_window in checked_windows_list: support.unmaximize(checked_window)
            self.check_exit_after_tile()

    def tile_vertically(self, *args):
        """Tile the Checked Windows Vertically"""
        self.gconf_client.set_string(cons.GCONF_LATEST_TILING % glob.screen_index, "v")
        checked_windows_list = self.store.get_checked_windows_list(True)
        tilings.tile_vertically(checked_windows_list, glob.monitors_areas, self.get_dest_ws())
        self.check_exit_after_tile()

    def tile_horizontally(self, *args):
        """Tile the Checked Windows Horizontally"""
        self.gconf_client.set_string(cons.GCONF_LATEST_TILING % glob.screen_index, "h")
        checked_windows_list = self.store.get_checked_windows_list(True)
        tilings.tile_horizontally(checked_windows_list, glob.monitors_areas, self.get_dest_ws())
        self.check_exit_after_tile()

    def tile_quad(self, *args):
        """Tile the Checked Windows Quad"""
        self.gconf_client.set_string(cons.GCONF_LATEST_TILING % glob.screen_index, "q")
        checked_windows_list = self.store.get_checked_windows_list(True)
        tilings.tile_quad(checked_windows_list, glob.monitors_areas, self.get_dest_ws())
        self.check_exit_after_tile()

    def tile_grid(self):
        """Tile the Checked Windows in a rows by cols grid"""
        self.gconf_client.set_string(cons.GCONF_LATEST_TILING % glob.screen_index, "g")
        checked_windows_list = self.store.get_checked_windows_list(True)
        tilings.tile_grid(cons.GRID_ROWS,
                          cons.GRID_COLS,
                          checked_windows_list,
                          glob.monitors_areas,
                          self.get_dest_ws())
        self.check_exit_after_tile()

    def tile_custom_1_set(self, *args):
        """The User Wants to Set/Update the Custom Tiling"""
        self.last_custom = 1
        self.glade.customsetdialog.set_title(_("Edit Custom Tile Settings") + " 1")
        response = self.glade.customsetdialog.run()
        self.glade.customsetdialog.hide()
        if response != 1: return
        custom_geoms_str = ""
        for win_geom in self.custom_geoms_1:
            custom_geoms_str += " %s,%s,%s,%s" % (win_geom[0], win_geom[1], win_geom[2], win_geom[3])
        if custom_geoms_str != "": custom_geoms_str = custom_geoms_str[1:]
        self.gconf_client.set_string(cons.GCONF_CUSTOM_1 % glob.screen_index, custom_geoms_str)

    def tile_custom_2_set(self, *args):
        """The User Wants to Set/Update the Custom Tiling"""
        self.last_custom = 2
        self.glade.customsetdialog.set_title(_("Edit Custom Tile Settings") + " 2")
        response = self.glade.customsetdialog.run()
        self.glade.customsetdialog.hide()
        if response != 1: return
        custom_geoms_str = ""
        for win_geom in self.custom_geoms_2:
            custom_geoms_str += " %s,%s,%s,%s" % (win_geom[0], win_geom[1], win_geom[2], win_geom[3])
        if custom_geoms_str != "": custom_geoms_str = custom_geoms_str[1:]
        self.gconf_client.set_string(cons.GCONF_CUSTOM_2 % glob.screen_index, custom_geoms_str)

    def on_drawing_area_draw(self, drawing_area, cairo_context):
        """Drawing Area was Exposed"""
        if self.last_custom == 1:
            if self.custom_geoms_1: self.custom_geoms_draw(self.custom_geoms_1, cairo_context)
        elif self.last_custom == 2:
            if self.custom_geoms_2: self.custom_geoms_draw(self.custom_geoms_2, cairo_context)

    def on_mouse_button_clicked_list(self, widget, event):
        """Catches mouse buttons clicks"""
        if event.button == 3:
            self.ui.get_widget("/ListMenu").popup(None, None, None, None, event.button, event.time)

    def on_button_update_custom_tiling_clicked(self, button):
        """Let's Get Positions and Size of the Flagged Windows"""
        checked_windows_list = self.store.get_checked_windows_list()
        if self.last_custom == 1:
            self.custom_geoms_1 = []
            for win_id in checked_windows_list[0] + checked_windows_list[1]:
                win_geom = support.get_geom(win_id)
                self.custom_geoms_1.append([win_geom[0], win_geom[1], win_geom[2], win_geom[3]])
        elif self.last_custom == 2:
            self.custom_geoms_2 = []
            for win_id in checked_windows_list[0] + checked_windows_list[1]:
                win_geom = support.get_geom(win_id)
                self.custom_geoms_2.append([win_geom[0], win_geom[1], win_geom[2], win_geom[3]])
        self.glade.drawingarea.queue_draw()

    def custom_geoms_draw(self, custom_geoms, cairo_context):
        """Draw Custom Geometries"""
        rgb_idx = 0
        for i, win_geom in enumerate(custom_geoms):
            cairo_context.set_source_rgb(*cons.DRAW_RGBS[rgb_idx])
            cairo_context.rectangle(win_geom[0]/cons.DRAW_SCALE, win_geom[1]/cons.DRAW_SCALE,
                         win_geom[2]/cons.DRAW_SCALE, win_geom[3]/cons.DRAW_SCALE)
            cairo_context.fill()
            cairo_context.set_source_rgb(0, 0, 0)
            cairo_context.set_font_size(13)
            cairo_context.move_to(win_geom[0]/cons.DRAW_SCALE + win_geom[2]/(2*cons.DRAW_SCALE),
                       win_geom[1]/cons.DRAW_SCALE + win_geom[3]/(2*cons.DRAW_SCALE))
            cairo_context.show_text(str(i+1))
            if rgb_idx + 1 < len(cons.DRAW_RGBS): rgb_idx += 1
            else: rgb_idx = 0

    def get_dest_ws(self):
        """Get Destination Desktop"""
        if self.glade.checkbutton_dest_workspace.get_active():
            return int(self.glade.spinbutton_dest_workspace.get_value()-1)
        return -1

    def invert_tiling(self, *args):
        """Invert the order of the latest tiling operation"""
        # get the win_id and win_geom of the latest tiled windows
        latest_tiling_geoms = []
        undo_snap_str = self.gconf_client.get_string(cons.GCONF_UNDO % glob.screen_index)
        if not undo_snap_str: return
        undo_snap_vec = undo_snap_str.split(" ")
        doubleundo_snap_vec = []
        for element in undo_snap_vec:
            win_id, is_maximized, x, y, width, height = element.split(",")
            win_geom = support.get_geom(int(win_id))
            latest_tiling_geoms.append({'win_id': win_id, 'win_geom': win_geom})
        #print "latest_tiling_geoms", latest_tiling_geoms
        # generate the win_id and win_geom of the next tiled windows
        next_tiling_geoms = []
        for i, element in enumerate(latest_tiling_geoms):
            next_tiling_geoms.append({'win_id': element['win_id'],
                                      'win_geom': latest_tiling_geoms[-1-i]['win_geom']})
        #print "next_tiling_geoms", next_tiling_geoms
        # tile the windows
        for element in next_tiling_geoms:
            doubleundo_snap_vec.append(support.get_undo_element_from_win_id(int(element['win_id'])))
            support.moveresize(int(element['win_id']),
                               int(element['win_geom'][0]),
                               int(element['win_geom'][1]),
                               int(element['win_geom'][2]),
                               int(element['win_geom'][3]),
                               self.get_dest_ws())
        if doubleundo_snap_vec:
            support.undo_snap_write(self.gconf_client, doubleundo_snap_vec)
        self.check_exit_after_tile()

    def cycle_tiling(self, *args):
        """Cycle the order of the latest tiling operation"""
        # get the win_id and win_geom of the latest tiled windows
        latest_tiling_geoms = []
        undo_snap_str = self.gconf_client.get_string(cons.GCONF_UNDO % glob.screen_index)
        if not undo_snap_str: return
        undo_snap_vec = undo_snap_str.split(" ")
        doubleundo_snap_vec = []
        for element in undo_snap_vec:
            win_id, is_maximized, x, y, width, height = element.split(",")
            win_geom = support.get_geom(int(win_id))
            latest_tiling_geoms.append({'win_id': win_id, 'win_geom': win_geom})
        #print "latest_tiling_geoms", latest_tiling_geoms
        # generate the win_id and win_geom of the next tiled windows
        next_tiling_geoms = []
        for i, element in enumerate(latest_tiling_geoms):
            next_tiling_geoms.append({'win_id': element['win_id'],
                                      'win_geom': latest_tiling_geoms[(i+1)%len(latest_tiling_geoms)]['win_geom']})
        #print "next_tiling_geoms", next_tiling_geoms
        # tile the windows
        for element in next_tiling_geoms:
            doubleundo_snap_vec.append(support.get_undo_element_from_win_id(int(element['win_id'])))
            support.moveresize(int(element['win_id']),
                               int(element['win_geom'][0]),
                               int(element['win_geom'][1]),
                               int(element['win_geom'][2]),
                               int(element['win_geom'][3]),
                               self.get_dest_ws())
        if doubleundo_snap_vec:
            support.undo_snap_write(self.gconf_client, doubleundo_snap_vec)
        self.check_exit_after_tile()

    def undo_tiling(self, *args):
        """Undo the Latest Tiling Operation"""
        undo_snap_str = self.gconf_client.get_string(cons.GCONF_UNDO % glob.screen_index)
        if not undo_snap_str: return
        undo_snap_vec = undo_snap_str.split(" ")
        doubleundo_snap_vec = []
        for element in undo_snap_vec:
            win_id, is_maximized, x, y, width, height = element.split(",")
            # save current state for eventual undo of the undo
            win_id_int = int(win_id)
            doubleundo_snap_vec.append(support.get_undo_element_from_win_id(win_id_int))
            # proceed with the undo
            if int(is_maximized) == 1: support.maximize(win_id_int)
            else: support.moveresize(win_id_int, int(x), int(y), int(width), int(height), self.get_dest_ws())
        if doubleundo_snap_vec:
            support.undo_snap_write(self.gconf_client, doubleundo_snap_vec)
        self.check_exit_after_tile()

    def tile_custom_1_run(self, *args):
        """Tile N Windows According to the User Defined Tiling"""
        custom_geoms_str = self.gconf_client.get_string(cons.GCONF_CUSTOM_1 % glob.screen_index)
        if not custom_geoms_str:
            support.dialog_info(_("The Custom Tile 1 was Not Set Yet: Click the Menu Item 'Tile->Custom Tile 1 Set'"), self.glade.window)
            return
        self.gconf_client.set_string(cons.GCONF_LATEST_TILING % glob.screen_index, "1")
        custom_geoms_vec = custom_geoms_str.split(" ")
        windows_list = self.store.get_checked_windows_list(True)
        windows_list = windows_list[0] + windows_list[1]
        win_num = 0
        for checked_window in windows_list:
            x, y, width, height = custom_geoms_vec[win_num].split(",")
            support.moveresize(checked_window, int(x), int(y), int(width), int(height), self.get_dest_ws())
            if win_num + 1 < len(custom_geoms_vec): win_num += 1
            else: break
        self.check_exit_after_tile()

    def tile_custom_2_run(self, *args):
        """Tile N Windows According to the User Defined Tiling"""
        custom_geoms_str = self.gconf_client.get_string(cons.GCONF_CUSTOM_2 % glob.screen_index)
        if not custom_geoms_str:
            support.dialog_info(_("The Custom Tile 2 was Not Set Yet: Click the Menu Item 'Tile->Custom Tile 2 Set'"), self.glade.window)
            return
        self.gconf_client.set_string(cons.GCONF_LATEST_TILING % glob.screen_index, "2")
        custom_geoms_vec = custom_geoms_str.split(" ")
        windows_list = self.store.get_checked_windows_list(True)
        windows_list = windows_list[0] + windows_list[1]
        win_num = 0
        for checked_window in windows_list:
            x, y, width, height = custom_geoms_vec[win_num].split(",")
            support.moveresize(checked_window, int(x), int(y), int(width), int(height), self.get_dest_ws())
            if win_num + 1 < len(custom_geoms_vec): win_num += 1
            else: break
        self.check_exit_after_tile()

    def tile_triangle_up(self, *args):
        """Tile 3 Windows in Triangle Up Scheme"""
        self.gconf_client.set_string(cons.GCONF_LATEST_TILING % glob.screen_index, "u")
        checked_windows_list = self.store.get_checked_windows_list(True)
        tilings.tile_triangle_up(checked_windows_list, glob.monitors_areas, self.get_dest_ws())
        self.check_exit_after_tile()

    def tile_triangle_down(self, *args):
        """Tile 3 Windows in Triangle Down Scheme"""
        self.gconf_client.set_string(cons.GCONF_LATEST_TILING % glob.screen_index, "d")
        checked_windows_list = self.store.get_checked_windows_list(True)
        tilings.tile_triangle_down(checked_windows_list, glob.monitors_areas, self.get_dest_ws())
        self.check_exit_after_tile()

    def tile_triangle_left(self, *args):
        """Tile 3 Windows in Triangle Left Scheme"""
        self.gconf_client.set_string(cons.GCONF_LATEST_TILING % glob.screen_index, "l")
        checked_windows_list = self.store.get_checked_windows_list(True)
        tilings.tile_triangle_left(checked_windows_list, glob.monitors_areas, self.get_dest_ws())
        self.check_exit_after_tile()

    def tile_triangle_right(self, *args):
        """Tile 3 Windows in Triangle Right Scheme"""
        self.gconf_client.set_string(cons.GCONF_LATEST_TILING % glob.screen_index, "r")
        checked_windows_list = self.store.get_checked_windows_list(True)
        tilings.tile_triangle_right(checked_windows_list, glob.monitors_areas, self.get_dest_ws())
        self.check_exit_after_tile()

    def show_hide_toolbar(self, menuitem, data=None):
        """Show/Hide the Toolbar"""
        if not self.no_toggling_signals:
            if self.ui.get_widget("/ToolBar").get_property('visible') == True:
                self.ui.get_widget("/ToolBar").hide()
                self.gconf_client.set_string(cons.GCONF_SHOW_TOOLBAR % glob.screen_index, cons.STR_FALSE)
            else:
                self.ui.get_widget("/ToolBar").show()
                self.gconf_client.set_string(cons.GCONF_SHOW_TOOLBAR % glob.screen_index, cons.STR_TRUE)
    
    def check_exit_after_tile(self):
        """Check if the Exit After Tile is Active and Eventually Quit"""
        if self.cmd_line_only: return
        if self.gconf_client.get_string(cons.GCONF_EXIT_AFTER_TILE % glob.screen_index) == cons.STR_TRUE:
            self.quit_application()
    
    def dialog_about(self, menuitem, data=None):
        """Show the About Dialog and hide it when a button is pressed"""
        self.glade.aboutdialog.run()
        self.glade.aboutdialog.hide()
    
    def on_help_menu_item_activated(self, menuitem, data=None):
        """Show the application's Instructions"""
        webbrowser.open("http://www.giuspen.com/x-tile/")
    
    def hide_and_process(self, command_str):
        """Hide the X Tile Window if Visible, then Process the Command"""
        if self.win_on_screen: self.window_hide()
        subprocess.call(command_str, shell=True)
    
    def undo_tiling_all(self, *args):
        """Just Undo the Latest Tiling Operation"""
        self.hide_and_process("x-tile z &")
    
    def invert_tiling_all(self, *args):
        """Invert the Order of the Latest Tiling Operation"""
        self.hide_and_process("x-tile i &")
    
    def cycle_tiling_all(self, *args):
        """Cycle the Order of the Latest Tiling Operation"""
        self.hide_and_process("x-tile y &")
    
    def tile_all_vertically(self, *args):
        """Just tile Vertically all opened windows"""
        self.hide_and_process("x-tile v &")
    
    def tile_all_horizontally(self, *args):
        """Just tile Horizontally all opened windows"""
        self.hide_and_process("x-tile h &")
    
    def tile_all_triangle_up(self, *args):
        """Just tile Triangle Up all opened windows"""
        self.hide_and_process("x-tile u &")
    
    def tile_all_triangle_down(self, *args):
        """Just tile Triangle Down all opened windows"""
        self.hide_and_process("x-tile d &")
    
    def tile_all_triangle_left(self, *args):
        """Just tile Triangle Left all opened windows"""
        self.hide_and_process("x-tile l &")
    
    def tile_all_triangle_right(self, *args):
        """Just tile Triangle Right all opened windows"""
        self.hide_and_process("x-tile r &")
    
    def tile_all_quad(self, *args):
        """Just tile Quad all opened windows"""
        self.hide_and_process("x-tile q &")
    
    def tile_all_grid(self, *args):
        """Just tile Grid all opened windows"""
        self.hide_and_process("x-tile g &")
    
    def tile_all_custom_1(self, *args):
        """Just tile Custom 1 all opened windows"""
        self.hide_and_process("x-tile 1 &")
    
    def tile_all_custom_2(self, *args):
        """Just tile Custom 2 all opened windows"""
        self.hide_and_process("x-tile 2 &")
    
    def maximize_all(self, *args):
        """Maximize all opened windows"""
        self.hide_and_process("x-tile m &")
    
    def unmaximize_all(self, *args):
        """Unmaximize all opened windows"""
        self.hide_and_process("x-tile M &")
    
    def close_all(self, *args):
        """Close all opened windows"""
        self.hide_and_process("x-tile c &")
    
    def dialog_about_all(self, *args):
        """Show the About Dialog and hide it when a button is pressed"""
        glade = GladeWidgetsWrapper(cons.GLADE_PATH + 'x-tile.glade', self)
        glade.aboutdialog.set_version(cons.VERSION)
        glade.aboutdialog.run()
        glade.aboutdialog.destroy()
        del glade
