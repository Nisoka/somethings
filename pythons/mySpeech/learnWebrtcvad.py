import webrtcvad

vad = webrtcvad.Vad()
# 0, 1 ,2, 3
# 0 is the least aggressive about filtering out non-speech, 
# 3 is the most aggressive
vad.set_mode(0)
# The WebRTC VAD only accepts 16-bit mono PCM audio, 
# sampled at 8000, 16000, or 32000 Hz. 
# A frame must be either 10, 20, or 30 ms in duration:
sample_rate = 16000
frame_duration = 10
frame = bytearray([ b'\x00\x00' for i in range(int(sample_rate * frame_duration/1000)) ])
print(vad.is_speech(frame, sample_rate))


