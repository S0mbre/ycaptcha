# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Iskander Shafikov <s00mbre@gmail.com>
# GNU General Public License v3.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
This file is part of the ycaptcha project hosted at https://github.com/S0mbre/ycaptcha

This module provides a command-line interface (CLI).

Use like so:
    python ycap.py run
"""

from utils.clibase import *
from utils.download import download_sample_captchas
from utils.xls import images_to_excel

## ******************************************************************************** ## 
                
class CLI(CLIBase):
    
    def __init__(self, splash=True):
        super().__init__()
        self.splash = splash
        
    #----- NON-COMMAND METHODS ------#
    
    def print_splash(self):
        with open('assets/splash', 'r') as f:
            print(COLOR_STRESS + f.read())
            
    def beforeRun(self):        
        super().beforeRun()
        try:
            if getattr(self, 'splash'): self.print_splash()
        except AttributeError:
            pass
        
    def beforeQuit(self):
        super().beforeQuit()
        print(COLOR_STRESS + 'QUITTING APP...')
           
    #----- COMMAND METHODS ------#    
    
    def cmd_download(self, user, apikey, domain='com', ncap=1, imgdir=None):
        """
        Downloads requested number of Yandex captchas as [GIF] images to indicated directory.
        PARAMS:
            - user [str]: Yandex XML username
            - apikey [str]: Yandex XML API key
            - domain [str]: OPTIONAL: either 'ru' (Russian Yandex) or 'com' (worldwide Yandex)
            - ncap [int]: OPTIONAL: how many captchas to retrieve (default = 1)
            - directory [str]: OPTIONAL: the save directory; if None, the current dir's "imgset" folder will be used
        RETURNS:
            Status text.
        """
        
        def download_callback(i, root, filename):
            print(COLOR_BRIGHT + '{}:\t{} >> {}...'.format((i+1), filename, root))
            return True        

        images = download_sample_captchas(user, apikey, domain, ncap, imgdir, download_callback)
        return 'Saved {} files to {}'.format(len(images), imgdir if not imgdir is None else IMG_DIRECTORY)
    
    def cmd_xls(self, xlsfile=None, imgdir=None, nfiles=-1):
        """
        Copies saved images to Excel spreadsheet (for storing captcha values).
        """
        images_to_excel(imgdir if not imgdir is None else IMG_DIRECTORY, 
                        xlsfile if not xlsfile is None else IMG_DIRECTORY + '/table.xlsx', nfiles)
                
            
## ******************************************************************************** ##             
    
def main():    
    fire.Fire(CLI, 'run')

## ******************************************************************************** ##    
       
if __name__ == '__main__':
    main()