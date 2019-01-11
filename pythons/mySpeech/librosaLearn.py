import librosa
import librosa.display
from librosa.core.spectrum import stft
import scipy.io.wavfile as sciwavpy
import numpy as np
import matplotlib.pyplot as plt

def sciwavfile_simulat_librosa_load(wavPath):
    sr, y = sciwavpy.read(wavPath)

    # --------------------------
    # simulate the librosa
    # --------------------------
    # Invert the scale of the data
    scale = 1./float(1 << ((8 * 2) - 1))
    # Construct the format string
    fmt = '<i{:d}'.format(2)
    # Rescale and format the data buffer
    y =  scale * np.frombuffer(y, fmt).astype(float)
    return y, sr

# NOTE：
# librosa 没有指定帧窗口， 导致输出的特征并不是25ms 帧窗, 10ms 偏移
# 1162/364 = 3.2 ==> 79.8(80ms帧窗口) 但是在哪里指定的呢？
# 所以librosa取特征还是有点问题阿
def librosa_compute_spec(y=None, sr = 1600, S=None, n_fft=2048, hop_length=512, power=1):
    if S is not None:
        # Infer n_fft from spectrogram shape
        n_fft = 2 * (S.shape[0] - 1)
    else:
        # Otherwise, compute a magnitude spectrogram from input
        # 计算的幅度普, 希望abs, 然后在取 power次方
        S = np.abs(stft(y, n_fft=n_fft, hop_length=hop_length))**power

    return S, n_fft

def librosa_get_logmelspectrogram(y, sr):
    # generate a melspectrogram
    melspec = librosa.feature.melspectrogram(y, sr, n_fft=1024, hop_length=512, n_mels=128)
    print(melspec.shape)
    logmelspec = librosa.power_to_db(melspec)

    kwargs = dict()
    kwargs.setdefault('cmap', librosa.display.cmap(logmelspec))
    kwargs.setdefault('rasterized', True)
    kwargs.setdefault('edgecolors', 'None')
    kwargs.setdefault('shading', 'flat')
    # plt out th e logmelspec
    plt.subplot(3, 1, 1)
    plt.pcolormesh(logmelspec, **kwargs)



def librosa_get_logspectrogram(y, sr):
    spec, n_fft = librosa_compute_spec(y, n_fft=1024, hop_length=512)
    print(spec.shape)
    logspec = librosa.power_to_db(spec)
    kwargs = dict()
    kwargs.setdefault('cmap', librosa.display.cmap(logspec))
    kwargs.setdefault('rasterized', True)
    kwargs.setdefault('edgecolors', 'None')
    kwargs.setdefault('shading', 'flat')

    plt.subplot(3, 1, 2)
    plt.pcolormesh(logspec, **kwargs)




from python_speech_features import sigproc

def psf_compute_logpowspec(signal,samplerate=16000,winlen=0.025,winstep=0.01,
                                        nfilt=26,nfft=512,lowfreq=0,highfreq=None,preemph=0.97,
                                        winfunc=lambda x:np.ones((x,))):
    # Note: nfft must bigger than winlen
    # otherwise, will lost some info

    # 1 pre emphasis 预加重
    signal = sigproc.preemphasis(signal,preemph)
    # signal == (185876,) 16000

    # 2 数据分帧
    # (sample_rate = 16000,  winlen=0.025,      winstep=0.01)
    #  采样率 16000          窗 0.025s(400)     窗移 0.01s(100)
    frames = sigproc.framesig(signal, winlen*samplerate, winstep*samplerate, winfunc)
    # print(frames.shape)
    # (1161, 400)

    # 第11帧数据是完全相等的, 说明没有进行计算, 只是进行分帧处理.
    # signal 计算的第11帧数据为 400*10 - 400*11
    # frames 分帧好的第11帧数据为 frames[10]
    # print(signal[1600:1610])
    # print(frames[10,:10])

    # 3 计算能量谱
    # nfft: 傅立叶频率数量,
    # 最终每帧数据会得到 (nfft/2+1) 个频率幅度向量.
    # 1.0 / NFFT   *  numpy.square(magspec(frames, NFFT))
    # 归一化？        取平方
    # pspec = sigproc.powspec(frames,nfft)

    # 3 直接计算log spec, 内部通过 sigproc.powspec 计算了能量谱
    logpspec = sigproc.logpowspec(frames, nfft).T
    # energy = np.sum(pspec,1) # this stores the total energy in each frame
    # energy = np.where(energy == 0,np.finfo(float).eps,energy) # if energy is zero, we get problems with log
    return logpspec


def psf_get_logspectrogram(y, sr):
    logpspec = psf_compute_logpowspec(y, nfft=512)
    print(logpspec.shape)
    kwargs = dict()
    kwargs.setdefault('cmap', librosa.display.cmap(logpspec))
    kwargs.setdefault('rasterized', True)
    kwargs.setdefault('edgecolors', 'None')
    kwargs.setdefault('shading', 'flat')

    plt.subplot(3, 1, 3)
    plt.pcolormesh(logpspec, **kwargs)












# ===================== Nouse =================
def librosa_show_logmelSpecAndWave(wavPath):
    y, sr = librosa.load(wavPath, sr=None)
    melspec = librosa.feature.melspectrogram(y, sr, n_fft=1024, hop_length=512, n_mels=128)
    logmelspec = librosa.power_to_db(melspec)

    plt.figure()
    plt.subplot(2, 1, 1)
    librosa.display.waveplot(y, sr)
    plt.title(wavPath)
    plt.subplot(2, 1, 2)
    librosa.display.specshow(logmelspec, sr=sr, x_axis='time', y_axis='mel')
    plt.title('mel Spectrogram1')
    plt.tight_layout()




def load_and_save():
    filename = librosa.util.example_audio_file()
    y_raw, sr_raw = librosa.load(filename)
    print(y_raw)
    print(sr_raw)               # 22050
    librosa.output.write_wav("./example.wav", y_raw, sr_raw)

    # resample as 8k, is ok!
    sr = 8000
    y_8k, sr_8k = librosa.load(filename, sr)
    print(y_8k)
    print(sr_8k)
    librosa.output.write_wav("./example-8k.wav", y_8k, sr_8k)

    librosa_show_logmelSpecAndWave("./example.wav")
    librosa_show_logmelSpecAndWave("./example-8k.wav")
    
    


if __name__ == '__main__':
    plt.figure()
    # librosa_show_logmelSpecAndWave('/home/nan/git-nan/code/speech-tools/denoise/rnnoise-master/sample-out-raw.wav')
    # librosa_show_logmelSpecAndWave('/home/nan/my.wav')
    # load_and_save()

    y, sr = librosa.load('/home/nan/my.wav', sr=None)
    print(y.shape, sr)
    librosa_get_logspectrogram(y, sr)
    psf_get_logspectrogram(y, sr)

    plt.show()
