#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Thu Jul 15 20:33:05 2021

@author: Jose Ramon Martinez Batlle (GH: @geofis)

Based on:
Author: Dr. Sreenivas Bhattiprolu
Multiclass semantic segmentation using U-Net
Including segmenting large images by dividing them into smaller patches 
and stiching them back
Video: https://youtu.be/XyX5HNuv-xE
"""

###############################################
# Start a logfile
%logstart -ot logfile rotate
# get_ipython().magic('logstop')

###############################################
# Path, packages, custom functions
path_global = '/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/'
import sys
sys.path.insert(0, path_global + 'scripts')
from simple_multi_unet_model import multi_unet_model #Uses softmax 
from keras.utils import normalize
import os
import glob
import gc
import cv2
import numpy as np
from matplotlib import pyplot as plt
import crop_patches as cp
from unpad import unpad
from random import sample, seed #For randomly select image files
import hashlib #To generate md5sum hash of image files
from sklearn.model_selection import train_test_split #To split the data in train and test sets
from keras.utils import to_categorical #To convert train masks to categorical
import segmentation_models as sm #To define some loss-functions
from keras.models import load_model #To load saved models
from tensorflow.keras.callbacks import ModelCheckpoint, CSVLogger #To add checkpoints and logger in CSV format
import pandas as pd #To convert the history object to Data Frame
import pickle #To save the history object

###############################################
# Define size of training tiles and number of clases
SIZE_X = 256
SIZE_Y = 256
n_classes=7 #Number of classes for segmentation

###############################################
# Create list of training images, to be converted to an array
train_images = []
ti_list=[]
for directory_path in glob.glob(path_global + "images/train/tiles/"):
    for img_path in glob.glob(os.path.join(directory_path, "*.tif")):
        ti_list.append(img_path) #This is a list of names
        img = cv2.imread(img_path)
        train_images.append(img) #This is a list of arrays
#Convert list to array for processing
train_images = np.array(train_images)

###############################################
# From the list of train image names, randomly select 10 images to show their
# md5sum as a reference for cross-checking which files were used
# for as training tiles
ti_names=[] #List of train-image names
for i in ti_list: j=str.split(i, '/'); ti_names.append(j[-1])
seed(0)
sample(ti_names, 10)
hash_trains = []
seed(0)
for i in sample(ti_names, 10):
    hs = hashlib.md5(str(path_global + "images/train/masks/" + i).encode('utf-8')).hexdigest()
    hash_trains.append(i + '   ' + hs)
hash_trains

###############################################
# Create list of training masks, which will be converted to an array later.
# A segmented image of the whole area was generated with Random Forest
# algorithm in the first place. That image was later cut in tiles which
# are used here as train masks.
train_masks = []
tm_list = []
for directory_path in glob.glob(path_global + "images/train/masks/"):
    for mask_path in glob.glob(os.path.join(directory_path, "*.tif")):
        tm_list.append(mask_path)
        mask = cv2.imread(mask_path, 0)
        train_masks.append(mask)
#Convert list to array for processing
train_masks = np.array(train_masks)

###############################################
# Check if images and mask names names are consistently ordered
tm_names=[]
for l in tm_list: m=str.split(l, '/'); tm_names.append(m[-1])
ti_names==tm_names #If True, both images and mask names are consistently ordered

###############################################
# From the list of train image names, randomly select 10 images to show their
# md5sum as a reference for cross-checking which files were used
# for as training tiles
hash_masks = []
seed(0)
for i in sample(tm_names, 10):
    hs = hashlib.md5(str(path_global + "images/train/masks/" + i).encode('utf-8')).hexdigest()
    hash_masks.append(i + '   ' + hs)
hash_masks

###############################################
# Should labels be recoded? If yes, then use LabelEncoder from sklearn.preprocessing
# At least, check whether unique labels are coded well
np.unique(train_masks)

###############################################
# Normalize train images
train_images = normalize(train_images, axis=3)

###############################################
# Expand mask arrays in one dimension. This is pre-requisite for U-Net model
train_masks_input = np.expand_dims(train_masks, axis=3)

###############################################
# Create a subset of data for quick testing
# Picking 25% for testing and remaining for training
X_train, X_test, y_train, y_test = train_test_split(train_images, train_masks_input, test_size = 0.25, random_state = 0)
# This code just below creates a corresponding list of file names reserved for testing
X1_ti_names, X_test_ti_names=train_test_split(np.array(ti_names), test_size=0.25, random_state=0)


###############################################
# Print again the class values in the training dataset (y_train)
print("Class values in the dataset are ... ", np.unique(y_train))  # 0 is the background/few unlabeled 

###############################################
# Convert train labels to categorical, otherwise, the model would treat the
# the dependent variable as numerical. Each class will be placed in a separated slice
y_train_cat = to_categorical(y_train, num_classes=n_classes)
# Do the same with the test labels
y_test_cat = to_categorical(y_test, num_classes=n_classes)

###############################################
# Define image dimensions for the model from the training data
IMG_HEIGHT = X_train.shape[1]
IMG_WIDTH  = X_train.shape[2]
IMG_CHANNELS = X_train.shape[3]

###############################################
# Define the model based on the multi_unet_model function in the script 
# "simple_multi_unet_model.py"
def get_model():
    return multi_unet_model(
        n_classes=n_classes,
        IMG_HEIGHT=IMG_HEIGHT,
        IMG_WIDTH=IMG_WIDTH,
        IMG_CHANNELS=IMG_CHANNELS)
model = get_model()

###############################################
# Compile the model. Multiple options for defining loss function. Select one
# from "categorial_crossentropy", "sm.losses.CategoricalFocalLoss()" or
# "sm.losses.DiceLoss". The first two were the more accurate
# model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy']) # BEST LOSS FUNCTION SO FAR!!!!!!
model.compile(optimizer='adam', loss=sm.losses.CategoricalFocalLoss(), metrics=['accuracy'])
# model.compile(optimizer='adam', loss=sm.losses.DiceLoss(), metrics=['accuracy'])
# Print model summary
model.summary()

###############################################
# Add Callbacks, e.g. ModelCheckpoints and csvlogger.
# from keras.callbacks import ModelCheckpoint and CSVLogger
# ModelCheckpoint callback saves a model at some interval. 
model_checkpoint_filepath= path_global + "model/model-epoch-{epoch:03d}-accuracy-{accuracy:03f}-val-accuracy-{val_accuracy:03f}-val-loss-{val_loss:03f}.hdf5" #File name includes epoch and validation accuracy.
#Use Mode = max for accuracy and min for loss. 
checkpoint = ModelCheckpoint(model_checkpoint_filepath, monitor='val_accuracy', verbose=1, save_best_only=False, mode='max', save_freq='epoch')
#CSVLogger logs epoch, acc, loss, val_acc, val_loss
log_csv = CSVLogger(path_global + 'model/my_logs.csv', separator=',', append=False)
callbacks_list = [checkpoint, log_csv]

#We can now use these generators to train our model. 
#Give this a name so we can call it later for plotting loss, accuracy etc. as a function of epochs.
# history = model.fit_generator(
#         X_train, y_train_cat, 
#         steps_per_epoch=2000 // 16,    #The 2 slashes division return rounded integer
#         epochs=5,
#         validation_data=(X_test, y_test_cat), 
#         validation_steps=800 // 16,
#         callbacks=callbacks_list)

###############################################
# Fit the model. Assign to an object, so we can call it back later for
# plotting purposes and to retrieve metrics. We can also retrieve metrics
# from the CSV file "my_logs.csv".
history = model.fit(X_train, y_train_cat,
                    batch_size = 16, 
                    verbose=1, 
                    epochs=100,
                    validation_data=(X_test, y_test_cat), 
                    # class_weight=class_weights,
                    # sample_weight= class_weights_arr,
                    shuffle=False,
                    callbacks=callbacks_list)
os.system('echo "Job finished" | mail -s "Job finished" zoneminderjr@gmail.com') #Yes, this is THE actual computation

###############################################
# Save the history object to retrieve metrics. We can also use the CSV file "my_logs.csv"
history_df = pd.DataFrame(history.history)
pickle.dump(history.history, open(path_global + 'model/history', 'wb'))

###############################################
# LOAD THE MODEL, CHECK ITS METRIC, PREDICT
# It is better to load a saved model rather than use the one obtained form the 
# last epoch of the fitting process
# model.save(path_global + 'model/test.hdf5')
# Example of how to load model with custom loss function
# model=load_model('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/model/using_smoothed_masks_from_majority_file/test07/model-epoch-067-accuracy-0.942376-val-accuracy-0.918130-val-loss-0.004345_sm.losses.CategoricalFocalLoss.hdf5', custom_objects={'focal_loss': sm.losses.CategoricalFocalLoss()}) #!!!!!!GOOD MODEL
# model=load_model('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/model/using_non_smoothed_masks/test01/model-epoch-058-accuracy-0.924932-val-accuracy-0.894267-val-loss-0.006085.hdf5', custom_objects={'focal_loss': sm.losses.CategoricalFocalLoss()}) #!!!!!!GOOD MODEL
# model=load_model('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/model/using_non_smoothed_masks/test02/model-epoch-076-accuracy-0.933162-val-accuracy-0.911374-val-loss-0.280565_categorical_crossentropy.hdf5', custom_objects={'focal_loss': 'categorical_crossentropy'}) #!!!!!!GOOD MODEL
# model=load_model('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/model/model-epoch-079-accuracy-0.918235-val-accuracy-0.904944-val-loss-0.299592.hdf5', custom_objects={'focal_loss': 'categorical_crossentropy'}) #!!!!!!GOOD MODEL
# model=load_model('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/model/model-epoch-098-accuracy-0.948391-val-accuracy-0.908943-val-loss-0.004927.hdf5', custom_objects={'focal_loss': sm.losses.CategoricalFocalLoss()}) #!!!!!!GOOD MODEL
# model=load_model('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/model/using_smoothed_masks_from_majority_file/test08/model-epoch-100-accuracy-0.942849-val-accuracy-0.877416-val-loss-0.444153.hdf5', compile=False) #!!!!!!GOOD MODEL
model=load_model('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/model/using_smoothed_masks_from_majority_file/test11_512x512_majority_acceptable_result_when_using_overlapping_in_prediction/model-epoch-099-accuracy-0.895865-val-accuracy-0.858394-val-loss-0.004859_sm.losses.CategoricalFocalLoss.hdf5', compile=False) #!!!!!!GOOD MODEL
model=load_model('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/model/using_non_smoothed_masks_from_majority_file/test12_256x256_NO_majority_acceptable_result_when_using_overlapping_in_prediction/model-epoch-098-accuracy-0.865276-val-accuracy-0.839103-val-loss-0.006905_sm.losses.CategoricalFocalLoss.hdf5', compile=False) #!!!!!!GOOD MODEL
model=load_model('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/model/using_non_smoothed_masks_from_majority_file/test13_256x256_NO_majority_acceptable_result_when_using_overlapping_in_prediction_categorical_crossentropy/model-epoch-085-accuracy-0.874583-val-accuracy-0.852062-val-loss-0.423324_categorical_crossentropy.hdf5', compile=False) #!!!!!!GOOD MODEL
model=load_model('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/model/using_non_smoothed_masks_from_majority_file/test14_256x256_NO_majority_acceptable_result_when_using_overlapping_in_prediction_diceloss/model-epoch-095-accuracy-0.805095-val-accuracy-0.828043-val-loss-0.287673_sm.losses.DiceLoss.hdf5', compile=False) #!!!!!!GOOD MODEL
model=load_model('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/model/using_smoothed_masks_from_majority_file/test15_128x128_majority_acceptable_result_when_using_overlapping_in_prediction_bars_and_clasts_grouped/model-epoch-098-accuracy-0.941324-val-accuracy-0.905922-val-loss-0.286298_categorical_crossentropy.hdf5', custom_objects={'focal_loss': 'categorical_crossentropy'}) #!!!!!!GOOD MODEL
model=load_model('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/model/using_smoothed_masks_from_majority_file/test16_256x256_majority_acceptable_result_when_using_overlapping_in_prediction_bars_and_clasts_grouped/model-epoch-099-accuracy-0.949614-val-accuracy-0.920464-val-loss-0.255084_categorical_crossentropy.hdf5', custom_objects={'focal_loss': 'categorical_crossentropy'}) #!!!!!!GOOD MODEL
model=load_model('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/model/using_smoothed_masks_from_majority_file/test17_256x256_majority_acceptable_result_when_using_overlapping_in_prediction_bars_and_clasts_grouped/model-epoch-096-accuracy-0.952686-val-accuracy-0.928995-val-loss-0.003136.hdf5', custom_objects={'focal_loss': sm.losses.CategoricalFocalLoss()}) #!!!!!!GOOD MODEL


############################################################
#Evaluate the model
	# evaluate model
_, acc = model.evaluate(X_test, y_test_cat)
print("Accuracy is = ", (acc * 100.0), "%")


###
#plot the training and validation accuracy and loss at each epoch
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(loss) + 1)
plt.plot(epochs, loss, 'y', label='Training loss')
plt.plot(epochs, val_loss, 'r', label='Validation loss')
plt.title('Training and validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

acc = history.history['acc']
val_acc = history.history['val_acc']

plt.plot(epochs, acc, 'y', label='Training Accuracy')
plt.plot(epochs, val_acc, 'r', label='Validation Accuracy')
plt.title('Training and validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()


##################################
#model = get_model()
# model.load_weights('sandstone_50_epochs_catXentropy_acc.hdf5')  
#model.load_weights('sandstone_50_epochs_catXentropy_acc_with_weights.hdf5')  

#IOU
y_pred=model.predict(X_test)
y_pred_argmax=np.argmax(y_pred, axis=3)

##################################################

#Using built in keras function
from keras.metrics import MeanIoU
# n_classes = 7
IOU_keras = MeanIoU(num_classes=n_classes)  
IOU_keras.update_state(y_test[:,:,:,0], y_pred_argmax)
print("Mean IoU =", IOU_keras.result().numpy())


#To calculate I0U for each class...
values = np.array(IOU_keras.get_weights()).reshape(n_classes, n_classes)
print(values)
# class1_IoU = values[0,0]/(values[0,0] + values[0,1] + values[0,2] + values[0,3] + values[0,4] + values[0,5] + values[0,6] + values[0,7] + values[1,0] + values[2,0] + values[3,0] + values[4,0] + values[5,0] + values[6,0] + values[7,0])
# class2_IoU = values[1,1]/(values[1,1] + values[1,0] + values[1,2] + values[1,3] + values[1,4] + values[1,5] + values[1,6] + values[1,7] + values[0,1] + values[2,1] + values[3,1] + values[4,1] + values[5,1] + values[6,1] + values[7,1])
# class3_IoU = values[2,2]/(values[2,2] + values[2,0] + values[2,1] + values[2,3] + values[2,4] + values[2,5] + values[2,6] + values[2,7] + values[0,2] + values[1,2] + values[3,2] + values[4,2] + values[5,2] + values[6,2] + values[7,2])
# class4_IoU = values[3,3]/(values[3,3] + values[3,0] + values[3,1] + values[3,2] + values[3,4] + values[3,5] + values[3,6] + values[3,7] + values[0,3] + values[1,3] + values[2,3] + values[4,3] + values[5,3] + values[6,3] + values[7,3])
# class5_IoU = values[4,4]/(values[4,4] + values[4,0] + values[4,1] + values[4,2] + values[4,3] + values[4,5] + values[4,6] + values[4,7] + values[0,4] + values[1,4] + values[2,4] + values[3,4] + values[5,4] + values[6,4] + values[7,4])
# class6_IoU = values[5,5]/(values[5,5] + values[5,0] + values[5,1] + values[5,2] + values[5,3] + values[5,4] + values[5,6] + values[5,7] + values[0,5] + values[1,5] + values[2,5] + values[3,5] + values[4,5] + values[6,5] + values[7,5])
# class7_IoU = values[6,6]/(values[6,6] + values[6,0] + values[6,1] + values[6,2] + values[6,3] + values[6,4] + values[6,5] + values[6,7] + values[0,6] + values[1,6] + values[2,6] + values[3,6] + values[4,6] + values[5,6] + values[7,6])
# class8_IoU = values[7,7]/(values[7,7] + values[7,0] + values[7,1] + values[7,2] + values[7,3] + values[7,4] + values[7,5] + values[7,6] + values[0,7] + values[1,7] + values[2,7] + values[3,7] + values[4,7] + values[5,7] + values[6,7])
class1_IoU = values[0,0]/(values[0,0] + values[0,1] + values[0,2] + values[0,3] + values[0,4] + values[0,5] + values[0,6] + values[1,0] + values[2,0] + values[3,0] + values[4,0] + values[5,0] + values[6,0])
class2_IoU = values[1,1]/(values[1,1] + values[1,0] + values[1,2] + values[1,3] + values[1,4] + values[1,5] + values[1,6] + values[0,1] + values[2,1] + values[3,1] + values[4,1] + values[5,1] + values[6,1])
class3_IoU = values[2,2]/(values[2,2] + values[2,0] + values[2,1] + values[2,3] + values[2,4] + values[2,5] + values[2,6] + values[0,2] + values[1,2] + values[3,2] + values[4,2] + values[5,2] + values[6,2])
class4_IoU = values[3,3]/(values[3,3] + values[3,0] + values[3,1] + values[3,2] + values[3,4] + values[3,5] + values[3,6] + values[0,3] + values[1,3] + values[2,3] + values[4,3] + values[5,3] + values[6,3])
class5_IoU = values[4,4]/(values[4,4] + values[4,0] + values[4,1] + values[4,2] + values[4,3] + values[4,5] + values[4,6] + values[0,4] + values[1,4] + values[2,4] + values[3,4] + values[5,4] + values[6,4])
class6_IoU = values[5,5]/(values[5,5] + values[5,0] + values[5,1] + values[5,2] + values[5,3] + values[5,4] + values[5,6] + values[0,5] + values[1,5] + values[2,5] + values[3,5] + values[4,5] + values[6,5])
class7_IoU = values[6,6]/(values[6,6] + values[6,0] + values[6,1] + values[6,2] + values[6,3] + values[6,4] + values[6,5] + values[0,6] + values[1,6] + values[2,6] + values[3,6] + values[4,6] + values[5,6])
print("IoU for Background is: ", class1_IoU) #Background
print("IoU for Clasts is: ", class2_IoU) #Clasts
print("IoU for Riffle-shallow-glare is: ", class3_IoU) #Riffle-shallow-glare
print("IoU for Low vegetation is: ", class4_IoU) #Low vegetation
print("IoU for Pool is: ", class5_IoU) #Pool
print("IoU for Riparian vegetation is: ", class6_IoU) #Riparian vegetation
print("IoU for Bar is: ", class7_IoU) #Shadow
# print("IoU for Shadow is: ", class8_IoU) #Shadow



plt.imshow(train_images[0, :,:,0], cmap='gray')
plt.imshow(train_masks[0], cmap='gray')
#######################################################################
#Predict on a few images
#model = get_model()
#model.load_weights('???.hdf5')  
import random
test_img_number = random.randint(0, len(X_test))
print(X_test_ti_names[test_img_number])
"""
# Using image from disk
test_img=cv2.imread('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/images/train/tiles/tile_0_1_8_6.tif')
test_img_norm=normalize(test_img)
ground_truth=cv2.imread('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/deep_learning_u_net/images/train/masks/tile_0_1_8_6.tif')
test_img_input=np.expand_dims(test_img_norm, 0)
prediction = (model.predict(test_img_input))
predicted_img=np.argmax(prediction, axis=3)[0,:,:]
"""
test_img = X_test[test_img_number]
ground_truth=y_test[test_img_number]
test_img_norm=normalize(test_img, axis=2)#[:,:,:][:,:,None]
test_img_input=np.expand_dims(test_img_norm, 0)
prediction = (model.predict(test_img_input))
predicted_img=np.argmax(prediction, axis=3)[0,:,:]


plt.figure(figsize=(12, 8))
plt.subplot(231)
plt.title('Testing Image')
plt.imshow(test_img[:,:,0], cmap='gray')
plt.subplot(232)
plt.title('Testing Label')
plt.imshow(ground_truth[:,:,0], cmap='jet')
plt.subplot(233)
plt.title('Prediction on test image')
plt.imshow(predicted_img, cmap='jet')
plt.show()

cv2.imwrite(path_global + 'test.tif', test_img[:,:,0])
cv2.imwrite(path_global + 'mask.tif', ground_truth)
cv2.imwrite(path_global + 'predicted.tif', predicted_img)

#####################################################################

#Predict on large image
#Apply a trained model on large image

# Predicting on tiles WITH overlap, USING FUNCTIONS (crop_patches and unpad)
from patchify import patchify, unpatchify
large_image = cv2.imread('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/original/mana_whole_padded.tif')
STEP = SIZE_X//2
pad_width = ((SIZE_X, SIZE_Y), (SIZE_X, SIZE_Y), (0, 0))
unpad_width = ((STEP*3//2, STEP*3//2), (STEP*3//2, STEP*3//2))
large_image = np.pad(large_image, pad_width)
patches = patchify(large_image, (SIZE_X, SIZE_Y, large_image.shape[2]), step=STEP)[:, :, 0, :, :, :]
del large_image
gc.collect()

predicted_patches = []
for i in range(patches.shape[0]):
    for j in range(patches.shape[1]):
        print(i,j)
        single_patch = patches[i,j,:,:,:]
        non_zeros = np.count_nonzero(single_patch)
        if(non_zeros>0):
            single_patch_norm = normalize(np.array(single_patch), axis=2)
            single_patch_input=np.expand_dims(single_patch_norm, 0)
            single_patch_prediction = (model.predict(single_patch_input))
            single_patch_predicted_img=np.argmax(single_patch_prediction, axis=3)[0,:,:]
        else:
            single_patch_predicted_img=np.zeros(shape=single_patch.shape[:2], dtype='int64')
        predicted_patches.append(single_patch_predicted_img)
os.system('echo "Job finished" | mail -s "Job finished" zoneminderjr@gmail.com')

predicted_patches = np.array(predicted_patches)
predicted_patches_reshaped = np.reshape(predicted_patches, patches.shape[:4])
del predicted_patches
gc.collect()
predicted_patches_cropped = cp.crop_patches(predicted_patches_reshaped, crop_size=STEP)
del predicted_patches_reshaped
gc.collect()
reconstructed_image = unpatchify(predicted_patches_cropped, (predicted_patches_cropped.shape[0]*STEP, predicted_patches_cropped.shape[1]*STEP))
reconstructed_image = unpad(reconstructed_image, unpad_width)
cv2.imwrite(path_global + 'images/predict/segmented_whole_image/predicted.tif', reconstructed_image)

"""
# Predicting on tiles with no overlap
from patchify import patchify, unpatchify
large_image = cv2.imread('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/original/mana_whole_padded.tif')
#This will split the image into small images of shape [3,3]
patches = patchify(large_image, (SIZE_X, SIZE_Y, large_image.shape[2]), step=SIZE_X)[:, :, 0, :, :, :]  #Step=256 for 256 patches means no overlap

