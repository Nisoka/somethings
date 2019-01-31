# copy From https://github.com/Xls1994/CDRextraction/blob/master/customize_layer.py
from keras import backend as K
import numpy as np
from keras.engine.topology import Layer
from keras.layers import Conv2D
from keras import regularizers
import tensorflow as tf



class BasicAttentiveWeightSum(Layer):
    def __init__(self, W_regularizer=None, b_regularizer=None, **kwargs):
        self.supports_masking = False
        # self.mask =mask
        self.W_regularizer = regularizers.get(W_regularizer)
        self.b_regularizer = regularizers.get(b_regularizer)
        super(BasicAttentiveWeightSum, self).__init__(**kwargs)

    def build(self, input_shape):
        in_dim = input_shape[2]
        out_dim = 1
        lim =np.sqrt(6./(in_dim + out_dim))

        self.W =K.random_uniform_variable((in_dim, out_dim), -lim, lim,
                                         name='{}_W'.format(self.name))

        self.b =K.zeros((out_dim, ), name='{}_b'.format(self.name))

        self.trainable_weights = [self.W,self.b]

        self.regularizer = []

        if self.W_regularizer is not None:
            self.add_loss(self.W_regularizer(self.W))
        if self.b_regularizer is not None:
            self.add_loss(self.b_regularizer(self.b))

        super(BasicAttentiveWeightSum, self).build(input_shape)
        # self.build =True

    def call(self, inputs,mask=None):
        # print('input shape', K.int_shape(inputs))
        # print(self.W.shape, self.b.shape)

        # the K.sum actually do the reshape ops, but K.reshape not do well, so use the K.sum
        e_t = K.sum(K.tanh(K.dot(inputs, self.W) + self.b), axis = -1)
        # print("e_t shape: ", e_t.shape)

        alpha = K.softmax(e_t)
        # print("alpha shape: ", alpha.shape)

        output = K.sum(inputs * K.expand_dims(alpha, axis=-1), axis=1) #sum(32 *6 *310)
        # print('output..shape',K.int_shape(output))
        return output

    def compute_output_shape(self, input_shape):
        shape =input_shape
        shape =list(shape)
        return  (shape[0],shape[2])

    def compute_mask(self, inputs, mask=None):
        return None


class AttentiveStatisticPool(Layer):
    def __init__(self, W_regularizer=None, b_regularizer=None, **kwargs):
        self.supports_masking = False
        # self.mask =mask
        self.W_regularizer = regularizers.get(W_regularizer)
        self.b_regularizer = regularizers.get(b_regularizer)
        super(AttentiveStatisticPool, self).__init__(**kwargs)

    def build(self, input_shape):
        in_dim = input_shape[2]
        out_dim = 1
        lim =np.sqrt(6./(in_dim + out_dim))

        self.W =K.random_uniform_variable((in_dim, out_dim), -lim, lim,
                                         name='{}_W'.format(self.name))

        self.b =K.zeros((out_dim, ), name='{}_b'.format(self.name))

        self.trainable_weights = [self.W,self.b]

        self.regularizer = []

        if self.W_regularizer is not None:
            self.add_loss(self.W_regularizer(self.W))
        if self.b_regularizer is not None:
            self.add_loss(self.b_regularizer(self.b))

        super(AttentiveStatisticPool, self).build(input_shape)
        # self.build =True

    def call(self, inputs,mask=None):
        # print('input shape', K.int_shape(inputs))
        # print(self.W.shape, self.b.shape)

        # the K.sum actually do the reshape ops, but K.reshape not do well, so use the K.sum
        e_t = K.sum(K.tanh(K.dot(inputs, self.W) + self.b), axis = -1)
        # print("e_t shape: ", e_t.shape)

        # calc the weight parameters alpha
        alpha = K.softmax(e_t)
        alpha = K.expand_dims(alpha, axis=-1)
        # print("alpha shape: ", alpha.shape)
        # print(inputs.shape)
        mean, stddev = tf.nn.weighted_moments(inputs, frequency_weights=alpha, axes=1)
        # print(mean.shape, stddev.shape)
        output = K.concatenate([mean, stddev])
        # print('output..shape',K.int_shape(output))
        return output

    def compute_output_shape(self, input_shape):
        shape =input_shape
        shape =list(shape)
        return  (shape[0],shape[2]*2)

    def compute_mask(self, inputs, mask=None):
        return None
