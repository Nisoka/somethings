from keras.callbacks import LearningRateScheduler
lr_base = 0.001
epochs = 250
lr_power = 0.9
def lr_scheduler(epoch, mode='power_decay'):
    '''if lr_dict.has_key(epoch):
        lr = lr_dict[epoch]
        print 'lr: %f' % lr
    '''
    if mode is 'power_decay': # original lr scheduler
        lr = lr_base * ((1 - float(epoch) / epochs) ** lr_power)
    if mode is 'exp_decay': # exponential decay
        lr = (float(lr_base) ** float(lr_power)) ** float(epoch + 1) # adam default lr
    if mode is 'adam':
        lr = 0.001
    if mode is 'progressive_drops': # drops as progression proceeds, good for sgd
        if epoch > 0.9 * epochs:
            lr = 0.0001
        elif epoch > 0.75 * epochs:
            lr = 0.001
        elif epoch > 0.5 * epochs:
            lr = 0.01
        else:
            lr = 0.1
        print('lr: %f' % lr)

    return lr


# 学习率调度器
scheduler = LearningRateScheduler(lr_scheduler)
# 这是用在 直接使用 model.fit 方法中，作为一个回调函数， 让fit在拟合过程中根据自己的epoch进行的
# 但是并不适用于train_on_batch 方法。

# import keras.backend as K
# sgd = SGD(lr=0.1, decay=0, momentum=0.9, nesterov=True)
# K.set_value(sgd.lr, 0.5 * K.get_value(sgd.lr))

# ---------------------
# 作者：韋頁
# 来源：CSDN
# 原文：https://blog.csdn.net/hanshuobest/article/details/78882334
# 版权声明：本文为博主原创文章，转载请附上博文链接！