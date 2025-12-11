#
#
import os
from M5 import *
import requests2

import json
import util

#
#
class ChatGPT(object):
  #
  #  Constructor
  #
  def __init__(self):
    self._endpoint = "https://api.openai.com/v1/responses"
    self.conf = util.load_conf("/flash/apikey.txt")
    self._apikey = self.conf.get('OPENAI_KEY')

    #self._endpoint = "http://localhost:1234/v1/responses"
    #self._apikey = 'lm-studio'

    self.model = 'gpt-5'
    self.chat_history=[]
    self.prompt = ""
  #
  #
  def reset_chat(self):
    self.chat_history=[]
  #
  #
  def set_prompt(self, prompt):
    self.prompt=prompt

  #
  #
  def gen_chat_content(self, txt, role="user"):
    res={
          "content" : txt,
          "role": role
        }
    self.chat_history.append(res)
    return res

  #
  #
  def get_system_chat_content(self, result):
    try:
      res=""
      for output in result['output']:
        if 'content' in output:

          for part in output['content']:

            try:
              if part['type'] == 'output_text':
                res += part['text']
            except:
              pass
      self.gen_chat_content(res, 'assistant')
      return res
    except:
      print("ERRPR", result)
      return "Fail"
  #
  #
  def request_openai(self, text):
    url = self._endpoint
    headers = {
        'Authorization': f'Bearer {self._apikey}',
        'Content-Type' : 'application/json; charset=utf-8' }

    self.gen_chat_content(text)
    data = {
      'model': self.model,
      'input': self.chat_history,
      #'tools': [{"type": "mcp", "server_label": "web-search" }]
      #'tools': [{"type": "web_search_preview"}],
      'tools': [{"type": "web_search"}],
    }
    if self.prompt:
      data["input"].insert(0,
          {
            'role': "developer",
            'content': self.prompt
          })
    try:
      result = requests2.post(url, data=json.dumps(data).encode('utf-8'), headers=headers)
      response = result.json()
      return response
    except:
      print ('Error', data, json.dumps(data).encode())
      return ""
  #
  #
  def talk(self, data):
    response=self.request_openai(data)
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

def main():
  con = ChatGPT()
  con.request("明日の東京では、傘は必要ですか？")

if __name__ == '__main__':
  main()