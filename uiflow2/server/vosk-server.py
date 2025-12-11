#

import comm
import vosk
import binascii
import json


class VoskRecognizer:
  def __init__(self, model_path="vosk-model-ja-0.22", sample_rate=16000):
    self.model=vosk.Model(model_path)
    self.sample_rate=sample_rate
    self.recognizer=vosk.KaldiRecognizer(self.model, sample_rate)

  def execute(self, data):
    #print("start execution")
    res=self.recognizer.AcceptWaveform(data)
    return self.recognizer.Result()
    #if res:
    #  return self.recognizer.Result()
    #else:
    #  return self.recognizer.PartialResult()

  def request(self, data):
    print("==== request=== ")
    try:
      bdata = binascii.a2b_base64(data)
      res=self.execute(bdata)
      response=json.loads(res)
      recog_txt=response['text'].replace(' ', '')
      return comm.response200('application/json', recog_txt)
    except:
      import traceback
      traceback.print_exc()
      return comm.response500()


if __name__ == '__main__':
    vosk=VoskRecognizer()
    web = comm.create_httpd(8000, "html")
    web.reader.registerCommand('/vosk', lambda data: vosk.request(data))
    web.start()

