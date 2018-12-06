import keras
import numpy as np
from keras import models
from keras import layers
from keras import optimizers
from keras.datasets import imdb
from keras.models import Sequential
from keras.utils import to_categorical
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

(train_data, train_labels), (test_data, test_labels) = imdb.load_data(num_words=500)

def vectorize_sequences(sequences, dimension=500):
    # Create an all-zero matrix of shape (len(sequences), dimension)
    results = np.zeros((len(sequences), dimension))
    for i, sequence in enumerate(sequences):
        results[i, sequence] = 1.  # set specific indices of results[i] to 1s
    return results

x_train = vectorize_sequences(train_data)
x_test = vectorize_sequences(test_data)
y_train = np.asarray(train_labels).astype('float32')
y_test = np.asarray(test_labels).astype('float32')

tbCallBack =keras.callbacks.TensorBoard(log_dir='./Graph',
                                        histogram_freq=2,
                                        write_graph=True,
                                        write_images=True)


model = models.Sequential()
model.add(layers.Dense(16, activation='relu', input_shape=(500,)))
model.add(layers.Dense(16, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

model.compile(optimizer='rmsprop',
                       loss='binary_crossentropy',
                       metrics=['acc'])

model.fit(x_train, y_train,
           epochs=5,
           batch_size=512,
           validation_data=(x_test, y_test),
           callbacks=[tbCallBack])


from keras.utils import plot_model
plot_model(model,show_shapes=True,to_file='model.png')