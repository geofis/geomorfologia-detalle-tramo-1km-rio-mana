#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 16:25:07 2021

@author: Jose Ramon Martinez Batlle (GH: @geofis)
"""

import numpy as np

def crop(img, crop_size, anchor='center'):
    h,w = img.shape[:2]
    if(anchor == 'center'):
        start_x = w//2 - (crop_size//2)
        start_y = h//2 - (crop_size//2)
    elif(anchor == 'top-left'):
        start_x = 0
        start_y = 0
    elif(anchor == 'top'):
        start_x = w//2 - (crop_size//2)
        start_y = 0
    elif(anchor == 'top-right'):
        start_x = w - crop_size
        start_y = 0
    elif(anchor == 'right'):
        start_x = w - crop_size
        start_y = h//2 - (crop_size//2)
    elif(anchor == 'bottom-right'):
        start_x = w - crop_size
        start_y = h - crop_size
    elif(anchor == 'bottom'):
        start_x = w//2 - (crop_size//2)
        start_y = h - crop_size
    elif(anchor == 'bottom-left'):
        start_x = 0
        start_y = h - crop_size
    elif(anchor == 'left'):
        start_x = 0
        start_y = h//2 - (crop_size//2)
    return img[start_y:start_y+crop_size, start_x:start_x+crop_size]

def crop_patches(patches_arr, crop_size): #Dimensions allowed: 4. Shape allowed: [H, W, h, w]
    ymax = patches_arr.shape[0]-1
    xmax = patches_arr.shape[1]-1
    cropped_patches = []
    for y in range(patches_arr.shape[0]):
        for x in range(patches_arr.shape[1]):
            if(y == 0 and x == 0):
                cropped = crop(patches_arr[y, x], crop_size = crop_size, anchor = 'top-left')
                # print('top-left')
            elif(y == 0 and 0 < x < xmax):
                cropped = crop(patches_arr[y, x], crop_size = crop_size, anchor = 'top')
                # print('top')
            elif(y == 0 and x == xmax):
                cropped = crop(patches_arr[y, x], crop_size = crop_size, anchor = 'top-right')
                # print('top-right')
            elif(0 < y < ymax and x == xmax):
                cropped = crop(patches_arr[y, x], crop_size = crop_size, anchor = 'right')
                # print('right')
            elif(y == ymax and x == xmax):
                cropped = crop(patches_arr[y, x], crop_size = crop_size, anchor = 'bottom-right')
                # print('bottom-right')
            elif(y == ymax and 0 < x < xmax):
                cropped = crop(patches_arr[y, x], crop_size = crop_size, anchor = 'bottom')
                # print('bottom')
            elif(y == ymax and x == 0):
                cropped = crop(patches_arr[y, x], crop_size = crop_size, anchor = 'bottom-left')
                # print('bottom-left')
            elif(0 < y < ymax and x == 0):
                cropped = crop(patches_arr[y, x], crop_size = crop_size, anchor = 'left')
                # print('left')
            else:
                cropped = crop(patches_arr[y, x], crop_size = crop_size, anchor = 'center')
                # print('center')
            cropped_patches.append(cropped)
    cropped_patches = np.array(cropped_patches)
    cropped_patches_reshaped = np.reshape(cropped_patches, (patches_arr.shape[0], patches_arr.shape[1], crop_size, crop_size))
    return(cropped_patches_reshaped)
