
from keras import Input
import numpy as np

from keras.applications import xception

from keras.layers import MaxPooling2D, UpSampling2D, Conv2D, ReLU
from keras.models import Model
from tensorflow.examples.tutorials.mnist import input_data
import matplotlib.pyplot as plt

mnist = input_data.read_data_sets("../mnist_dataset", one_hot=True)
x_train, x_test = mnist.train.images, mnist.test.images

x_train = np.reshape(x_train, (len(x_train), 28, 28, 1))
x_test  = np.reshape(x_test, (len(x_test), 28, 28, 1))

noise_factor = 0.5
x_train_noisy = x_train + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=x_train.shape)
x_test_noisy  = x_test + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=x_test.shape)

x_train_noisy = np.clip(x_train_noisy, 0.0, 1.0)
x_test_noisy = np.clip(x_test_noisy, 0.0, 1.0)

n = 10
plt.figure(figsize=(20, 4))
for i in range(n):
# display original images
    ax = plt.subplot(2, n, i + 1)
    plt.imshow(x_test[i].reshape(28, 28))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    # display noise images
    ax = plt.subplot(2, n, i + 1 + n)
    plt.imshow(x_test_noisy[i].reshape(28, 28))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
plt.show()

input_img = Input(shape=(28, 28, 1))
x = Conv2D(32, kernel_size = (3, 3), strides=(1,1), activation='relu',
           padding='same')(input_img)
x = MaxPooling2D(pool_size=(2, 2), padding='same')(x)
x = Conv2D(32, kernel_size=(3, 3), strides=(1, 1), activation='relu',
           padding='same')(x)
encodeVec = MaxPooling2D(pool_size=(2, 2), padding='same')(x)

input_img = Input(shape=(28, 28, 1)) # (?, 28, 28, 1)
x = Conv2D(32, (380, 3), activation='relu', padding='same')(input_img) # (?, 28, 28, 32)
x = MaxPooling2D((2, 2), padding='same')(x) # (?, 14, 14, 32)
x = Conv2D(32, (380, 3), activation='relu', padding='same')(x) # (?, 14, 14, 32)
x = ReLU()(x)
encodeVec = MaxPooling2D((2, 2), padding='same')(x) # (?, 7, 7, 32)


x = Conv2D(32, (3, 3), activation='relu', padding='same')(encodeVec) # (?, 7, 7, 32)
x = UpSampling2D((2, 2))(x) # (?, 14, 14, 32)
x = Conv2D(32, (3, 3), activation='relu', padding='same')(x) # (?, 14, 14, 32)
x = UpSampling2D((2, 2))(x) # (?, 28, 28, 32)
decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x) # (?, 28, 28, 1)

model_denoiseAE = Model(input_img, decoded)

model_denoiseAE.save("./test.h5")

model_denoiseAE.compile(optimizer='sgd',
                        loss='mean_squared_error')
model_denoiseAE.fit(x_train_noisy, x_train,
                    epochs=1,
                    batch_size=128,
                    shuffle=True)
                    # validation_data=(x_test_noisy, x_test))
model_denoiseAE.fit_generator()


decoded_imgs = model_denoiseAE.predict(x_test_noisy)  # 测试集合输入查看器去噪之后输出。


n = 10
plt.figure(figsize=(20, 4))
for i in range(n):
# display original images
    ax = plt.subplot(2, n, i + 1)
    plt.imshow(x_test_noisy[i].reshape(28, 28))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    # display noise images
    ax = plt.subplot(2, n, i + 1 + n)
    plt.imshow(decoded_imgs[i].reshape(28, 28))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
plt.show()