predicted_patches = []
for i in range(patches.shape[0]):
    for j in range(patches.shape[1]):
        print(i,j)
        single_patch = patches[i,j,:,:,:]
        non_zeros = np.count_nonzero(single_patch)
        if(non_zeros>0):
            single_patch_norm = normalize(np.array(single_patch), axis=2)
            single_patch_input = np.expand_dims(single_patch_norm, 0)
            single_patch_prediction = (model.predict(single_patch_input))
            single_patch_predicted_img = np.argmax(single_patch_prediction, axis=3)[0,:,:]
        else:
            single_patch_predicted_img = np.zeros(shape=single_patch.shape[:2], dtype='int64')
        predicted_patches.append(single_patch_predicted_img)

os.system('echo "Job finished" | mail -s "Job finished" zoneminderjr@gmail.com')
predicted_patches = np.array(predicted_patches)
predicted_patches_reshaped = np.reshape(predicted_patches, (patches.shape[0], patches.shape[1], SIZE_X, SIZE_Y) )
reconstructed_image = unpatchify(predicted_patches_reshaped, large_image.shape[:2])
cv2.imwrite(path_global + 'images/predict/testing/segmented_whole_image/predicted.tif', reconstructed_image)
"""

"""
# Predicting on tiles WITH overlap, but preserving only the inner part of tiles
from patchify import patchify, unpatchify
large_image = cv2.imread('/media/jose/datos/deep_learning/geomorfologia-detalle-tramo-1km-rio-mana/machine_learning_rf/images/original/mana_whole_padded.tif')
STEP = 256
patches = patchify(large_image, (SIZE_X, SIZE_Y, large_image.shape[2]), step=STEP)[:, :, 0, :, :, :]

