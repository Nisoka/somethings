

import numpy as np
from keras import Input
from keras.layers import MaxPooling2D, UpSampling2D, Conv2D
from keras.models import  Model
from tensorflow.examples.tutorials.mnist import input_data
import matplotlib.pyplot as plt

mnist = input_data.read_data_sets('minist', one_hot=True)
x_train, x_test = mnist.train.images, mnist.test.images