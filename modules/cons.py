# -*- coding: UTF-8 -*-
#
#      cons.py
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

import gtk, os


APP_NAME = "x-tile"
VERSION = "2.0"
if os.path.isdir('glade'):
    GLADE_PATH = "glade/"
    ICON_PLACE = "linux/x-tile.svg"
    LOCALE_PATH = "locale/"
else:
    GLADE_PATH = "/usr/share/x-tile/glade/"
    ICON_PLACE = "/usr/share/pixmaps/x-tile.svg"
    LOCALE_PATH = "/usr/share/locale/"

AVAILABLE_LANGS = ['default', 'de', 'en', 'es_AR', 'fr', 'it', 'ru', 'zh_CN', 'zh_TW']

CMD_LINE_ACTIONS = ["z", "i", "v", "h", "u", "d", "l", "r", "1", "2", "q", "g", "m", "M", "c"]

OVERRIDE_1 = 0
OVERRIDE_2 = 0
X1 = 0
Y1 = 0
W1 = 10
H1 = 10
X2 = 0
Y2 = 0
W2 = 10
H2 = 10
GRID_ROWS = 2
GRID_COLS = 2

WINNAMES_BLACKLIST = ["x-nautilus-desktop", "pcmanfm"]
PROCESSES_BLACKLIST = ["lxpanel"]

STR_TRUE = "True"
STR_FALSE = "False"

DRAW_SCALE = 4
DRAW_RGBS = (
               (1, 0, 0), # red
               (0, 1, 0), # green
               (0, 0, 1), # blue
               (1, 1, 0), # yellow
               (0, 1, 1), # cyan
               (1, 0, 1), # red violet
               (0.5, 0.5, 0.5), # grey
               (1, 1, 1), # white
               #(0, 0, 0), # black
               (1, 0.65, 0), # orange yellow
               (0.25, 1, 0), # yellow green
               (1, 0, 0.25), # red wine
             )

ICONS_SIZE = {1: gtk.ICON_SIZE_MENU, 2: gtk.ICON_SIZE_SMALL_TOOLBAR, 3: gtk.ICON_SIZE_LARGE_TOOLBAR,
              4: gtk.ICON_SIZE_DND, 5: gtk.ICON_SIZE_DIALOG}

ICONS_FILENAMES = [(GLADE_PATH + 'tile-vertically.svg', 'Tile Vertically'),
                   (GLADE_PATH + 'tile-horizontally.svg', 'Tile Horizontally'),
                   (GLADE_PATH + 'tile-quad.svg', 'Tile Quad'),
                   (GLADE_PATH + 'tile-grid.svg', 'Tile Grid'),
                   (GLADE_PATH + 'tile-custom-1-set.svg', 'Custom Set 1'),
                   (GLADE_PATH + 'tile-custom-1-exe.svg', 'Custom Exe 1'),
                   (GLADE_PATH + 'tile-custom-2-set.svg', 'Custom Set 2'),
                   (GLADE_PATH + 'tile-custom-2-exe.svg', 'Custom Exe 2'),
                   (GLADE_PATH + 'tile-triangle-up.svg', 'Tile Triangle Up'),
                   (GLADE_PATH + 'tile-triangle-down.svg', 'Tile Triangle Down'),
                   (GLADE_PATH + 'tile-triangle-left.svg', 'Tile Triangle Left'),
                   (GLADE_PATH + 'tile-triangle-right.svg', 'Tile Triangle Right'),
                   (GLADE_PATH + 'reload-windows-list.svg', 'Reload Windows List'),
                   (GLADE_PATH + 'maximize-checked-windows.svg', 'Maximize Windows'),
                   (GLADE_PATH + 'unmaximize-checked-windows.svg', 'Unmaximize Windows'),
                   (GLADE_PATH + 'close-checked-windows.svg', 'Close Windows'),
                   (GLADE_PATH + 'invert-tiling.svg', 'Invert Tiling'),
                   (GLADE_PATH + 'toolbar.png', 'Toolbar'),
                   (GLADE_PATH + 'quit-app.svg', 'Quit App'),
                   (GLADE_PATH + 'help-contents.svg', 'Help Contents'),
                   (GLADE_PATH + 'checkbox_checked.svg', 'Select All'),
                   (GLADE_PATH + 'checkbox_unchecked.svg', 'Deselect All')]

