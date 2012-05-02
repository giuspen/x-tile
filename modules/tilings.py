# -*- coding: UTF-8 -*-
#
#      core.py
#
#      Copyright 2009-2012
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

import support, cons


def tile_vertically(windows_list, monitors_areas, dws):
    """Tile the Checked Windows Vertically"""
    number_of_windows = len(windows_list[0])
    number_of_windows2 = len(windows_list[1])
    if number_of_windows >= 2:
        tile_vertically_on_area(windows_list[0],
                                monitors_areas[0][0], monitors_areas[0][1],
                                monitors_areas[0][2], monitors_areas[0][3],
                                dws)
    if number_of_windows2 >= 2:
        tile_vertically_on_area(windows_list[1],
                                monitors_areas[1][0], monitors_areas[1][1],
                                monitors_areas[1][2], monitors_areas[1][3],
                                dws)

def tile_horizontally(windows_list, monitors_areas, dws):
    """Tile the Checked Windows Horizontally"""
    number_of_windows = len(windows_list[0])
    number_of_windows2 = len(windows_list[1])
    if number_of_windows >= 2:
        tile_horizontally_on_area(windows_list[0],
                                  monitors_areas[0][0], monitors_areas[0][1],
                                  monitors_areas[0][2], monitors_areas[0][3],
                                  dws)
    if number_of_windows2 >= 2:
        tile_horizontally_on_area(windows_list[1],
                                  monitors_areas[1][0], monitors_areas[1][1],
                                  monitors_areas[1][2], monitors_areas[1][3],
                                  dws)

def tile_quad(windows_list, monitors_areas, dws):
    """Tile the Given Windows Quad"""
    number_of_windows = len(windows_list[0])
    number_of_windows2 = len(windows_list[1])
    if number_of_windows >= 2:
        tile_quad_on_area(windows_list[0],
                          monitors_areas[0][0], monitors_areas[0][1],
                          monitors_areas[0][2], monitors_areas[0][3],
                          dws)
    if number_of_windows2 >= 2:
        tile_quad_on_area(windows_list[1],
                          monitors_areas[1][0], monitors_areas[1][1],
                          monitors_areas[1][2], monitors_areas[1][3],
                          dws)

def tile_grid(rows, cols, windows_list, monitors_areas, dws):
    """Tile the Given Windows in a rows by cols grid"""
    number_of_windows = len(windows_list[0])
    number_of_windows2 = len(windows_list[1])
    if number_of_windows >= 2:
        tile_grid_on_area(rows, cols, windows_list[0],
                          monitors_areas[0][0], monitors_areas[0][1],
                          monitors_areas[0][2], monitors_areas[0][3],
                          dws)
    if number_of_windows2 >= 2:
        tile_grid_on_area(rows, cols, windows_list[1],
                          monitors_areas[1][0], monitors_areas[1][1],
                          monitors_areas[1][2], monitors_areas[1][3],
                          dws)

def tile_triangle_up(windows_list, monitors_areas, dws):
    """Tile 3 Windows in Triangle Up Scheme"""
    number_of_windows = len(windows_list[0])
    number_of_windows2 = len(windows_list[1])
    if number_of_windows >= 2:
        tile_triangle_up_on_area(windows_list[0],
                                 monitors_areas[0][0], monitors_areas[0][1],
                                 monitors_areas[0][2], monitors_areas[0][3],
                                 dws)
    if number_of_windows2 >= 2:
        tile_triangle_up_on_area(windows_list[1],
                                 monitors_areas[1][0], monitors_areas[1][1],
                                 monitors_areas[1][2], monitors_areas[1][3],
                                 dws)

def tile_triangle_down(windows_list, monitors_areas, dws):
    """Tile 3 Windows in Triangle Up Scheme"""
    number_of_windows = len(windows_list[0])
    number_of_windows2 = len(windows_list[1])
    if number_of_windows >= 2:
        tile_triangle_down_on_area(windows_list[0],
                                   monitors_areas[0][0], monitors_areas[0][1],
                                   monitors_areas[0][2], monitors_areas[0][3],
                                   dws)
    if number_of_windows2 >= 2:
        tile_triangle_down_on_area(windows_list[1],
                                   monitors_areas[1][0], monitors_areas[1][1],
                                   monitors_areas[1][2], monitors_areas[1][3],
                                   dws)

def tile_triangle_left(windows_list, monitors_areas, dws):
    """Tile 3 Windows in Triangle Up Scheme"""
    number_of_windows = len(windows_list[0])
    number_of_windows2 = len(windows_list[1])
    if number_of_windows >= 2:
        tile_triangle_left_on_area(windows_list[0],
                                   monitors_areas[0][0], monitors_areas[0][1],
                                   monitors_areas[0][2], monitors_areas[0][3],
                                   dws)
    if number_of_windows2 >= 2:
        tile_triangle_left_on_area(windows_list[1],
                                   monitors_areas[1][0], monitors_areas[1][1],
                                   monitors_areas[1][2], monitors_areas[1][3],
                                   dws)

