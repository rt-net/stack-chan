#
# Google Speech-to-Text
import sys, os
from M5 import Mic
import time
import json
import binascii
import requests2
from comm import Command

import math
import struct
import util

####################
#
class Gasr(Command):
  #
  #  Constructor
  def __init__(self, node=None, language='ja-JP'):
    self._endpoint = 'https://speech.googleapis.com/v1/speech:recognize'
    self.key_config = util.load_conf("/flash/apikey.txt")
    self._apikey = self.key_config.get('GOOGLE_SPEECH_KEY')

    self._lang=language

    self._buffer = b''
    self._audio = b''
    self.audio_segments = []

    self._sample_width=2
    self._frame_rate=8000
    self._channels=1

    self._prebuf= b''
    self.request=None
    self.parent = None
    self.response = None
  #
  def set_config(self, conf):
    self._lang = util.get_config(conf, "google/lang", "ja-JP")
    self._frame_rate = util.get_config(conf, "google/sampleRateHertz",8000)
    #print("Gasr:", self._lang, self._frame_rate)
    return
  #
  #
  def calc_power(self, indata):
    indata2 = struct.unpack(f"{len(indata) / 2:.0f}h", indata)
    sqr_sum = sum([x*x for x in indata2])
    rms = math.sqrt(sqr_sum/len(indata2))
    power = 20 * math.log10(rms) if rms > 0.0 else -math.inf
    return power
  #
  #  Request Google Voice Recognition
  def request_speech_recog(self, data):
    url = self._endpoint+"?key="+self._apikey
    headers = {  'Content-Type' : 'application/json; charset=utf-8' }

    audio_data = binascii.b2a_base64(data, newline=False)

    request_data = {
             "config" : { 'languageCode' : self._lang    # en-US, ja-JP, fr-FR
                          , 'encoding' : 'LINEAR16'
                          , 'sampleRateHertz' : self._frame_rate
                          },
             "audio"  : {
                        'content' : audio_data.decode('utf-8')
                          }
            }
    try:
      self.response = requests2.post(url, json=request_data, headers=headers)
      return self.response.text
    except:
      return ""
  #
  #
  def record_audio(self, tm=5, thr=41, max_count=1 ):
      if not Mic.begin():
        print("Mic not work")
        return []
      ds=0.5
      tm0=time.time()+tm
      res=b""
      flag=False
      count=0
      while time.time() < tm0:
        rec_data_ = bytearray(int(8000 * ds))
        Mic.record(rec_data_, 8000, False)
        while Mic.isRecording():
          time.sleep_ms(50)
        power = self.calc_power(rec_data_)
        #print(power)
        if power > thr:
          flag=True
          res +=rec_data_
          count=0
        elif flag:
          res += rec_data_
          count += 1
          if count > max_count:
            Mic.end()
            return res
      Mic.end()
      return res
  #
  #
  def do_process(self, max_seconds=10, thr=41, max_count=0):
    if not self._apikey :
      print("No API key")
      return
    data=self.record_audio(max_seconds, thr, max_count)

    if len(data) > 0:
      self.show_message("音声認識中…")
      res_=self.request_speech_recog(data)
      try:
        response=json.loads(res_)
        res=response['results'][0]['alternatives'][0]['transcript']
        print("RESPONSE:", res)
        return { 'result': res , 'error': ''}
      except:
        print("==== Fail")
        #return None
      return  { 'result': '', 'error': 'Fail to recoginze' }
    else:
      print("==== No sound")
      return None
  #
  #
  def execute(self, data):
    if isinstance(data, str):
      try:
        val = eval(data)
        return self.do_process(*val)
      except:
        return { 'result': '', 'error': 'Invalid params' }
    return False
  #
  #
  def set_request(self, data):
    self.request = data
    return True
  #
  #
  def check_request(self):
    if self.request:
      self.show_message("音声入力…", 0x8888ff)
      param=json.loads(self.request)
      #print(param)
      res=self.do_process(param['max_seconds'], param['threshold'], param['max_count'])
      if res is None:
        self.request=None
      self.show_message("")
      if self.response:
        self.response.close()
        self.response=None
      return res
    return False
  
  def show_message(self, msg='', color=0xffff00):
    if self.parent:
      self.parent.print_info(msg, color)

####################
#
def main():
   recog = Gasr()
   for n in range(5):
     print("==== Start speech...")
     recog.do_process()

if __name__ == '__main__':
  main()