GCONF_DIR = "/apps/x-tile"
GCONF_LANG = "/apps/x-tile/language"
GCONF_UNDO = "/apps/x-tile/%s/undo"
GCONF_LATEST_TILING = "/apps/x-tile/%s/latest_tiling"
GCONF_CUSTOM_1 = "/apps/x-tile/%s/custom"
GCONF_CUSTOM_2 = "/apps/x-tile/%s/custom_2"
GCONF_EXIT_AFTER_TILE = "/apps/x-tile/%s/exit_after_tile"
GCONF_ONLY_CURR_DESK = "/apps/x-tile/%s/only_curr_desk"
GCONF_NOT_MINIMIZED = "/apps/x-tile/%s/not_minimized"
GCONF_TOOLBAR_ICON_SIZE = "/apps/x-tile/%s/toolbar_icon_size"
GCONF_PROCESS_BLACKLIST = "/apps/x-tile/%s/process_blacklist"
GCONF_PROCESS_WHITELIST = "/apps/x-tile/%s/process_whitelist"
GCONF_WIN_SIZE_W = "/apps/x-tile/%s/win_size_w"
GCONF_WIN_SIZE_H = "/apps/x-tile/%s/win_size_h"
GCONF_WIN_POSITION_X = "/apps/x-tile/%s/win_position_x"
GCONF_WIN_POSITION_Y = "/apps/x-tile/%s/win_position_y"
GCONF_SHOW_TOOLBAR = "/apps/x-tile/%s/show_toolbar"
GCONF_X1 = "/apps/x-tile/%s/x_1"
GCONF_Y1 = "/apps/x-tile/%s/y_1"
GCONF_W1 = "/apps/x-tile/%s/w_1"
GCONF_H1 = "/apps/x-tile/%s/h_1"
GCONF_X2 = "/apps/x-tile/%s/x_2"
GCONF_Y2 = "/apps/x-tile/%s/y_2"
GCONF_W2 = "/apps/x-tile/%s/w_2"
GCONF_H2 = "/apps/x-tile/%s/h_2"
GCONF_OVERRIDE_1 = "/apps/x-tile/%s/override_1"
GCONF_OVERRIDE_2 = "/apps/x-tile/%s/override_2"
GCONF_GRID_ROWS = "/apps/x-tile/%s/grid_rows"
GCONF_GRID_COLS = "/apps/x-tile/%s/grid_cols"
GCONF_SYSTRAY_ENABLE = "/apps/x-tile/%s/systray_enable"
GCONF_SYSTRAY_START = "/apps/x-tile/%s/systray_start"

