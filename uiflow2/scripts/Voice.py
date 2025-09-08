'''
  Mic and Speaker
'''
from M5 import *
import time
import struct
import math

###########
#
class Voice:
  #
  #
  def __init__(self):
    self.setVolume()
  #
  #
  def setVolume(self, x=1):
    Speaker.begin()
    Speaker.setVolumePercentage(x)
    Speaker.end()
  #
  #
  def record(self, sec=5):
    Mic.begin()
    rec_data = bytearray(8000 * sec)
    Mic.record(rec_data, 8000, False)
    while Mic.isRecording():
      time.sleep_ms(500)
    Mic.end()
    return rec_data
  #
  #
  def play(self, data):
    Speaker.begin()
    Speaker.playRaw(data, 8000)
    while Speaker.isPlaying():
      time.sleep_ms(500)
    Speaker.end()
  #
  #
  def calc_power(self, indata):
    indata2 = struct.unpack(f"{len(indata) / 2:.0f}h", indata)
    sqr_sum = [x*x for x in indata2]
    rms = math.sqrt(sqr_sum/len(indata2))
    power = 20 * math.log10(rms) if rms > 0.0 else -math.inf 
    return power

#################
#
def calc_power(indata):
  indata2 = struct.unpack(f"{len(indata) / 2:.0f}h", indata)
  sqr_sum = sum([x*x for x in indata2])
  rms = math.sqrt(sqr_sum/len(indata2))
  power = 20 * math.log10(rms) if rms > 0.0 else -math.inf 
  return power
#
#
def record(tm=10, thr=38.5):
    Mic.begin()
    ds=0.5
    tm0=time.time()+tm
    res=b""
    thr=34
    flag=False
    while time.time() < tm0:
      rec_data_ = bytearray(int(8000 * ds))
      Mic.record(rec_data_, 8000, False)
      while Mic.isRecording():
        time.sleep_ms(100)
      if calc_power(rec_data_) > thr:
        flag=True
        res +=rec_data_
      elif flag:
        Mic.end()
        return res
    Mic.end()
    return res
#
#
def play(data, sample_rate=8000):
  Speaker.begin()
  Speaker.setVolumePercentage(50)
  Speaker.playRaw(data, sample_rate)
  while Speaker.isPlaying():
    time.sleep_ms(500)
  Speaker.end()
  