# copy From https://github.com/Xls1994/CDRextraction/blob/master/customize_layer.py
from keras import backend as K
import numpy as np
from keras.engine.topology import Layer
from keras.layers import Conv1D
from keras import regularizers
import tensorflow as tf


def DFSMNLayer(input, out_dim, kernel, stride):
    # test 28 x 28
    # 1 CONV1D
    # x = Conv1D(1024, 3, strides=1, padding='same', activation=None, use_bias=True)(x_)
    h_low = Conv1D(out_dim, kernel_size=kernel, strides=stride, activation='relu',padding='same')(input)
    p_hat = DispersedMemory(10, 10, 2, 2, name="DFSMN")(h_low)
    

class DispersedMemory(Layer):
    # THIS CLASS LAYER, IS JUST FOR COMPUTE THE DFSMN'S Memory part
    # as the other part can be implement to combine the Dnn + DispersedMemory + skip_connect very well
    def __init__(self, memory_size_left, memory_size_right, stride_l, stride_r, **kwargs):

        self._memory_size_left = memory_size_left
        self._memory_size_right = memory_size_right

        self._stride_l = stride_l
        self._stride_r = stride_r

        self.left_use_max = self._memory_size_left * self._stride_l
        self.right_use_max = self._memory_size_right * self._stride_r


        self.M_regularizer = regularizers.get(M_regularizer)
        self.time_steps = 0
        self.in_dim = 0
        super(DispersedMemory, self).__init__(**kwargs)

    def build(self, input_shape):
        self.time_steps = input_shape[1]
        self.in_dim = input_shape[2]

        lim = np.sqrt(6. / (self.in_dim*2))

        self._memory_vector_left =  \
            K.random_uniform_variable((self.in_dim, self._memory_size_left), -lim, lim,
                                       name='{}_MemoryVectorL'.format(self.name))

        self._memory_vector_right =  \
            K.random_uniform_variable((self.in_dim, self._memory_size_right), -lim, lim,
                                       name='{}_MemoryVectorR'.format(self.name))

        self.trainable_weights = [self._memory_vector_left, self._memory_vector_right]


        if self.M_regularizer is not None:
            self.add_loss(self.M_regularizer(self._memory_vector_left, self._memory_vector_right))

        super(DispersedMemory, self).build(input_shape)
        # self.build =True

    def call(self, P, mask=None):
        # The INPUT WILL BE all time P_t
        # (Batch_size, time_steps, feature-dim)
        # so will be do the compute
        #  P_hat = PM
        #  M is the weight vector memory.
        # for time_step_0  will be [1, c1, c2, ... cn, 0, 0, ... 0]^T
        #     time_step_1  will be [a1, 1, c1, c2 .... cn, 0, 0 .0]^T

        # M will be [time_steps, time_steps, feature_dim]
        # [
        #  [1, c1, c2, ... cn, 0, 0, ... 0]
        #  [a1, 1, c1, c2, ... cn, 0, 0, 0]
        #  ....
        #  [0, ...0, an, ..,a2, a1, 1, c1 ]
        #  [0, 0, an, ..,a2, a1, 1, c1, c2 ]
        # ]^T

        # so one example's P == [ time_steps, feature_dim ]
        # P*M will be [ time_steps, time_steps, feature_dim ] x [time_steps, feature_dim] = [time_steps, feature_dim]
        #

        # 1 construct the Memory- M
        # Construct memory matrix
        memory_matrix = K.zeros(shape=(self.time_steps, self.time_steps, self.in_dim))
        weight_one = K.ones(shape=(self.time_steps, self.in_dim))

        # for each time step.
        for step in range(self.time_steps):
            # [ x, x, x, x, x, x, x, x, x, x]
            #       |                | ???
            # a0 - an, is the lookback memory weight

            target_l_start = 0
            if step < self.left_use_max:
                target_l_start = 0
            else:
                target_l_start = step - self.left_use_max

            target_r_end = 0
            if self.time_steps - step > self.right_use_max:
                target_r_end = step + self.right_use_max + 1
            else:
                target_r_end = self.time_steps


            # check time_steps = 100
            # step == 5, (will compute the 0, 1, 2, 3, 4)  memory_vector_left[5:]
            # so will start at 5 = left_use_max - step
            src_l_start = tf.maximum(self.left_use_max - step, 0)
            # if step = 95, will compute the (96 97 98 99), memory_vector_right[:4]
            # so will end at 4  = self.time_steps - 1 - step = 4
            src_r_end = tf.minimum(self.time_steps - 1 - step , self.right_use_max)


            mem_l = K.zeros(shape=(self.left_use_max, self.in_dim))
            alpha_list = list(range(self.left_use_max))
            alpha_list.reverse()
            stat = 0
            mem_index = -1
            for i in alpha_list:
                if stat != 0:
                    stat -= 1
                else:
                    mem_l[i] = self._memory_vector_left[mem_index]
                    stat = self._stride_l
                    mem_index -= 1

            mem_r = K.zeros(shape=(self.right_use_max, self.in_dim))
            alpha_list = list(range(self.left_use_max))
            stat = 0
            mem_index = 0
            for i in alpha_list:
                if stat != 0:
                    stat -= 1
                else:
                    mem_r[i] = self._memory_vector_right[mem_index]
                    stat = self._stride_r
                    mem_index += 1



            memory_matrix[step][step] = weight_one
            memory_matrix[step][target_l_start:step] = mem_l[src_l_start:]
            memory_matrix[step][step+1:target_r_end] = mem_r[:src_r_end]

        P_hatt = K.matmul(memory_matrix, P)
        print(P_hatt.shape)
        return P_hatt

    def compute_output_shape(self, input_shape):
        return input_shape

    def compute_mask(self, inputs, mask=None):
        return None