predicted_patches = []
for i in range(patches.shape[0]):
    for j in range(patches.shape[1]):
        print(i,j)
        single_patch = patches[i,j,:,:,:]
        non_zeros = np.count_nonzero(single_patch)
        if(non_zeros>0):
            single_patch_norm = normalize(np.array(single_patch), axis=2)
            single_patch_input=np.expand_dims(single_patch_norm, 0)
            single_patch_prediction = (model.predict(single_patch_input))
            single_patch_predicted_img=np.argmax(single_patch_prediction, axis=3)[0,:,:]
        else:
            single_patch_predicted_img=np.zeros(shape=single_patch.shape[:2], dtype='int64')
        predicted_patches.append(single_patch_predicted_img)
os.system('echo "Job finished" | mail -s "Job finished" zoneminderjr@gmail.com')

predicted_patches_interior=[]
for i in range(len(predicted_patches)):
    interior=predicted_patches[i][(SIZE_X-STEP)//2:SIZE_X-(SIZE_X-STEP)//2,(SIZE_Y-STEP)//2:SIZE_Y-(SIZE_Y-STEP)//2]
    predicted_patches_interior.append(interior)
predicted_patches_interior = np.array(predicted_patches_interior)
predicted_patches_reshaped = np.reshape(predicted_patches_interior, (patches.shape[0], patches.shape[1], interior.shape[0], interior.shape[1]))
reconstructed_image = unpatchify(predicted_patches_reshaped, (predicted_patches_reshaped.shape[0]*predicted_patches_reshaped.shape[2], predicted_patches_reshaped.shape[1]*predicted_patches_reshaped.shape[3]))
cv2.imwrite(path_global + 'images/predict/testing/segmented_whole_image/predicted.tif', reconstructed_image)
"""

plt.imshow(reconstructed_image, cmap='gray')
#plt.imsave('data/results/segm.jpg', reconstructed_image, cmap='gray')

plt.hist(reconstructed_image.flatten())  #Threshold everything above 0

# final_prediction = (reconstructed_image > 0.01).astype(np.uint8)
# plt.imshow(final_prediction)

plt.figure(figsize=(8, 8))
plt.subplot(221)
plt.title('Large Image')
plt.imshow(large_image, cmap='gray')
plt.subplot(222)
plt.title('Prediction of large Image')
plt.imshow(reconstructed_image, cmap='jet')
plt.show()
