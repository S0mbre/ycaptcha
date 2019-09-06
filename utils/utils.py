# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Iskander Shafikov <s00mbre@gmail.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
This file is part of the ycaptcha project hosted at https://github.com/S0mbre/ycaptcha
"""

import sys
import os
import requests
from PIL import Image
from .globalvars import *


def print_err(what, file=sys.stderr):
    print(COLOR_ERR + what, file=file)

def print_dbg(what, file=sys.stdout):    
    print(COLOR_STRESS + what, file=file)
        
def print_help(what, file=sys.stdout):
    print(COLOR_HELP + what, file=file)
    
def get_ip():
    """
    Вернуть текущий внешний IP хоста.
    """
    for service in IPSERVICES:
        try:
            return requests.get(service, proxies=HTTP_PROXIES, timeout=HTTP_TIMEOUT).text
        except:
            pass
    return ''

def walk_dir(root_path, recurse, file_types, file_process_function):
    """
    """
    for d, dirs, files in os.walk(os.path.abspath(root_path)):
        for f in files:
            ext = os.path.splitext(f)[1][1:].lower()
            if (not file_types) or (ext in file_types):
                if file_process_function:
                    if not file_process_function(os.path.join(d, f)): return
        if not recurse: break
    
def convert_img(img_source, dest_dir=None, dest_format='jpg'):
    """
    Converts an image file passed in img_source to a given format passed in dest_format,
    saving the result image in dest_dir (if it's set, otherwise - to the source directory).
    The filename doesn't change, only the extension. 
    """
    img_path = os.path.split(img_source)
    img_base = os.path.splitext(img_path[1])
    img_dest = os.path.join(dest_dir if not dest_dir is None else img_path[0], '{}.{}'.format(img_base[0], dest_format))
    if img_source == img_dest: return img_dest
    print('Converting {}{}...'.format(*img_base), end='\t\t')
    try:
        if dest_format == 'jpg':
            Image.open(img_source).convert('RGB').save(img_dest)
        else:
            Image.open(img_source).save(img_dest)
        print('DONE')
        return img_dest
    except:
        return ''

def convert_images(dir_source, recurse=False, dir_dest=None, imgtypes=('gif',), dest_format='jpg'):
    walk_dir(dir_source, recurse, imgtypes, lambda filein: convert_img(filein, dir_dest, dest_format))