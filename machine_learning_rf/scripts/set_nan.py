#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 18:50:32 2021

@author: Jose Ramon Martinez Batlle (GH: @geofis)
"""

import cv2
import numpy as np
from PIL import Image

def set_nan(src_path, dst_path):
    
    # Load image as array
    source_arr = cv2.imread(src_path)
    
    # Convert to float
    non_nan_img = np.float32(source_arr)
    
    non_nan_img[non_nan_img == 0] = np.nan
    print('The number of non-zero and non-nan values is', np.count_nonzero(~np.isnan(non_nan_img)))
        
    # Target image
    # source_arr_img = Image.fromarray(source_arr[:, :, [2,1,0]], 'RGB')
    # padded_arr_img.show()
    cv2.imwrite(dst_path, non_nan_img)
    return(non_nan_img)