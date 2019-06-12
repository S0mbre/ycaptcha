# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Iskander Shafikov <s00mbre@gmail.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
This file is part of the ycaptcha project hosted at https://github.com/S0mbre/ycaptcha
"""

import os
import requests
import xml.etree.ElementTree as ET
import hashlib
from .utils import *


REQ_HEADERS = {'Content-Type': 'text/xhtml+xml; charset=UTF-8', 
               'Accept': 'application/xhtml+xml,application/xml', 
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
               'Accept-Charset': 'utf-8',
               'Accept-Language': 'ru,en-us',
               'Connection': 'close', 
               'X-Real-Ip': get_ip()}
SAMPLE_CAPTCHA_QUERY = 'e48a2b93de1740f48f6de0d45dc4192a'
IMAGE_TYPES = {'gif': '.gif', 'jpeg': '.jpg', 'png': '.png', 'jpg': '.jpg'}

def get_node(node, nodename, default=''):
    nd = node.find(nodename)
    return nd.text if not nd is None else default

def get_sample_captcha(user, apikey, domain='com', only_image=True):
    try:
        q = 'https://yandex.{}/search/xml?&query={}&user={}&key={}&showmecaptcha=yes'.format(domain, SAMPLE_CAPTCHA_QUERY, user, apikey)
        resp = requests.get(q, proxies=HTTP_PROXIES, timeout=HTTP_TIMEOUT, headers=REQ_HEADERS) 
        if resp.status_code != 200:
            raise Exception('Result of query "{}" cannot be retrieved, HTTP Error = {}'.format(q, resp.status_code))
            
        #print_dbg('SERVER RETURNED:\n' + resp.text)  
        if not only_image: return resp.text
        tree = ET.fromstring(resp.text)            
        return get_node(tree, './captcha-img-url')
        
    except Exception as err:
        print_err(str(err))
        return None

def download_sample_captchas(user, apikey, domain='com', ncap=1, directory=None, cback=None):
    """
    Downloads requested number of Yandex captchas as [GIF] images to indicated directory.
    PARAMS:
        - user [str]: Yandex XML username
        - apikey [str]: Yandex XML API key
        - domain [str]: either 'ru' (Russian Yandex) or 'com' (worldwide Yandex)
        - ncap [int]: how many captchas to retrieve (default = 1)
        - directory [str]: the save directory; if None, the current dir's "imgset" folder will be used
        - cback [object]: callback function returning the original downloaded file path or a new one; 
                          if the return results evaluates to False (e.g. empty string), downloading will stop
    """
    root = directory if not directory is None else os.path.abspath(IMG_DIRECTORY)
    if not os.path.isdir(root): os.makedirs(root)
    
    out_paths = []
    for i in range(ncap):
        url = get_sample_captcha(user, apikey, domain)
        if not url:
            print_err('Error downloading captcha! No image URL!')
            continue
        try:
            res = requests.get(url, proxies=HTTP_PROXIES, timeout=HTTP_TIMEOUT, headers=REQ_HEADERS)
            if res.status_code != 200:
                print_err('Error downloading captcha! HTTP Error = {}'.format(res.status_code))
                continue
            ftype = res.headers['Content-Type'].split('/')[-1].split(';')[0] if 'Content-Type' in res.headers else 'gif'
            if not ftype in IMAGE_TYPES:
                print_err('Wrong image format: ' + ftype)
                continue
            fname = hashlib.md5(url.encode()).hexdigest() + IMAGE_TYPES[ftype]
            fpath = os.path.join(root, fname)
                        
            with open(fpath, 'wb') as f:
                f.write(res.content)
            #print_dbg('SAVED:\t' + os.path.basename(fname))
            
            if not cback is None:
                fpath = cback(i, fpath)
                if not fpath: break
            
            out_paths.append(fpath)           
            
            
        except Exception as err:
            print_err(str(err))
            continue
        
    return out_paths
            
    
