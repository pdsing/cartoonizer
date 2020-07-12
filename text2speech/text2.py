from gtts import gTTS
import os
tts = gTTS(text='Hi. This is Paramdeep. The best product for text to speech is the google text to speech. Is it able to generate a good female voice?', lang='en-us')
tts.save("good.wav")