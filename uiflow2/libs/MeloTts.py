'''
  Melo TTS on LLM-Module
'''
import os, sys, io
import M5
from M5 import *
from module import LlmModule
import time
import comm

##############
#
class MeloTts:
    #
    #
    def __init__(self):
        self.llm = LlmModule(2, tx=17, rx=18)
        while not (self.llm.check_connection()):
            time.sleep(0.5)
        self.llm.sys_reset(True)
        self.llm.audio_setup(cap_volume=0.5, play_volume=0.15, request_id='audio_setup')
        self.llm.melotts_setup(model='melotts-ja-jp', input='tts.utf-8.stream', enoutput=False, enkws='', request_id='melotts_setup')
    #
    #
    def talk(self, text, tm=10000):
        self.llm.melotts_inference(self.llm.get_latest_melotts_work_id(), text, tm, 'melotts_inference')

####################
TTS=None
#
#
def init_tts():
    global TTS
    TTS=MeloTts()
    return TTS
#
#
def talk(text, tm=3000):
    global TTS
    if TTS:
        TTS.talk(text, tm)
        return comm.response200('application/json', json.dumps({"result": "OK"}))
    else:
        print("No tts interface")
        return comm.response400()
