# coding: utf-8
'''
  For Voicevox engine: Text-to-speech
'''
from M5 import *
import sys
import requests2
import time
from comm import Command
import json
import struct
import binascii

#########
#
def play_audio(data, sample_rate=8000, volume=50):
  Speaker.begin()
  Speaker.setVolumePercentage(volume)
  Speaker.playRaw(data, sample_rate)
  while Speaker.isPlaying():
    time.sleep_ms(100)
  Speaker.end()
  return

##############
#
class Voicevox(Command):
    #
    #
    def __init__(self, host="192.168.0.100", id=1):
        self.header = {"Content-Type": "application/json"}
        self.result_wav_file="audio.wav"
        self.query=""
        self.setUrl(host, id)
        self.requesting=False
        self._volume = 50
        self.request = ""
        self.parent = None
    #
    #
    def setUrl(self, host=None, id=1):
        if host: self.host=host
        self.id=id
        #self.query_url="http://%s:50021/audio_query?speaker=%d" % (self.host, self.id)
        #self.synth_url="http://%s:50021/synthesis?speaker=%d" % (self.host, self.id)
        self.synth_url="http://%s:8000/tts" % (self.host)
        return
    #
    #
    def set_speaker(self, id=1):
        if isinstance(id, str):
            self.id = int(id)
        else:
            self.id=id
        return self.id
    
    def text2speech(self, txt):
        data={'data': txt, 'speaker': self.id}
        response = requests2.post(self.synth_url, data=json.dumps(data).encode(), headers=self.header)
        return response
    #
    #
    def speak(self, txt):
        result = False
        if self.requesting:
            return result    
        self.requesting=True
        res = self.text2speech(txt)
        if res and res.status_code == 200:
            result=res.json()
            audio=binascii.a2b_base64(result['audio'])
            self.play_wav(audio)
            result = True
        else:
            print("Fail to synthesize")
        self.requesting=False
        return result
    #
    #
    def execute(self, txt):
        return self.speak(txt)
    #
    #
    def play_wav(self, data, rate=24000):
        if self.parent:
            self.parent.face.start_talk()
        if data[:4].decode() == 'RIFF' and data[8:12].decode() == "WAVE":
            fmt=struct.unpack("H", data[20:22])[0]
            start=44
            if fmt != 1:
                print("Data is not Liner PCM")
                return
            rate=struct.unpack("I", data[24:28])[0]
            play_audio(data[start:], rate, self._volume)
        else:
            print("Unknown format")
            play_audio(data, rate, self._volume)

        if self.parent:
            self.parent.face.stop_talk()
        return
    
    #
    #
    def set_request(self, data):
        self.request = data
        return True
    #
    #
    def check_request(self):
        if self.request:
            self.show_message("応答中…")
            request = self.request.replace("!", "!\n")
            request = self.request.replace("?","?\n" )
            req = request.replace("\n", "。").split("。")
            for msg in req:
                if msg:
                    self.speak(msg)
            self.request=None
            self.show_message()
        return
    #
    #
    def show_message(self, msg='', color=0xffff00):
      if self.parent:
          self.parent.print_info(msg, color)
