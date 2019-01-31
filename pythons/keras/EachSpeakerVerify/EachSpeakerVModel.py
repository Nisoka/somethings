import logging
import os, sys

os.environ["CUDA_VISIBLE_DEVICES"] = "2,3"
import keras.backend as K
from keras import regularizers
from keras.layers import Input
from keras.layers.convolutional import Conv2D, Conv1D, MaxPooling2D
from keras.layers.core import Lambda, Dense, RepeatVector, Dropout
from keras.layers.core import Reshape
from keras.layers.normalization import BatchNormalization
from keras.models import Model
from keras.utils import multi_gpu_model



