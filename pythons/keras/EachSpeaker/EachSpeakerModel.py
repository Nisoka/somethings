from keras.applications.xception import Xception
from keras.preprocessing import image
from keras.models import Model
from keras.layers import Dense, GlobalAveragePooling2D, Conv2D
from keras.layers import Input, Conv1D, MaxPooling1D, Flatten
from keras.layers.core import Reshape, Lambda
from keras import backend as K
import keras
from keras.utils.vis_utils import plot_model

import ds_constant as c

import math

kW1 = 300
dW1 = 10
mp1 = 5
kW2 = 10
dW2 = 1
mp2 = 5


# the conv1d shape changes
#
nout1 = math.floor((c.nInput-kW1)/dW1)+1
nout2 = math.floor(nout1/mp1)
nout3 = math.floor((nout2-kW2)/dW2)+1
nout4 = math.floor(nout3/mp2)


print(nout1, nout2, nout3, nout4)


def SpeakerFeatureModel(input_shape=c.INPUT_SHAPE):


    # if signal 16kHz
    # ==> 1s -- 16000, so 300 will be (1s * 1000 ms)*300/16000 == 18.75

    input = Input(shape=input_shape, name='input')
    x = Conv1D(filters=20, kernel_size= 300, strides=10, padding='valid', activation='relu', name='conv_1')(input)
    x = MaxPooling1D(pool_size = 5, strides = 5)(x)   # no overlap
    x = Conv1D(filters=20, kernel_size= 10, strides=1, padding='valid', activation='relu', name='conv_2')(x)
    x = MaxPooling1D(pool_size = 5, strides = 5)(x)   # no overlap
    x = Flatten()(x)
    # x = Reshape((nout4*20))(x)

    print(x.shape)
    x = Dense(100, activation='relu', name='embedding')(x)

    return input, x




def SpeakerIdentityModel(train_speaker_cnt=c.train_speaker_cnt, model_name='SpeakerIdentity'):
    input, x = SpeakerFeatureModel()
    # identity layer
    x = Dense(train_speaker_cnt, activation='softmax', name='identitySoftmax')(x)
    identityModel = Model(inputs=input, outputs=x, name=model_name)
    print(identityModel.summary())
    return identityModel

def EachSpeakerVerifyModel(model_name='EachVerify'):
    input, x = SpeakerFeatureModel()
    x = Dense(2, activation='softmax', name='verifySotmax')(x)
    eachVerfiyModel = Model(inputs=input, outputs=x, name=model_name)
    return eachVerfiyModel


def ConvertIdentityToEachVerify(identity_weight=None, verify_weight=None, model_name='EachVerify'):
    identity_model = SpeakerIdentityModel(c.train_speaker_cnt)
    if identity_weight is not None:
        identity_model.load_weights(identity_weight)

    # shared layers
    input = identity_model.get_layer('input')
    embedding = identity_model.get_layer('embedding')

    # verify layer
    x = Dense(2, activation='softmax', name='verifySotmax')(embedding)


    eachVerfiyModel = Model(inputs=input, outputs=x, name= model_name)

    if verify_weight is not None:
        eachVerfiyModel.save_weights(verify_weight)

    return eachVerfiyModel



if __name__ == "__main__":
    model = SpeakerIdentityModel()
    model.save_weights("./SpeakerIdentity.h5")







