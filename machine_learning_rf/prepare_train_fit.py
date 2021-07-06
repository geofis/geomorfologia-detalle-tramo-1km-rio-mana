#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 18:58:54 2021

@author: Jose Ramon Martinez Batlle (GH: @geofis)
"""


######################################
# Packages and paths (change global path as desired)
global_path = '/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/'
import sys
sys.path.insert(0, global_path + 'scripts')
import os
import numpy as np
# import pad_image as pi #Commented, image alredy padded. Source of script: https://stackoverflow.com/a/49375740
import cv2
import pandas as pd
import feature_extraction as fe
# import reduce_glare as rg #Commented because seemed to have little efect on glare
# from patchify import patchify, unpatchify #Comment out if patchifying is needed
import glob
from matplotlib import pyplot as plt
import pickle
from time import time

######################################
# Pad the image
# Padded image is necessary to generate training and predict tiles
# across the whole image
tile_size = 1024
path_to_images = global_path + 'images/'
orig_img_path = path_to_images + 'original/mana_whole.tif'
padded_image_path = path_to_images + 'original/mana_whole_padded.tif'
# Commented lines, image already padded
# padded_image = pi.pad_image(
#     src_path=orig_img_path,
#     dst_path=padded_image_path,
#     tile_size=tile_size)
# Edit the TFW file this way
# ULX coordinate - ((Number of new cells to the west - 1) * resolution)
# ULY coordinate + ((Number of new cells to the north - 1) * resolution)
# padded_image.show()

######################################
# Reduce glare. COMMENTED, no useful output generated from this process
# glarered_image_path = path_to_images + 'original/mana_whole_padded_glarereduced.tif'
# rg.reduce_glare(src_img_path=padded_image_path, dst_img_path=glarered_image_path)

# Read again the padded or the glareless-padded image
padded_arr = cv2.imread(padded_image_path)

######################################
# Generate patches for training
# factor=1
# PATCH_SIZE=tile_size*factor
# STEP=(tile_size-16)*factor
# The STEP variable is used in the step argument of the patchify function.
# The step argument may be useful to generate tiles with overlap.
# Overlapping is recommended in training tiles, but not in prediction tiles
# Commented, because the overlapped tiles needed for training were generated
# before annotating (painting) in apeer.com
# patches = patchify(padded_arr, (PATCH_SIZE, PATCH_SIZE, 3), step=STEP)[:, :, 0, :, :, :]
# tiles_x = patches.shape[1]
# tiles_y = patches.shape[0]
# for i in range(0, tiles_y):
#     for j in range(0, tiles_x):
#         img = patches[i, j, :, :, :].astype(np.uint8)
#         cv2.imwrite(path_to_images + 'rf/train/tiles_all/tile_' + str(i) + '_' + str(j) + '.tif', img)

######################################
# Train
# Extract features, generate df
t1_start = time()
img_path = global_path + 'images/train/tiles/*.tif'
image_dataset = pd.DataFrame()
for image in sorted(glob.glob(img_path)):
    img = cv2.imread(image)
    foo_image_dataset = fe.feature_extraction(img)
    foo_image_dataset['Image Name'] = image
    image_dataset = image_dataset.append(foo_image_dataset)
os.system('echo "Job finished" | mail -s "Job finished" zoneminderjr@gmail.com')
t1_stop = time()
print("Elapsed time during the whole program in seconds:", t1_stop-t1_start)
# Elapsed time during the whole program in seconds: 767.9713170528412

######################################
# Add labels column from the mask dataset
mask_path =  global_path + 'images/train/masks/*tif'
mask_dataset = pd.DataFrame()
for mask in sorted(glob.glob(mask_path)):
    foo_mask_df = pd.DataFrame()
    input_mask = cv2.imread(mask)
    if input_mask.ndim == 3 and input_mask.shape[-1] == 3:
        label = cv2.cvtColor(input_mask,cv2.COLOR_BGR2GRAY)
    elif input_mask.ndim == 2:
        label = input_mask
    else:
        raise Exception("The module works only with grayscale and RGB images!")
    label_values = label.reshape(-1)
    foo_mask_df['Label Value'] = label_values
    foo_mask_df['Mask Name'] = mask
    mask_dataset = mask_dataset.append(foo_mask_df)

######################################
# Concat image and mask datasets
# Keep only image and mask filenames in corresponding columns
t1_start = time()
img_list=[]
for i in sorted(glob.glob(img_path)): j=i.split('/')[-1]; img_list.append(j)
mask_list=[]
for i in sorted(glob.glob(mask_path)): j=i.split('/')[-1]; mask_list.append(j)
print(img_list==mask_list)#Check for consistency
df = pd.concat([image_dataset, mask_dataset], axis=1)
image_series=df['Image Name'].str.split('/', expand=True)
mask_series=df['Mask Name'].str.split('/', expand=True)
print(all(image_series.iloc[:, -1] == mask_series.iloc[:, -1])) #Check for consistency
del image_series
del mask_series
os.system('echo "Job finished" | mail -s "Job finished" zoneminderjr@gmail.com')
t1_stop = time()
print("Elapsed time during the whole program in seconds:", t1_stop-t1_start)
# Elapsed time during the whole program in seconds: 106.66420936584473

######################################
# Remove zeros
df = df[df['Label Value'] != 0]

######################################
# Notes on the proportion of training pixels vs. whole area of prediction
"""
df.shape
# (6967832, 129).
# Since the whole padded_arr has 15360x31744=487587840 pixeles, the training data
# represents 6967832/487587840=1.43% of the whole image. However, this figure
# includes the background (e.g. NoData values), which is over-represented in the
# training data. Thus, to have a more realistic proportion, it is better to
# exclude the NoData values.
df_no_background = df[df['Label Value'] != 6]
df_no_background.shape
# (4791109, 129)
np.count_nonzero(cv2.cvtColor(padded_arr,cv2.COLOR_BGR2GRAY))
# 26555156
# So, the proportion of NoData training values is 4791109/26555156=18%
"""

######################################
# Save the data frame
df_filename = global_path + "df/df"
pickle.dump(df, open(df_filename, 'wb'))

######################################
# Define variables
# Dependent variable
Y = df["Label Value"].values
# Independent variables
X = df.drop(labels = ["Image Name", "Mask Name", "Label Value"], axis=1)

######################################
# Split data into train and test to verify accuracy after fitting the model
from sklearn.model_selection import train_test_split
# The test_size argument is set to an extremely low value for generating smoothly
# segmented tiles that were patched for use as train masks in the deep learning
# model. However, the elapsed times shown after each time-consuming process, as well
# as the accuracy, correspond to a model using 0.1 as test size.
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.001, random_state=20)

######################################
# Create an (empty) instance of the model
from sklearn.ensemble import RandomForestClassifier
# Instantiate model with n number of decision trees
model = RandomForestClassifier(n_estimators = 100, random_state = 42, n_jobs = 7) # Je je, "42"

######################################
# Train the model on training data
t1_start = time()
model.fit(X_train, y_train)
os.system('echo "Job finished" | mail -s "Job finished" zoneminderjr@gmail.com')
# print('Number of Trees used : ', model.n_estimators)
t1_stop = time()
print("Elapsed time during the whole program in seconds:", t1_stop-t1_start)
# Elapsed time during the whole program in seconds: 926.1325390338898

######################################
# Predict
# On train data 
t1_start = time()
prediction_test_train = model.predict(X_train)
# On test data to calculate accuracy
prediction_test = model.predict(X_test)
# prediction_prob_test = model.predict_proba(X_test)
os.system('echo "Job finished" | mail -s "Job finished" zoneminderjr@gmail.com')
t1_stop = time()
print("Elapsed time during the whole program in seconds:", t1_stop-t1_start)
# Elapsed time during the whole program in seconds: 105.34479641914368

######################################
# Accuracy check
from sklearn import metrics
print ("Accuracy on training data = ", metrics.accuracy_score(y_train, prediction_test_train))
print ("Accuracy = ", metrics.accuracy_score(y_test, prediction_test))
# Accuracy on training data =  0.9999896666109632
# Accuracy =  0.9155120326547694

######################################
# Get numerical feature importances
importances = list(model.feature_importances_)
feature_list = list(X.columns)
feature_imp = pd.Series(model.feature_importances_,index=feature_list).sort_values(ascending=False)
print(feature_imp)
feature_imp.head(15)
"""
ch0 Gaussian s7    0.083309
ch1 Gaussian s7    0.062445
ch2 Gaussian s7    0.061719
ch2 Gaussian s3    0.054579
ch1 Gaussian s3    0.054471
ch0 Gaussian s3    0.051882
ch1 Median s3      0.032430
ch0 Median s3      0.030643
ch1 Gabor19        0.027954
ch1 Gabor3         0.025071
ch2 Median s3      0.022430
ch0 Pixel Value    0.020053
ch0 Gabor19        0.018665
ch1 Pixel Value    0.017425
ch0 Gabor21        0.015766
"""

######################################
# Save the model
model_filename = global_path + "model/model"
pickle.dump(model, open(model_filename, 'wb'))

######################################
# Predict on training data

# DELETE all the variables + restart kernel.

# Load necessary packages
import os
import numpy as np
import cv2
import scripts.feature_extraction as fe
import glob
from matplotlib import pyplot as plt
import pickle
from time import time

# Load the model
model_filename = global_path + "model/model"
loaded_model = pickle.load(open(model_filename, 'rb'))

# Predict
t1_start = time()
img_path = global_path + 'images/train/tiles/*.tif'
for file in glob.glob(img_path):
    print(file)
    img1= cv2.imread(file)
    X = fe.feature_extraction(img1)
    result = loaded_model.predict(X)
    segmented = result.reshape(img1.shape[:2])
    plt.imshow(segmented, cmap ='gray')
    name = file.split('/')[-1]
    cv2.imwrite(global_path + 'images/train/segmented/'+ name.split('.')[0] + '_segmented.tiff', segmented)
os.system('echo "Job finished" | mail -s "Job finished" zoneminderjr@gmail.com')
t1_stop = time()
print("Elapsed time during the whole program in seconds:", t1_stop-t1_start)
# Elapsed time during the whole program in seconds: 945.0758574008942

"""
If no online service is suitabble for image annotation, use QGIS.
I tried apeer.com, but many random errors occurred (e.g., labels scrambles,
out-of-service). I moved my annotations schemes to QGIS. To do so, I
polygonized the masks previously generated in apeer.com using gdal.
(all commands executed in bash within the masks folder)

1. First, I created a tfw to each TIF-mask file 
for tif in ./*.tif; do echo -e "1\n0\n0\n-1\n0\n0" > ${tif//tif/tfw}; done

2. Afterwards, I created the corresponding polygons
for tif in ./*.tif; do gdal_polygonize.py -f GPKG $tif ${tif//tif/gpkg}; done

3. I edited and saved the polygons containing the masks in QGIS

4. Lastly, I rasterized the edited masks
gdal_rasterize -l out -a DN -tr 1 1 -a_nodata 0 -te 0 -1024 1024 0 -ot Byte -of GTiff tile_12_26.gpkg tile_12_26_new.tif
"""

