# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Iskander Shafikov <s00mbre@gmail.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
This file is part of the ycaptcha project hosted at https://github.com/S0mbre/ycaptcha
"""

import numpy as np
import random
import uuid
from PIL import Image, ImageFont, ImageDraw
from dask.distributed import Client as DaskClient

YC_CHARS = '0123456789'
YC_LENGTH = 6
YC_WIDTH = 200
YC_HEIGHT = 60
YC_BACKCOLOR = (255, 255, 255, 255)
YC_BACKCOLOR_TR = (255, 255, 255, 0)
YC_TEXTCOLOR = (0, 0, 0, 255)
YC_SYNTH = {'digit_start_offset': (3, 10), 'transform_times': 3, 'skew_angles': (-10, 10), 'skew_center': (-20, 20), 
            'transform_methods': [Image.AFFINE, Image.PERSPECTIVE], 'transform_resamples': [Image.NEAREST, Image.BILINEAR, Image.BICUBIC],
            'digit_hzoffset': (3.0, 8.0), 'curve_number': 2, 'curve_start_offset': (0.0, 0.2), 'curve_complexity': (2, 10),
            'curve_sections': (1, 4), 'curve_section_offset': 20, 'logo_resize': 0.7,
            'digit_fonts': ['fonts/antquab.ttf', 'fonts/ariblk.ttf', 'fonts/arlrdbd.ttf', 'fonts/impact.ttf'],
            'digit_font_sizes': list(range(48, 55, 1))}
SAVE_FOLDER = '../imgset/synth'

def pascal_row(n, memo={}):
    # This returns the nth row of Pascal's Triangle
    if n in memo: return memo[n]
    result = [1]
    x, numerator = 1, n
    for denominator in range(1, n//2+1):
        # print(numerator,denominator,x)
        x *= numerator
        x /= denominator
        result.append(x)
        numerator -= 1
    if n & 1 == 0:
        # n is even
        result.extend(reversed(result[:-1]))
    else:
        result.extend(reversed(result))
    memo[n] = result
    return result

def make_bezier(xys):
    # xys should be a sequence of 2-tuples (Bezier control points)
    n = len(xys)
    combinations = pascal_row(n-1)
    def bezier(ts):
        # This uses the generalized formula for bezier curves
        # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
        result = []
        for t in ts:
            tpowers = (t**i for i in range(n))
            upowers = reversed([(1-t)**i for i in range(n)])
            coefs = [c*a*b for c, a, b in zip(combinations, tpowers, upowers)]
            result.append(
                tuple(sum([coef*p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
        return result
    return bezier

def ScaleRotateTranslate(image, angle, center=None, new_center=None, scale=None, method=Image.AFFINE, resample=Image.BICUBIC):
    if center is None:
        return image.rotate(angle)
    angle = -angle/180.0 * np.pi
    nx,ny = x,y = center
    sx = sy = 1.0
    if new_center:
        (nx,ny) = new_center
    if scale:
        (sx,sy) = scale
    cosine = np.cos(angle)
    sine = np.sin(angle)
    a = cosine/sx
    b = sine/sx
    c = x-nx*a-ny*b
    d = -sine/sy
    e = cosine/sy
    f = y-nx*d-ny*e
    return image.transform(image.size, method, (a,b,c,d,e,f), resample) # NEAREST gives better results for captcha than BICUBIC

def outline_text(dr, pos, text, fnt, stroke, fill):
    dr.text((pos[0]-1, pos[1]), text, font=fnt, fill=stroke)
    dr.text((pos[0]+1, pos[1]), text, font=fnt, fill=stroke)
    dr.text((pos[0], pos[1]-1), text, font=fnt, fill=stroke)
    dr.text((pos[0], pos[1]+1), text, font=fnt, fill=stroke)
    dr.text(tuple(pos), text, font=fnt, fill=fill)

def synth_captcha(logo_country='en'):
    """
    Yandex Captcha generation steps:
        1. Generate a random array of 6 digits [0...9], e.g. [8, 3, 2, 5, 6, 8]
        2. Use random image font to render each digit (4-5 different fonts):
            - color = black
            - size = random [50...90%] of image height
        3. For each digit, remove the filling, leave contours only
        4. Apply transformations to each digit:
            - distortion (skewed perspective)
            - convolution (wavy contours)
            - slant (inclined left/right)
        4. Make random number [2...10] of gaps in contours, gap length = [2...6%] of contour length
        5. Put digits on image:
            - 1st digit left offset = 1-2 px
            - space between digits = random [-30%...10%] of digit width (negative means overlapping)
            - random top position of digits: [10...50%] of image height, depending on digit height
        6. Make 2 curving lines across the image (from left to right):
            - color = black (as digits)
            - thickness = 1 px
            - left offset (start) / right offset (end) = [0...20%] of image width
            - top offset (start) / bottom offset (end) = [0...100%] of image height
            - wave forms, number and angles of undulations = random (?)
        7. Overlay Yandex logo ("Yandex" for worldwide, "Яндекс" for Russian):
            - position = exactly in top right corner (calculate)
            - size = uniform (calculate)
            - alpha = 100% transparent white color
        8. Add noise to whole image (pixelize) - ??
    """
    
    # generate empty image
    img = Image.new('RGBA', (YC_WIDTH, YC_HEIGHT), color=YC_BACKCOLOR)
    
    digit_offset = [random.randint(1, YC_SYNTH['digit_start_offset'][0]), random.randint(1, YC_SYNTH['digit_start_offset'][1])]
    digit_sz = [0, 0]
    digit_offset = [1, 0]
    
    # Generate a random array of 6 digits
    digits = ''
    for i in range(YC_LENGTH):
        # pick random digit
        digit = random.choice(YC_CHARS)    
        digits += str(digit)
        # pick random font and size (from corresponding lists)
        font = ImageFont.truetype(random.choice(YC_SYNTH['digit_fonts']), random.choice(YC_SYNTH['digit_font_sizes']))
        # calculate the text size in pixels for the selected digit and font
        draw = ImageDraw.Draw(img)
        digit_sz = draw.textsize(digit, font=font)
        # new transparent (alpha) image layer
        txt = Image.new('RGBA', tuple(x + 5 for x in digit_sz), color=YC_BACKCOLOR_TR)
        # canvas
        draw = ImageDraw.Draw(txt)
        # draw digit     
        outline_text(draw, (0, 0), digit, font, YC_TEXTCOLOR, YC_BACKCOLOR_TR)
        # skew several times
        for _ in range(YC_SYNTH['transform_times']):
            txt = ScaleRotateTranslate(txt, random.randint(*YC_SYNTH['skew_angles']), 
                                       new_center=(txt.width / 2 + random.randint(*YC_SYNTH['skew_center']), 
                                                   txt.height / 2 + random.randint(*YC_SYNTH['skew_center'])), 
                                       method=random.choice(YC_SYNTH['transform_methods']),
                                       resample=random.choice(YC_SYNTH['transform_resamples']))       
                
        # make random horizontal offset (in most captchas, the digits overlap)  
        digit_offset[0] += digit_sz[0] + random.randint(
                -digit_sz[0] // YC_SYNTH['digit_hzoffset'][0], 
                -digit_sz[0] // YC_SYNTH['digit_hzoffset'][1])
        # calculate the text size in pixels for the selected digit and font
        #digit_sz = draw.textsize(digit, font=font)
        # make random vertical offset (digit must not get clipped by image boundaries)
        digit_offset[1] = random.randint(1, max(2, YC_HEIGHT - digit_sz[1] - 15))
        # paste digit at random position to background img
        img.paste(txt, tuple(digit_offset), txt)        
          
    # make 2 curves across the combined image
    for _ in range(YC_SYNTH['curve_number']):
        curveimg = Image.new('RGBA', img.size, color=YC_BACKCOLOR_TR)
        draw = ImageDraw.Draw(curveimg)
        ts = [t/img.width for t in range(img.width + 1)]
        xys = [(random.randint(YC_SYNTH['curve_start_offset'][0], img.width * YC_SYNTH['curve_start_offset'][1]), 
                random.randint(0, img.height))]
        j = 0
        for i in range(random.randrange(*YC_SYNTH['curve_complexity'])):
            j += 1
            xys.append((random.randint(xys[j-1][0] + 2, xys[j-1][0] + YC_SYNTH['curve_section_offset']), 
                        random.randint(0, img.height)))
        points = make_bezier(xys)(ts)
        for k in range(random.randrange(*YC_SYNTH['curve_sections'])):
            xys = [xys[-1]]
            j = 0
            for i in range(random.randrange(*YC_SYNTH['curve_complexity'])):
                j += 1
                xys.append((random.randint(xys[j-1][0] + 2, xys[j-1][0] + YC_SYNTH['curve_section_offset']), 
                            random.randint(0, img.height)))
            points.extend(make_bezier(xys)(ts))
        draw.line(points, fill=YC_TEXTCOLOR, joint='curve')
        img.paste(curveimg, (0, 0), curveimg)
        
    # add yandex logo
    logo_file = '../assets/yandex-for-white-background_{}.png'.format(logo_country)
    logo_img = Image.open(logo_file)
    logo_img = logo_img.resize( tuple(int(x * YC_SYNTH['logo_resize']) for x in logo_img.size) )
    img.paste(logo_img, (img.width - logo_img.width, 0), logo_img)
    
    # save final image  
    fname = '{}/{}__{}.png'.format(SAVE_FOLDER, digits, str(uuid.uuid4()).replace('-', ''))
    img.save(fname)
    #img.show()
    return digits, fname

def generate_captchas():
    # start Dask distributed client with 4 processes / 1 thread per process
    client = DaskClient(n_workers=6, threads_per_worker=1)
    # submit future functions to cluster
    futures = []
    for i in range(10000): 
        futures.append(client.submit(synth_captcha, pure=False))
    # execute and compute results (synchronous / blocking!)
    results = client.gather(futures)
    print(len(results))
    # stop & release client
    client.close()


## ******************************************************************************** ##         
if __name__ == '__main__':
    generate_captchas()