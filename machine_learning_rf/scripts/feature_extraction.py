#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 24 18:17:59 2021
Based on: Python for Microscopists: https://www.youtube.com/watch?v=LsuCjbUoI7A

@author: jose
"""


import numpy as np
import cv2
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import minmax_scale
 
def _feature_extraction(img):
    df = pd.DataFrame()
    df['Pixel Value'] = img.reshape(-1)

#Generate Gabor features
    num = 1
    kernels = []
    for theta in range(2):
        theta = theta / 4. * np.pi
        for sigma in (1, 3):
            for lamda in np.arange(0, np.pi, np.pi / 4):
                for gamma in (0.05, 0.5):
#               print(theta, sigma, , lamda, frequency)
                    gabor_label = 'Gabor' + str(num)
#                    print(gabor_label)
                    ksize=9
                    kernel = cv2.getGaborKernel((ksize, ksize), sigma, theta, lamda, gamma, 0, ktype=cv2.CV_32F)    
                    kernels.append(kernel)
                    #Now filter image and add values to new column
                    fimg = cv2.filter2D(img, cv2.CV_8UC3, kernel)
                    filtered_img = fimg.reshape(-1)
                    df[gabor_label] = filtered_img  #Modify this to add new column for each gabor
                    num += 1
########################################
    #Generate OTHER FEATURES and add them to the data frame
    #Feature 3 is canny edge
    edges = cv2.Canny(img, 100,200)
    edges1 = edges.reshape(-1)
    df['Canny Edge'] = edges1

    from skimage.filters import roberts, sobel, scharr, prewitt

    #Feature 4 is Roberts edge
    edge_roberts = roberts(img)
    edge_roberts1 = edge_roberts.reshape(-1)
    df['Roberts'] = edge_roberts1

    #Feature 5 is Sobel
    edge_sobel = sobel(img)
    edge_sobel1 = edge_sobel.reshape(-1)
    df['Sobel'] = edge_sobel1

    #Feature 6 is Scharr
    edge_scharr = scharr(img)
    edge_scharr1 = edge_scharr.reshape(-1)
    df['Scharr'] = edge_scharr1

    #Feature 7 is Prewitt
    edge_prewitt = prewitt(img)
    edge_prewitt1 = edge_prewitt.reshape(-1)
    df['Prewitt'] = edge_prewitt1

    #Feature 8 is Gaussian with sigma=3
    from scipy import ndimage as nd
    gaussian_img = nd.gaussian_filter(img, sigma=3)
    gaussian_img1 = gaussian_img.reshape(-1)
    df['Gaussian s3'] = gaussian_img1

    # #Feature 9 is Gaussian with sigma=7
    gaussian_img2 = nd.gaussian_filter(img, sigma=7)
    gaussian_img3 = gaussian_img2.reshape(-1)
    df['Gaussian s7'] = gaussian_img3

    #Feature 10 is Median with sigma=3
    median_img = nd.median_filter(img, size=3)
    median_img1 = median_img.reshape(-1)
    df['Median s3'] = median_img1

    #Feature 11 is Variance with size=3
    variance_img = nd.generic_filter(img, np.var, size=3)
    variance_img1 = variance_img.reshape(-1)
    df['Variance s3'] = variance_img1
    
    # df = df.dropna(axis=1)
    
    return df

def feature_extraction(img):
    df = pd.DataFrame()
    if img.ndim==3 and img.shape[2]>=2:
        for i in range(img.shape[2]):
            img1 = img[:, :, i]
            df1 = pd.DataFrame()
            # df1['Original Image'] = img1.reshape(-1)
            df1 = _feature_extraction(img1)
            df1.columns = 'ch' + str(i) + ' ' + df1.columns
            df = pd.concat([df, df1], axis=1)
    elif img.ndim==2:
        df['Pixel Value'] = img.reshape(-1)
        df1 = _feature_extraction(img)
        df = pd.concat([df, df1], axis=1)
    else:
        raise Exception("The module works only with grayscale and RGB images!")
    
    return df