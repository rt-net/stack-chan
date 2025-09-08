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
    self.conf = util.load_conf("/sd/apikey.txt")
    self._apikey = self.conf['OPENHRI_KEY']

    self._lang=language

    self._buffer = b''
    self._audio = b''
    self.audio_segments = []

    self._sample_width=2
    self._frame_rate=8000
    self._channels=1

    self._prebuf= b''
    self.request=None
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

    response = requests2.post(url, json=request_data, headers=headers)
    return response.text
  #
  #
  def record_audio(self, tm=5, thr=41, max_count=1 ):
      Mic.begin()
      ds=0.5
      tm0=time.time()+tm
      res=b""
      flag=False
      count=0
      while time.time() < tm0:
        rec_data_ = bytearray(int(8000 * ds))
        Mic.record(rec_data_, 8000, False)
        while Mic.isRecording():
          time.sleep_ms(100)
        if self.calc_power(rec_data_) > thr:
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
      res_=self.request_speech_recog(data)
      response=json.loads(res_)
      try:
        res=response['results'][0]['alternatives'][0]['transcript']
        print("RESPONSE:", res)
        return { 'result': res , 'error': ''}
      except:
        print("==== Fail")
        pass
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
          param=json.loads(self.request)
          print(param)
          res=self.do_process(param['max_seconds'], param['threshold'], param['max_count'])
          self.request=None
          return res
      return None
####################
#
def main():
   recog = Gasr()
   for n in range(5):
     print("==== Start speech...")
     recog.do_process()

if __name__ == '__main__':
  main()
