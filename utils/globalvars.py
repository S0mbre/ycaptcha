# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Iskander Shafikov <s00mbre@gmail.com>
# GNU General Public License v3.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
This file is part of the ycaptcha project hosted at https://github.com/S0mbre/ycaptcha

This module contains the global variables used in any other modules.
"""

# debug messages
DEBUGGING = True

# default encoding
ENCODING = 'utf-8'

# for colorama colored console output
COLORED_OUTPUT = True           # will work only if colorama is installed; set to False to switch off colored output
COLOR_INITIATED = False
COLOR_PROMPT = ''
COLOR_HELP = ''
COLOR_ERR = ''
COLOR_STRESS = ''
COLOR_BRIGHT = ''

if COLORED_OUTPUT and not COLOR_INITIATED:
    try:
        import colorama
        colorama.init(autoreset=True)
        COLOR_PROMPT = colorama.Fore.GREEN
        COLOR_HELP = colorama.Fore.YELLOW
        COLOR_ERR = colorama.Fore.RED
        COLOR_STRESS = colorama.Fore.CYAN
        COLOR_BRIGHT = colorama.Style.BRIGHT
        COLOR_INITIATED = True
    except ImportError:
        COLORED_OUTPUT = False
        
IPSERVICES = ['https://api.ipify.org', 'https://ident.me', 'https://ipecho.net/plain', 'https://myexternalip.com/raw']
HTTP_PROXIES = None # or dict, e.g. {'http': 'http://ip:port', 'https': 'http://ip:port'}
HTTP_TIMEOUT = 5                 # ожидание соединения и ответа (сек.) None = вечно

IMG_DIRECTORY = 'imgset/original'