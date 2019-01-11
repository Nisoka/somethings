from keras.applications.xception import Xception
from keras.preprocessing import image
from keras.models import Model
from keras.layers import Dense, GlobalAveragePooling2D
from keras.layers.core import Reshape, Lambda
from keras import backend as K
import keras
from keras.utils.vis_utils import plot_model

model_name = "Xception-innovem"
softmax_size = 4775
# 构建不带分类器的预训练模型
base_model = Xception(weights='imagenet', include_top=False)

inputs = base_model.input
# 添加全局平均池化层
x = base_model.output
# shape: [batch_size, 4, frames/16, 512]
x = GlobalAveragePooling2D(name='avg_pool')(x)

# want to change the mean to lstm
# average on the num_frames, then get
# [batch_size, frames, 2048] -> [batch_size, 1, 2048]
# x = Lambda(lambda y: K.mean(y, axis=1), name='average')(x)

# affine from 2048 -> 512
x = Dense(512, name='affine')(x)  # .shape = (BATCH_SIZE * NUM_FRAMES, 512)

# normalize on the sample??
embeddings = Lambda(lambda y: K.l2_normalize(y, axis=1), name='ln')(x)

softmax_out = Dense(softmax_size, activation='softmax', name='softmax')(x)

Xception_innovem = Model(inputs=inputs, outputs=[embeddings, softmax_out], name=model_name)

print(Xception_innovem.summary())
plot_model(Xception_innovem, to_file='model.png',show_shapes=True)

# tbCallBack =keras.callbacks.TensorBoard(log_dir='./Graph_xception',
#                                         histogram_freq=2,
#                                         write_graph=True,
#                                         write_images=True)


