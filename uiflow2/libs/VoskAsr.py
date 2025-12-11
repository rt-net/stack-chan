#
'''
  Vosk: Speech-to-Text
'''
import sys, os
from M5 import Mic
import time
import json
import binascii
import requests2

import math
import struct
import util
from comm import Command

###############
#
class VoskAsr(Command):
  #
  #  Constructor
  def __init__(self, host="192.168.0.100", language='ja-JP'):
    self.host = host
    self._endpoint = "http://%s:8000/vosk" % self.host
    self._lang=language

    self._buffer = b''
    self._audio = b''
    self.audio_segments = []

    self._sample_width=2
    self._frame_rate = 8000
    self._channels = 1

    self._prebuf = b''
    self.silent_power = 38
    self.silence = bytearray(8000*5)
    
    self.parent = None
    self.request = None
  #
  #
  def calc_power(self, indata):
    indata2 = struct.unpack(f"{len(indata) / 2:.0f}h", indata)
    sqr_sum = sum([x*x for x in indata2])
    rms = math.sqrt(sqr_sum/len(indata2))
    power = 20 * math.log10(rms) if rms > 0.0 else -math.inf 
    return power
  #
  #
  def get_silent_power(self, len=10):
    powers_=[]
    count=0
    for x in range(len):
      val=self.calc_power(self.record_audio_time(2))
      if val > 0:
        powers_.append(val)
        if count >= 5:
          break
    self.silent_power = sum(powers_)/count
    print(self.silent_power)
    return self.silent_power
  #
  #
  def record_silence(self, tm=5):
    self.silence=self.record_audio_time(tm)
    return
  #
  #  Request Google Voice Recognition
  def request_speech_recog(self, data):
    url = self._endpoint
    headers = {  'Content-Type' : 'application/json; charset=utf-8' }
    audio_data = binascii.b2a_base64(data, newline=False)
    request_data = audio_data.decode()
    try:
      response = requests2.post(url, json=request_data, headers=headers)
      return response.text
    except:
      print("Error in rewuest")
      return None
  #
  #
  def record_audio(self, tm=10, thr=-1):
      Mic.begin()
      ds=0.5
      tm0=time.time()+tm
      res=b""
      flag=False
      if thr < 0: thr = self.silent_power
      while time.time() < tm0:
        rec_data_ = bytearray(int(8000 * ds))
        Mic.record(rec_data_, 8000, False)
        while Mic.isRecording():
          time.sleep_ms(100)
        if self.calc_power(rec_data_) > thr:
          flag=True
          res +=rec_data_
        elif flag:
          res += self.silence
          Mic.end()
          return res
      Mic.end()
      return res
  #
  #
  def record_audio_time(self, tm):
    Mic.begin()
    rec_data_ = bytearray(int(8000 * tm))
    Mic.record(rec_data_, 8000, False)   
    while Mic.isRecording():
      time.sleep_ms(500)
    Mic.end()
    return rec_data_
  #
  #
  def do_process(self, max_seconds=10, thr=-1):
    data=self.record_audio(max_seconds, thr)
    print("Reuqest ASR")
    if len(data) > 0:
      self.show_message("音声認識中…")
      try:
        res=self.request_speech_recog(data)
        if res is None: return None
        print("RESPONSE:", res)
        return { 'result': res , 'error': ''}
      except:

        print("==== Fail")
        pass
      return { 'result': '', 'error': 'Fail to recoginze' }
    else:
      print("==== No sound")
    return None
  #
  #
  def run(self):
    while True:
      self.do_process()
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
          res=self.do_process(param['max_seconds'], param['threshold'])
          if res is None:
            self.request=None
          self.show_message("")
          return res
      return False
  
  def show_message(self, msg='', color=0xffff00):
    if self.parent:
        self.parent.print_info(msg, color)
