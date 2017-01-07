import pyaudio
import audioop
import mido

mido.set_backend('mido.backends.rtmidi')

output = mido.open_output()

# CHUNK = 256
CHUNK = 1024

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 50 # set for how many seconds it is active
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

maxRMS = 8000 # adjust according to the input device used, noise etc.
lastMax = 0
maxMIDI = 0

averageLast = []
maxAvgLast = 50

def retAverage(last):

    global averageLast

    if len(averageLast) == 5:
        del averageLast[-1]
        averageLast = [last] + averageLast
    else:
        averageLast = [last] + averageLast

    total = 0
    for item in averageLast:
        total += item

    return total/len(averageLast)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    rms = audioop.rms(data, 2)
    if rms > lastMax:
        print 'lastMax', rms
        lastMax = rms

    if rms < maxRMS:
        midiVal = (rms * 127) / maxRMS
        print midiVal
        if midiVal > maxMIDI:
            maxMIDI = midiVal
            print maxMIDI

        output.send(mido.Message('control_change', control=1, value=retAverage(midiVal)))

stream.stop_stream()
stream.close()
p.terminate()
