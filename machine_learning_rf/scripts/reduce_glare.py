#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 21:44:11 2021

@author: Jose Ramon Martinez Batlle (GH: @geofis)

Based on: https://stackoverflow.com/a/65383303
"""

import cv2
import numpy as np

def reduce_glare(src_img_path, dst_img_path):
    # clahefilter = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16,16))
    img = cv2.imread(src_img_path)
    
    # Gray
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # grayimg = gray
    
    # Glare
    # GLARE_MIN = np.array([0, 0, 50],np.uint8)
    # GLARE_MAX = np.array([0, 0, 225],np.uint8)
    
    #HSV
    # hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # frame_threshed = cv2.inRange(hsv_img, GLARE_MIN, GLARE_MAX)
    
    #INPAINT
    # mask1 = cv2.threshold(grayimg , 220, 255, cv2.THRESH_BINARY)[1]
    # result1 = cv2.inpaint(img, mask1, 0.1, cv2.INPAINT_TELEA) 
    
    #CLAHE
    # claheCorrecttedFrame = clahefilter.apply(grayimg)
    
    #COLOR 
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    lab_planes = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
    lab_planes[0] = clahe.apply(lab_planes[0])
    lab = cv2.merge(lab_planes)
    clahe_bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    #INPAINT + HSV
    # result = cv2.inpaint(img, frame_threshed, 0.1, cv2.INPAINT_TELEA) 
    
    #INPAINT + CLAHE
    grayimg1 = cv2.cvtColor(clahe_bgr, cv2.COLOR_BGR2GRAY)
    mask2 = cv2.threshold(grayimg1 , 220, 255, cv2.THRESH_BINARY)[1]
    result2 = cv2.inpaint(img, mask2, 0.1, cv2.INPAINT_TELEA) 
    
    #HSV+ INPAINT + CLAHE
    # lab1 = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
    # lab_planes1 = cv2.split(lab1)
    # clahe1 = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    # lab_planes1[0] = clahe1.apply(lab_planes1[0])
    # lab1 = cv2.merge(lab_planes1)
    # clahe_bgr1 = cv2.cvtColor(lab1, cv2.COLOR_LAB2BGR)
    
    cv2.imwrite(dst_img_path, result2)