UI_INFO = """
<ui>
    <menubar name='MenuBar'>
        <menu action='FileMenu'>
            <menuitem action='Filter'/>
            <menuitem action='DefaultSel'/>
            <menuitem action='Reload'/>
            <separator/>
            <menuitem action='QuitApp'/>
            <menuitem action='ExitApp'/>
        </menu>

        <menu action='EditMenu'>
            <menuitem action='Preferences'/>
            <separator/>
            <menuitem action='SelectAll'/>
            <menuitem action='DeselectAll'/>
            <separator/>
        </menu>

        <menu action='RowMenu'>
            <menuitem action='RowUp'/>
            <menuitem action='RowDown'/>
            <separator/>
            <menuitem action='RowDelete'/>
        </menu>

        <menu action='TileMenu'>
            <menuitem action='UnTile'/>
            <menuitem action='InverTile'/>
            <separator/>
            <menuitem action='Vertically'/>
            <menuitem action='Horizontally'/>
            <menuitem action='Grid'/>
            <separator/>
            <menuitem action='Custom1Set'/>
            <menuitem action='Custom2Set'/>
            <menuitem action='Custom1Exe'/>
            <menuitem action='Custom2Exe'/>
            <separator/>
            <menuitem action='TriangleLeft'/>
            <menuitem action='TriangleRight'/>
            <menuitem action='TriangleUp'/>
            <menuitem action='TriangleDown'/>
            <separator/>
            <menuitem action='Quad'/>
            <separator/>
            <menuitem action='Maximize'/>
            <menuitem action='Unmaximize'/>
            <menuitem action='Close'/>
        </menu>

        <menu action='ViewMenu'>
            <menuitem action='ShowHideToolbar'/>
            <separator/>
            <menuitem action='IncreaseToolbarIconsSize'/>
            <menuitem action='DecreaseToolbarIconsSize'/>
        </menu>

        <menu action='HelpMenu'>
            <menuitem action='Help'/>
            <separator/>
            <menuitem action='About'/>
        </menu>
    </menubar>

    <toolbar name='ToolBar'>
        <toolitem action='SelectAll'/>
        <toolitem action='Reload'/>
        <separator/>
        <toolitem action='UnTile'/>
        <toolitem action='InverTile'/>
        <separator/>
        <toolitem action='Vertically'/>
        <toolitem action='Horizontally'/>
        <toolitem action='Grid'/>
        <toolitem action='Custom1Exe'/>
        <toolitem action='Custom2Exe'/>
        <separator/>
        <toolitem action='Maximize'/>
        <toolitem action='Unmaximize'/>
        <toolitem action='Close'/>
    </toolbar>
    
    <popup name='SysTrayMenu'>
        <menuitem action='ExitApp'/>
        <separator/>
        <menuitem action='All_About'/>
        <separator/>
        <menuitem action='All_C'/>
        <menuitem action='All_U'/>
        <menuitem action='All_M'/>
        <separator/>
        <menuitem action='All_4'/>
        <separator/>
        <menuitem action='All_TD'/>
        <menuitem action='All_TU'/>
        <menuitem action='All_TR'/>
        <menuitem action='All_TL'/>
        <separator/>
        <menuitem action='All_C2'/>
        <menuitem action='All_C1'/>
        <separator/>
        <menuitem action='All_G'/>
        <menuitem action='All_H'/>
        <menuitem action='All_V'/>
        <separator/>
        <menuitem action='All_Invert'/>
        <menuitem action='All_Undo'/>
    </popup>
    
    <popup name='ListMenu'>
        <menuitem action='RowUp'/>
        <menuitem action='RowDown'/>
        <separator/>
        <menuitem action='RowDelete'/>
    </popup>
</ui>
"""

