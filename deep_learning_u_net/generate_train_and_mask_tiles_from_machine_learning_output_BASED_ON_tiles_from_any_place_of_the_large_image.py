#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate train and mask tiles from RandomForest (traiditional machine learning algorithm) output
Created on Mon Jun 28 18:58:54 2021

@author: Jose Ramon Martinez Batlle (GH: @geofis)
"""


######################################
# Packages and paths (change global path as desired)
path_global = '/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/'
import sys
sys.path.insert(0, path_global + 'scripts')
import numpy as np
import cv2
from patchify import patchify
# import glob
# from matplotlib import pyplot as plt
import os

######################################
# Prepare training and mask tiles. Within commented cell because
# the processing is already done, no need for repeating.
"""
Using the same train/mask tiles used in the machine learning approach. For 
this, I needed to delete the first 15 cm of the river shore from both the train
and masks tiles, because it was misclassified as riparian vegetation. To do
so, I masked the "mana_whole_padded.tif" from the original folder and the
"segmented_whole_image.tif" using a vector mask called
"gis_mask_for_shore_deletion.gpkg", which is a vector file generated from 
geoprocessing the original mask file ("/home/jose/Documentos/odm/mana_whole/cnn/mask_2.gpkg")
with an interior buffer of 15 cm. To avoid generating GeoTIFF train and masks 
tiles, I used gdalwarp first to create a VRT and afterwards, I used gdal_translate
to convert it to PNG including a WORLDFILE.
# Train tiles
os.system('gdalwarp -s_srs EPSG:32619 -t_srs EPSG:32619 -of VRT -cutline /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/predict/segmented_whole_image/gis_mask_for_shore_deletion.gpkg -cl gis_mask_for_shore /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/original/mana_whole_padded.tif /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/original/mana_whole_padded_shore_deleted.vrt')
t1_start = time()
os.system('gdal_translate -a_srs EPSG:32619 -of PNG -co WORLDFILE=YES /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/original/mana_whole_padded_shore_deleted.vrt /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/original/mana_whole_padded_shore_deleted.png')
os.system('echo "Job finished" | mail -s "Job finished" zoneminderjr@gmail.com')
t1_stop = time()
print("Elapsed time during the whole program in seconds:", t1_stop-t1_start)
# Mask tiles
os.system('gdalwarp -s_srs EPSG:32619 -t_srs EPSG:32619 -of VRT -cutline /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/predict/segmented_whole_image/gis_mask_for_shore_deletion.gpkg -cl gis_mask_for_shore -dstnodata 6 /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/predict/segmented_whole_image/segmented_whole_image.tif /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/predict/segmented_whole_image/segmented_whole_image_shore_deleted.vrt')
t1_start = time()
os.system('gdal_translate -a_srs EPSG:32619 -of PNG -co WORLDFILE=YES /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/predict/segmented_whole_image/segmented_whole_image_shore_deleted.vrt /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/predict/segmented_whole_image/segmented_whole_image_shore_deleted.png')
os.system('echo "Job finished" | mail -s "Job finished" zoneminderjr@gmail.com')
t1_stop = time()
print("Elapsed time during the whole program in seconds:", t1_stop-t1_start)
Almost finally, a majority filter was applied to "segmented_whole_image_shore_deleted.png". I used GRASS GIS r.neighbors addon for this, defining the mode method and applying a 5x5 kernel. I chose GeoTIFF as an output format, and afterwards, I applied the NoData mask to the GeoTIFF and generated a VRT
os.system('gdalwarp -s_srs EPSG:32619 -t_srs EPSG:32619 -of VRT -cutline /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/predict/segmented_whole_image/gis_mask_for_shore_deletion.gpkg -cl gis_mask_for_shore -dstnodata 6 /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/predict/segmented_whole_image/segmented_whole_image_shore_deleted_majority.tif /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/predict/segmented_whole_image/segmented_whole_image_shore_deleted_majority.vrt')
Finally, I converted the VRT file to PNG format, flattening the image with '-expand gray', which also assigns 0 to NoData value
os.system('gdal_translate -a_srs EPSG:32619 -of PNG -co WORLDFILE=YES -expand gray /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/predict/segmented_whole_image/segmented_whole_image_shore_deleted_majority.vrt /media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/predict/segmented_whole_image/segmented_whole_image_shore_deleted_majority.png')
"""

######################################
# Paths
path_ml_img = '/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/'
file_src_train_large = path_ml_img + 'original/mana_whole_padded_shore_deleted.png'

# file_src_masks_large =  path_ml_img + 'predict/segmented_whole_image/segmented_whole_image_shore_deleted_majority.png'
# file_src_masks_large =  path_ml_img + 'predict/segmented_whole_image/segmented_whole_image_shore_deleted.png'

file_src_masks_large_recoded =  path_ml_img + 'predict/segmented_whole_image/segmented_whole_image_shore_deleted_majority_recoded.png'
# file_src_masks_large_recoded =  path_ml_img + 'predict/segmented_whole_image/segmented_whole_image_shore_deleted_recoded.png'

path_dst_images = path_global + 'images/'
path_dst_tiles = path_dst_images + 'train/tiles/'
path_dst_masks = path_dst_images + 'train/masks/'

######################################
# Patches setup. The same layout of patches used for training the machine
# learning was used for this setup
factor=1
overlap = 256
tile_size = 512
PATCH_SIZE = tile_size*factor
STEP = (PATCH_SIZE-overlap)*factor
# The STEP variable is used in the step argument of the patchify function.
# The step argument may be useful to generate tiles with overlap.
# Overlapping is recommended in training tiles, but not in prediction tiles

######################################
# TRAIN: Large train tiles 1024x1024, small patches 128x128, both with 16 px of overlapping
train_arr_large = cv2.imread(file_src_train_large)
IMG_CHANNELS = train_arr_large.shape[2]
prop_nonzeros = 0.75
patches = patchify(train_arr_large, (PATCH_SIZE, PATCH_SIZE, 3), step=STEP)[:, :, 0, :, :, :]
index_x = patches.shape[1]
index_y = patches.shape[0]

tile_index = []
for i in range(0, index_y):
    for j in range(0, index_x):
        img = patches[i, j, :, :, :].astype(np.uint8)
        non_zeros = np.count_nonzero(img)
        threshold = (PATCH_SIZE*PATCH_SIZE*IMG_CHANNELS*prop_nonzeros)
        if(non_zeros > threshold):
            cv2.imwrite(path_dst_tiles + 'tile_' + str(i) + '_' + str(j) + '.tif', img)
            tile_index.append([i, j])

######################################
# MASKS: large mask tiles 1024x1024, small patches 128x128, both with 16 px of overlapping
# mask_arr_large_input = cv2.imread(file_src_masks_large)
# mask_arr_large = cv2.cvtColor(mask_arr_large_input, cv2.COLOR_BGR2GRAY)
# mask_arr_large[mask_arr_large==6]=0
# mask_arr_large[mask_arr_large==7]=6
# mask_arr_large[mask_arr_large==8]=7
# cv2.imwrite(path_ml_img + 'predict/segmented_whole_image/segmented_whole_image_shore_deleted_majority_recoded.png', mask_arr_large)

mask_arr_large_input = cv2.imread(file_src_masks_large_recoded)
mask_arr_large = cv2.cvtColor(mask_arr_large_input, cv2.COLOR_BGR2GRAY)
mask_patches = patchify(mask_arr_large, (PATCH_SIZE, PATCH_SIZE), step=STEP)[:, :, :, :]

for k in tile_index:
    img = mask_patches[k[0], k[1], :, :]
    cv2.imwrite(path_dst_masks + 'tile_' + str(k[0]) + '_' + str(k[1]) + '.tif', img)
