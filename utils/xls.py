# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Iskander Shafikov <s00mbre@gmail.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
This file is part of the ycaptcha project hosted at https://github.com/S0mbre/ycaptcha
"""

import xlsxwriter
from .utils import *


def images_to_excel(imgdir, xlsfile, nfiles=-1, imgtypes=('jpg',), recurse=False, scale=1.0):
    """
    https://xlsxwriter.readthedocs.io/example_images.html
    """
        
    wb = xlsxwriter.Workbook(xlsfile)
    ws = wb.add_worksheet()
    ws.set_column('A:A', 80)
    ws.set_column('B:B', 30)
    row = 1
    
    def write_img(imgfile):
        nonlocal ws
        nonlocal row
        ws.set_row(row - 1, 50)
        ws.write('A{}'.format(row), imgfile)
        ws.insert_image('B{}'.format(row), imgfile, None if scale == 1.0 else {'x_scale': scale, 'y_scale': scale})
        row += 1
        return nfiles == -1 or row < nfiles
    
    walk_dir(imgdir, recurse, imgtypes, write_img)
    
    wb.close()
            
    