def get_entries(inst):
    """Returns the Menu Entries Given the Class Instance"""
    return [
    # name, stock id, label
    ( "FileMenu", None, _("_File") ),
    ( "EditMenu", None, _("_Edit") ),
    ( "RowMenu", None, _("_Row") ),
    ( "TileMenu", None, _("_Tile") ),
    ( "ViewMenu", None, _("_View") ),
    ( "HelpMenu", None, _("_Help") ),
    # name, stock id, label, accelerator, tooltip, callback
    ( "Filter", "gtk-properties", _("_Filter"), "<control>F", _("Filter Rows"), inst.dialog_filter),
    ( "DefaultSel", "gtk-properties", _("Selected by _Default"), "<control>D", _("Rows to be Selected by Default"), inst.dialog_selected_by_default),
    ( "Reload", "Reload Windows List", _("_Reload"), "F5", _("Reload the Windows List"), inst.reload_windows_list),
    ( "QuitApp", "Quit App", _("_Quit"), "<control>Q", _("Quit the Application"), inst.quit_application),
    ( "ExitApp", "Quit App", _("_Exit X Tile"), "<control><shift>Q", _("Exit from X Tile"), inst.quit_application_totally),
    ( "Preferences", "gtk-preferences", _("_Preferences"), "<control><alt>P", _("Open the Preferences Window"), inst.dialog_preferences),
    ( "SelectAll", "Select All", _("Select _All"), "<control>A", _("Select All the Windows in the List"), inst.flag_all_rows),
    ( "DeselectAll", "Deselect All", _("Deselect A_ll"), "<control><shift>A", _("Deselect All the Windows in the List"), inst.unflag_all_rows),
    ( "Vertically", "Tile Vertically", _("Tile _Vertically"), "<control>V", _("Tile Vertically The Checked Windows"), inst.tile_vertically),
    ( "Horizontally", "Tile Horizontally", _("Tile _Horizontally"), "<control>H", _("Tile Horizontally The Checked Windows"), inst.tile_horizontally),
    ( "TriangleUp", "Tile Triangle Up", _("_Triangle Up"), "<control>Up", _("Tile Triangle Up The Checked Windows"), inst.tile_triangle_up),
    ( "TriangleDown", "Tile Triangle Down", _("Triangle _Down"), "<control>Down", _("Tile Triangle Down The Checked Windows"), inst.tile_triangle_down),
    ( "TriangleLeft", "Tile Triangle Left", _("Triangle _Left"), "<control>Left", _("Tile Triangle Left The Checked Windows"), inst.tile_triangle_left),
    ( "TriangleRight", "Tile Triangle Right", _("Triangle _Right"), "<control>Right", _("Tile Triangle Right The Checked Windows"), inst.tile_triangle_right),
    ( "Quad", "Tile Quad", _("Tile _Quad"), "<control>4", _("Tile into 4 quadrants The Checked Windows"), inst.tile_quad),
    ( "Grid", "Tile Grid", _("Tile _Grid"), "<control>G", _("Tile into an Arbitrary Grid The Checked Windows"), inst.dialog_grid),
    ( "Custom1Set", "Custom Set 1", _("Custom Tile 1 _Set"), "<alt>1", _("Edit Custom Tile 1 Settings"), inst.tile_custom_1_set),
    ( "Custom1Exe", "Custom Exe 1", _("Custom Tile _1 Run"), "<control>1", _("Execute Custom Tile 1"), inst.tile_custom_1_run),
    ( "Custom2Set", "Custom Set 2", _("Custom Tile 2 S_et"), "<alt>2", _("Edit Custom Tile 2 Settings"), inst.tile_custom_2_set),
    ( "Custom2Exe", "Custom Exe 2", _("Custom Tile _2 Run"), "<control>2", _("Execute Custom Tile 2"), inst.tile_custom_2_run),
    ( "UnTile", "gtk-undo", _("U_ndo Tiling"), "<control>Z", _("Undo the Latest Tiling Operation"), inst.undo_tiling),
    ( "InverTile", "Invert Tiling", _("_Invert Tiling Order"), "<control>I", _("Invert the Order of the Latest Tiling Operation"), inst.invert_tiling),
    ( "Maximize", "Maximize Windows", _("_Maximize Windows"), "<control>M", _("Maximize The Checked Windows"), inst.maximize_checked_windows),
    ( "Unmaximize", "Unmaximize Windows", _("_Unmaximize Windows"), "<control>U", _("Unmaximize The Checked Windows"), inst.unmaximize_checked_windows),
    ( "Close", "Close Windows", _("_Close Windows"), "<control>C", _("Close The Checked Windows"), inst.close_checked_windows),
    ( "RowUp", "gtk-go-up", _("Move _Up"), "<alt>Up", _("Move the Selected Row Up"), inst.on_button_row_up_clicked),
    ( "RowDown", "gtk-go-down", _("Move _Down"), "<alt>Down", _("Move the Selected Row Down"), inst.on_button_row_down_clicked),
    ( "RowDelete", "gtk-remove", _("_Remove"), "Delete", _("Remove the Selected Row"), inst.on_button_row_delete_clicked),
    ( "ShowHideToolbar", "Toolbar", _("Show/Hide _Toolbar"), None, _("Toggle Show/Hide Toolbar"), inst.show_hide_toolbar),
    ( "IncreaseToolbarIconsSize", "gtk-add", _("_Increase Toolbar Icons Size"), None, _("Increase the Size of the Toolbar Icons"), inst.toolbar_icons_size_increase),
    ( "DecreaseToolbarIconsSize", "gtk-remove", _("_Decrease Toolbar Icons Size"), None, _("Decrease the Size of the Toolbar Icons"), inst.toolbar_icons_size_decrease),
    ( "Help", "Help Contents", _("_Help"), None, _("X Tile Project Home Page"), inst.on_help_menu_item_activated),
    ( "About", "gtk-about", _("_About"), None, _("About X Tile"), inst.dialog_about),
    ( "All_About", "gtk-about", _("_About"), None, _("_About"), inst.dialog_about_all),
    ( "All_C", "Close Windows", _("Close All"), None, _("Close All"), inst.close_all),
    ( "All_U", "Unmaximize Windows", _("_Unmaximize All"), None, _("_Unmaximize All"), inst.unmaximize_all),
    ( "All_M", "Maximize Windows", _("_Maximize All"), None, _("_Maximize All"), inst.maximize_all),
    ( "All_4", "Tile Quad", _("Tile All _Quad"), None, _("Tile All _Quad"), inst.tile_all_quad),
    ( "All_TD", "Tile Triangle Down", _("Tile All Triangle _Down"), None, _("Tile All Triangle _Down"), inst.tile_all_triangle_down),
    ( "All_TU", "Tile Triangle Up", _("Tile All Triangle _Up"), None, _("Tile All Triangle _Up"), inst.tile_all_triangle_up),
    ( "All_TR", "Tile Triangle Right", _("Tile All Triangle _Right"), None, _("Tile All Triangle _Right"), inst.tile_all_triangle_right),
    ( "All_TL", "Tile Triangle Left", _("Tile All Triangle _Left"), None, _("Tile All Triangle _Left"), inst.tile_all_triangle_left),
    ( "All_C2", "Custom Exe 2", _("Tile All Custom _2"), None, _("Tile All Custom _2"), inst.tile_all_custom_2),
    ( "All_C1", "Custom Exe 1", _("Tile All Custom _1"), None, _("Tile All Custom _1"), inst.tile_all_custom_1),
    ( "All_G", "Tile Grid", _("Tile All _Grid"), None, _("Tile All _Grid"), inst.tile_all_grid),
    ( "All_H", "Tile Horizontally", _("Tile All _Horizontally"), None, _("Tile All _Horizontally"), inst.tile_all_horizontally),
    ( "All_V", "Tile Vertically", _("Tile All _Vertically"), None, _("Tile All _Vertically"), inst.tile_all_vertically),
    ( "All_Invert", "Invert Tiling", _("_Invert Tiling Order"), None, _("_Invert Tiling Order"), inst.invert_tiling_all),
    ( "All_Undo", "gtk-undo", _("U_ndo Tiling"), None, _("U_ndo Tiling"), inst.undo_tiling_all),
    ]

HELP_TEXT = """

NAME
   X Tile - Tile the Windows upon your Desktop

SYNOPSIS
   x-tile OPTION [grid rows] [grid columns]

DESCRIPTION
   This manual page briefly documents the command line arguments

OPTIONS

   w => open the x-tile main window without using the panel

   z => undo the latest tiling operation

   v => tile all opened windows vertically

   h => tile all opened windows horizontally

   u => tile all opened windows triangle-up

   d => tile all opened windows triangle-down

   l => tile all opened windows triangle-left

   r => tile all opened windows triangle-right

   q => quad tile all opened windows

   g => tile all opened windows in a grid having number of rows and columns the given arguments

   1 => custom tile 1 all opened windows

   2 => custom tile 2 all opened windows

   i => invert the order of the latest tiling operation

   m => maximize all opened windows

   M => unmaximize all opened windows

   c => close all opened windows

SEE ALSO
   http://www.giuspen.com/x-tile

AUTHORS
   Giuseppe Penone (aka giuspen) and Chris Camacho (aka Chris_C)

"""
