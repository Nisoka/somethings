from keras import Input
import numpy as np
from keras.layers import MaxPooling2D, UpSampling2D, Conv2D, LSTM, Dense
from keras.models import Model
from tensorflow.examples.tutorials.mnist import input_data
import matplotlib.pyplot as plt
import keras.backend as K
import time

from keras.utils import to_categorical

from AttentionLayers import BasicAttentiveWeightSum, AttentiveStatisticPool

# 输入数据，包括数据集的下载、读取、切分、归一化处理等。
def get_mnist_data():
    mnist = input_data.read_data_sets('MNIST_data', one_hot=True)
    x_train, x_test = mnist.train.images, mnist.test.images
    y_train, y_test = mnist.train.labels, mnist.test.labels
    # 将784维转换为28*28矩阵。
    x_train = np.reshape(x_train, (len(x_train), 28, 28))
    x_test = np.reshape(x_test, (len(x_test), 28, 28))
    classes = 10
    # y_train = to_categorical(y_train, classes)
    # y_test = to_categorical(y_test, classes)
    return x_train, x_test, y_train, y_test

def get_model():
    print("get model")

    input = Input(shape=(28, 28))
    x_lstm = LSTM(100, activation='relu', return_sequences=True)(input)
    print(x_lstm.shape)
    # mean = BasicAttentiveWeightSum(name='AttentiveWeigthSum')(x_lstm)
    mean = AttentiveStatisticPool(name='AttentiveWeigthSum')(x_lstm)
    softmax = Dense(10, activation='softmax', name='softmax_layer')(mean)
    print(softmax.shape)
    model = Model(input, softmax)
    return model


if __name__ == "__main__":

    model = get_model()
    # # print(model.summary())
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    x_train, x_test, y_train, y_test = get_mnist_data()
    model.fit(x_train, y_train, epochs=5, batch_size=64, verbose=1, validation_split=0.05)



# BasicAttentiveWeightSum
# epoch: 5, loss: 0.0795, acc: 0.9777
# 收敛速度特别快,一次迭代就90%

# AttentiveStatisticPool
# epoch: 5, loss: 0.0795, acc: 0.9758