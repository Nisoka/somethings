

samples_per_sec = 16000
frames_per_sec = 100
samples_per_frame = samples_per_sec//frames_per_sec
context_frames = 25

nInput = samples_per_sec*(2*context_frames + 1)

INPUT_SHAPE = (nInput, 1) # sample_len x 1, just the one channel signal
train_speaker_cnt = 1000