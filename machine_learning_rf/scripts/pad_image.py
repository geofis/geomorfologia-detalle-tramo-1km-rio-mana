#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 18:50:32 2021

@author: Jose Ramon Martinez Batlle (GH: @geofis)
"""

import cv2
import numpy as np
from PIL import Image

def pad_image(src_path, dst_path, tile_size, border_fill = (0, 0, 0)):
    
    # Load image as array
    source_arr = cv2.imread(src_path)
    
    # Dimensions
    ho, wo, do = source_arr.shape
    
    # Padding parameters
    wd = wo + (tile_size- wo % tile_size)
    hd = ho + (tile_size - ho % tile_size)

    # Target array center
    cx = (wd - wo) // 2
    cy = (hd - ho) // 2
    
    # Target array
    padded_arr = np.full((hd, wd, do), border_fill, dtype=np.uint8) # Empty array
    padded_arr[cy:cy+ho, cx:cx+wo] = source_arr # Overlay source over empty array
    
    # Target image
    padded_arr_img = Image.fromarray(padded_arr[:, :, [2,1,0]], 'RGB')
    # padded_arr_img.show()
    cv2.imwrite(dst_path, padded_arr)
    return(padded_arr_img)