def tile_triangle_right(windows_list, monitors_areas, dws):
    """Tile 3 Windows in Triangle Up Scheme"""
    number_of_windows = len(windows_list[0])
    number_of_windows2 = len(windows_list[1])
    if number_of_windows >= 2:
        tile_triangle_right_on_area(windows_list[0],
                                    monitors_areas[0][0], monitors_areas[0][1],
                                    monitors_areas[0][2], monitors_areas[0][3],
                                    dws)
    if number_of_windows2 >= 2:
        tile_triangle_right_on_area(windows_list[1],
                                    monitors_areas[1][0], monitors_areas[1][1],
                                    monitors_areas[1][2], monitors_areas[1][3],
                                    dws)

def tile_vertically_on_area(windows_list, x, y, w, h, dws):
    """Tile the Given Windows Vertically on the Given Area"""
    step = (h / len(windows_list))
    win_num = 0
    for checked_window in windows_list:
        support.moveresize(checked_window, x, y+win_num*step, w , step, dws)
        win_num += 1

def tile_horizontally_on_area(windows_list, x, y, w, h, dws):
    """Tile the Given Windows Horizontally on the Given Area"""
    step = (w / len(windows_list))
    win_num = 0
    for checked_window in windows_list:
        support.moveresize(checked_window, x + win_num*step, y, step, h, dws)
        win_num += 1

def tile_quad_on_area(windows_list, x, y, w, h, dws):
    """Tile the Given Windows Quad on the Given Area"""
    if len(windows_list) > 4: windows_list = windows_list[0:4]
    for index,checked_window in enumerate(windows_list):
        if index in [1, 3]: xo = w/2
        else: xo = 0
        if index > 1: yo = h/2
        else: yo = 0
        support.moveresize(checked_window, (x + xo), (y + yo), w/2 , h/2, dws)

def tile_grid_on_area(rows, cols, windows_list, x, y, w, h, dws):
    """Tile the Given Windows Grid on the Given Area"""
    if len(windows_list) > rows*cols: windows_list = windows_list[0:rows*cols]
    step_h = (h / rows)
    step_w = (w / cols)
    for index,checked_window in enumerate(windows_list):
        xo = step_w*(index%cols)
        yo = step_h*(index/cols)
        support.moveresize(checked_window, x+xo, y+yo, step_w , step_h, dws)

def tile_triangle_up_on_area(windows_list, x, y, w, h, dws):
    """Tile 3 Windows in Triangle Up Scheme on the Given Area"""
    if len(windows_list) > 3: windows_list = windows_list[0:3]
    for index,checked_window in enumerate(windows_list):
        if index == 2: xo = w/2
        else: xo = 0
        if index > 0: yo = h/2
        else: yo = 0
        if index == 0: width = w
        else: width = w/2
        support.moveresize(checked_window, (x + xo), (y + yo), width, h/2, dws)

def tile_triangle_down_on_area(windows_list, x, y, w, h, dws):
    """Tile 3 Windows in Triangle Down Scheme on the Given Area"""
    if len(windows_list) > 3: windows_list = windows_list[0:3]
    for index,checked_window in enumerate(windows_list):
        if index == 1: xo = w/2
        else: xo = 0
        if index == 2: yo = h/2
        else: yo = 0
        if index == 2: width = w
        else: width = w/2
        support.moveresize(checked_window, (x + xo), (y + yo), width, h/2, dws)

def tile_triangle_left_on_area(windows_list, x, y, w, h, dws):
    """Tile 3 Windows in Triangle Left Scheme on the Given Area"""
    if len(windows_list) > 3: windows_list = windows_list[0:3]
    for index,checked_window in enumerate(windows_list):
        if index > 0: xo = w/2
        else: xo = 0
        if index == 2: yo = h/2
        else: yo = 0
        if index == 0: height = h
        else: height = h/2
        support.moveresize(checked_window, (x + xo), (y + yo), w/2 , height, dws)

def tile_triangle_right_on_area(windows_list, x, y, w, h, dws):
    """Tile 3 Windows in Triangle Right Scheme on the Given Area"""
    if len(windows_list) > 3: windows_list = windows_list[0:3]
    for index,checked_window in enumerate(windows_list):
        if index == 1: xo = w/2
        else: xo = 0
        if index == 2: yo = h/2
        else: yo = 0
        if index == 1: height = h
        else: height = h/2
        support.moveresize(checked_window, (x + xo), (y + yo), w/2 , height, dws)
