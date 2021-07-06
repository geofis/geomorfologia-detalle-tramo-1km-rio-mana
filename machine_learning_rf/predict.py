#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 18:00:28 2021

@author: Jose Ramon Martinez Batlle (GH: @geofis)
"""


######################################
# Packages
global_path = '/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/'
import sys
sys.path.insert(0, global_path + 'scripts')
import os
import numpy as np
import cv2
import scripts.feature_extraction as fe
from patchify import patchify, unpatchify
# import glob
# from matplotlib import pyplot as plt
from time import time
import pickle

######################################
# Input image
tile_size = 1024
path_to_images = global_path + 'images/'
padded_image_path = path_to_images + 'original/mana_whole_padded.tif'
padded_arr = cv2.imread(padded_image_path)

######################################
# Patchify
# Generate patches for training
factor=1
PATCH_SIZE=tile_size*factor
# The STEP variable is used in the step argument of the patchify function.
# The step argument may be useful to generate tiles with overlap.
# Overlapping is recommended in training tiles, but not in prediction tiles
patches = patchify(padded_arr, (PATCH_SIZE, PATCH_SIZE, 3), step=PATCH_SIZE)[:, :, 0, :, :, :]

######################################
# Test the model on future datasets
model_filename = global_path + "model/model"
loaded_model = pickle.load(open(model_filename, 'rb'))

######################################
# Predict
# Whole image in patches
t1_start = time()
predicted_patches = []
for i in range(patches.shape[0]):
    for j in range(patches.shape[1]):
        print(i,j)
        single_patch = patches[i,j,:,:,:]
        X = fe.feature_extraction(single_patch)
        result = loaded_model.predict(X)
        segmented = result.reshape(single_patch.shape[:2])
        predicted_patches.append(segmented)
os.system('echo "Job finished" | mail -s "Job finished" zoneminderjr@gmail.com')
t1_stop = time()
print("Elapsed time during the whole program in seconds:", t1_stop-t1_start)
# Elapsed time during the whole program in seconds: 19612.19780230522

######################################
# Unpatchify and save
predicted_patches_arr = np.array(predicted_patches)
predicted_patches_reshaped = np.reshape(predicted_patches_arr, (patches.shape[0], patches.shape[1], PATCH_SIZE, PATCH_SIZE) )
reconstructed_image = unpatchify(predicted_patches_reshaped, padded_arr.shape[:2])
cv2.imwrite(path_to_images + 'predict/segmented_whole_image/segmented_whole_image.tiff', reconstructed_image)

######################################
# Summaries
import collections
class_summary = collections.Counter(reconstructed_image.reshape(-1))
dict(sorted(class_summary.items(), key=lambda item: item[0]))
"""
{1: 1151184,
 2: 11676435,
 3: 2368475,
 4: 4454609,
 5: 4551889,
 6: 460205246,
 7: 2001819,
 8: 1178183}
"""
dict(sorted(class_summary.items(), key=lambda item: item[1]))
"""
{1: 1151184,
 8: 1178183,
 7: 2001819,
 3: 2368475,
 4: 4454609,
 5: 4551889,
 2: 11676435,
 6: 460205246}
"""


######################################
# BONUS: TIPS AND TRICKS TO RECONSTRUCT IMAGE AND GENERATE WORLDFILE (E.G., tfw)
# FROM PATCHES GENERATED USING THE STEP ARGUMENT
"""
predicted_patches = []
for i in range(patches.shape[0]):
    for j in range(patches.shape[1]):
        print(i,j)
        single_patch = patches[i,j,:,:,:]
        X = fe.feature_extraction(single_patch)
        result = loaded_model.predict(X)
        segmented = result.reshape(single_patch.shape[:2])
        predicted_patches.append(segmented)
os.system('echo "Job finished" | mail -s "Job finished" zoneminderjr@gmail.com')

predicted_patches_interior=[]
for i in range(len(predicted_patches)):
    interior=predicted_patches[i][(PATCH_SIZE-STEP)//2:PATCH_SIZE-(PATCH_SIZE-STEP)//2,(PATCH_SIZE-STEP)//2:PATCH_SIZE-(PATCH_SIZE-STEP)//2]
    predicted_patches_interior.append(interior)
predicted_patches_reshaped = np.reshape(predicted_patches_interior, (patches.shape[0], patches.shape[1], STEP, STEP))
reconstructed_image = unpatchify(predicted_patches_reshaped, (15120,31248))
cv2.imwrite('images/rf/segmented_whole_image/segmented_whole_image.tiff', reconstructed_image)
"""

######################################
# Attempt to predict over the whole image (never finished at all, allocation error)
""""
large_file = 'images/original/mana_whole_padded.tif'
large_img = cv2.imread(large_file)
X = fe.feature_extraction(large_img)
os.system('echo "Job finished" | mail -s "Job finished" zoneminderjr@gmail.com')
result = loaded_model.predict(X)
segmented = result.reshape(large_img.shape[:2])
plt.imsave('images/test-image-2_segmented.tiff', segmented, cmap ='gray')
"""