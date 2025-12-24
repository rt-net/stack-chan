'''
Copyright 2025 Isao Hara, RT Corporation.

Licensed under the Apache License, Version 2.0 (the “License”);
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an “AS IS” BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.

'''
import os
from M5 import *
import requests2

import json
import util


class Gemini(object):
  #
  #  Constructor
  #
  def __init__(self):
    self._endpoint = "https://generativelanguage.googleapis.com/v1beta/models"
    self.conf = util.load_conf("/flash/apikey.txt")
    self._apikey = self.conf.get('GEMINI_KEY')

    self.model = "/gemini-2.5-flash:generateContent"
    self._lang = 'ja-JP'
    self.chat_history=[]
    self.prompt = ""
  #
  #
  def reset_chat(self):
    self.chat_history=[]
    return
  
  def set_prompt(self, prompt):
    self.prompt=prompt
    return
  #
  #
  def gen_chat_content(self, txt, role="user"):
    res={
          "parts" : [{ "text": txt }],
          "role": role
        }
    self.chat_history.append(res)
    return res

  #
  #
  def get_system_chat_content(self, result):
    try:
      res=result['candidates'][0]['content']['parts'][0]['text']
      self.gen_chat_content(res, 'model')
      return res
    except:
      print(result)
      return "失敗しました"
  #
  #
  def request_gemini(self, text):
    url = self._endpoint+self.model
    headers = { 'x-goog-api-key': self._apikey,
                'Content-Type' : 'application/json; charset=utf-8' }

    self.gen_chat_content(text)

    data = {
      "contents": self.chat_history,
    }
    if self.prompt:
      data["system_instruction"] = {
          "parts" : [{
           "text": self.prompt
         }],
         "role" : "model"
      }
    #
    #
    data["tools"] = [
            { "url_context": {} },
            { "google_search": {} }
            ]
    try:
      result = requests2.post(url, data=json.dumps(data).encode('utf-8'), headers=headers)
      response = result.json()
      return response
    except:
      print(result.json())
      print ('Error', data, json.dumps(data).encode())
      return ""
  #
  #
  def talk(self, data):
    response=self.request_gemini(data)
    if response:
      return response
    return None
  #
  #
  def request(self, txt):
    result = self.talk(txt)
    if result:
      return self.get_system_chat_content(result)
    return ""
  
#
#
def main():
  from Gtts import GoogleTextToSpeech
  from Gasr import GoogleSpeechRecog
  gtts_client= GoogleTextToSpeech()
  recog = GoogleSpeechRecog()


  gemini = Gemini()
  gemini.reset_chat()
  reset_flag=False
  while True:
    print("＝＝＝＝ 話しかけてください")
    sample_text=recog.speech_recognition()
    if sample_text is None: continue
    if sample_text == 'さようなら': break
    if sample_text == 'ありがとう':
      reset_flag=True

    result=gemini.request(sample_text)
    if result:
      print("RESPONSE:", result)
      gtts_client.speak(result.replace('*', ''))

    if reset_flag:
      gemini.reset_chat()
      reset_flag=False

#
#
if __name__ == '__main__':
  main()
