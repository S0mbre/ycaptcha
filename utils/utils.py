# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Iskander Shafikov <s00mbre@gmail.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
This file is part of the ycaptcha project hosted at https://github.com/S0mbre/ycaptcha
"""

import sys
import os
import glob
import requests
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
            if not file_types or ext in file_types:
                if file_process_function:
                    if not file_process_function(os.path.join(d, f)): return
        if not recurse: break