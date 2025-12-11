'''
  Google Text-to-Speech
'''
from M5 import *
import requests2
import binascii
import time
import socket
import select
import json

from comm import Command
import util

_EffectsProfile=('wearable', 'handset', 'headphone', 'small-bluetooth-speaker', 'medium-bluetooth-speaker', 'large-home-entertainment', 'large-automotive', 'telephony')

JP_FEMAIL=['ja-JP-Chirp3-HD-Aoede', 'ja-JP-Chirp3-HD-Kore', 'ja-JP-Chirp3-HD-Leda', 'ja-JP-Chirp3-HD-Zephyr']
JP_MALE=['ja-JP-Chirp3-HD-Charon', 'ja-JP-Chirp3-HD-Fenrir', 'ja-JP-Chirp3-HD-Orus', 'ja-JP-Chirp3-HD-Puck']

###################
#
def set_volume(volume=50):
    Speaker.begin()
    Speaker.setVolumePercentage(volume)
    Speaker.end()

def play_audio(data, sample_rate=8000, volume=50):
    Speaker.begin()
    Speaker.setVolumePercentage(volume)
    Speaker.playRaw(data, sample_rate)
    while Speaker.isPlaying():
        time.sleep_ms(100)
    Speaker.end()
    return

####################
# 
class Gtts(Command):
    #
    #
    def __init__(self):
        self._endpoint = "https://texttospeech.googleapis.com/v1/text:synthesize"
        self.key_config = util.load_conf("/flash/apikey.txt")
        self._apikey = self.key_config.get('GOOGLE_SPEECH_KEY')

        self._lang = "ja-JP"
        self._speakingRate = "1.2"
        self._ssmlGender = "FEMALE"
        self._voiceName = "ja-JP-Wavenet-B"
        self._pitch = "5.0"
        self._volumeGain = "0"
        self._sampleRate = "8000"
        self._effectsProfileId = None
        self.udp=None
        self.request = None
        self.set_volume(50)
        self.parent=None
        self.response=None
    #
    #
    def setup_upd(self, port=10800):
        self.udp=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind(("0.0.0.0", port))
        self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.poll = select.poll()
        self.poll.register(self.udp, select.POLLIN)
        return
    
    def set_config(self, conf):
        self._lang = util.get_config(conf, "google/lang", "ja-JP")
        self._speakingRate = util.get_config(conf, "google/speakingRate", "1.2")
        self._ssmlGender = util.get_config(conf, "google/ssmlGender","FEMALE")
        self._voiceName = util.get_config(conf, "google/voiceName","ja-JP-Wavenet-B")
        self._pitch = util.get_config(conf, "google/pitch","5.0")
        self._volumeGain = util.get_config(conf, "google/volumeGain","0")
        self._sampleRate = util.get_config(conf, "google/sampleRate","8000")
        self._effectsProfileId = util.get_config(conf, "google/effectsProfileId","")
        #print("Gtts:", self._lang, self._speakingRate,self._ssmlGender,self._voiceName,self._pitch,self._volumeGain,self._sampleRate,self._effectsProfileId)
        return
    #
    #
    def text2speech(self, text):
        url = self._endpoint+"?key="+self._apikey
        headers = {  'Content-Type' : 'application/json; charset=utf-8' }
        data = {
                 "input": { "text" : text },
                 "voice" : {
                             'languageCode' : self._lang    # en-US, ja-JP, fr-FR
                            , 'name' : self._voiceName
                            , 'ssmlGender' : self._ssmlGender # MALE, FEMALE, NEUTRAL
                       },
                 'audioConfig': {
                          'audioEncoding':'LINEAR16'  # LINEAR16, MP3, OGG_OPUS
                          #'audioEncoding':'MP3'  # LINEAR16, MP3, OGG_OPUS
                        , 'speakingRate' : self._speakingRate   # [0.25: 4.0]
                        , 'pitch' : self._pitch         # [ -20.0: 20.0]
                        , 'volumeGainDb' : self._volumeGain
                        , 'sampleRateHertz' : self._sampleRate # default is 22050
                      }
            }
        
        if self._effectsProfileId in _EffectsProfile:
            if self._effectsProfileId == 'telephony':
                data['audioConfig']['effectsProfileId'] = 'telephony-class-application'
            else:
                data['audioConfig']['effectsProfileId'] = self._effectsProfileId + "-class-device"
        try:
            response = requests2.post(url, data=json.dumps(data).encode('utf-8'), headers=headers)
            return response
        except:
            return None
    #
    #
    def set_volume(self, x):
        self._volume = x
        set_volume(self._volume)
        return
    #
    #
    def speak(self, data):
        response=self.text2speech(data)
        res_=True
        if response:
            try:
                result=response.json()
                audio=binascii.a2b_base64(result['audioContent'])
                if audio[:4] == b'RIFF':
                    if audio[8:12] == b'WAVE':
                        audio = audio[44:]
                if self.parent:
                    self.parent.face.start_talk()
                play_audio(audio, volume=self._volume)
                if self.parent:
                    self.parent.face.stop_talk()              
            except:
                try:
                    print(result)
                except:
                    print("Unknown error")
                res_ = False
            res_ = True
            response.close()
        return res_
    #
    #
    def set_speaker(self, data):
        self._voiceName = data
        return True
    #
    #
    def execute(self, data):
        print("start tts ", data)
        return self.speak(data)
    #
    #
    def set_request(self, data):
        self.request = data
        return True
    #
    #
    def check_request(self):
        if self.request:
            #print("Google TTS")
            self.show_message("応答中…")
            request = self.request.replace("!", "!\n")
            request = self.request.replace("?","?\n" )
            req=request.replace("\n", "。").split("。")
            for msg in req:
                if msg:
                    res = self.speak(msg)
                    if res is False:
                        self.show_message("音声合成失敗…", 0xff8888)
            self.request=None
            self.show_message()
        return
    #
    #
    def update(self):
        if self.udp:
            #if self.poll.poll(0.1)
            recv_data = self.udp.recvfrom(1024)
            self.execute(recv_data[0])
    #
    #
    def reset(self):
        machine.reset()
        return
    
    def show_message(self, msg='', color=0xffff00):
      if self.parent:
          self.parent.print_info(msg, color)

