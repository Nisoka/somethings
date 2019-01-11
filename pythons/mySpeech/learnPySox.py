import sox
import numpy as np
import matplotlib.pyplot as plt
import librosa.display

tfm = sox.Transformer()
spectrum = np.array(tfm.power_spectrum('/home/nan/my.wav'))

librosa.display.specshow(spectrum)
# plt.specgram(spectrum)
plt.show()

