#
'''
  Web Server
'''
from M5 import *
import machine
import time
import os
import comm
import json

#####################
#
class WebServer:
  #
  #
  def __init__(self, port=80, top="/flash/html"):
    if type(port) == str: port = int(port)
    self.port = port
    self.reader = comm.HttpReader(top)
    self.server = comm.SocketServer(self.reader, "Web", "", port)
    self.started=False
    self.registerCommand("/get_file", self.get_content)
    self.registerCommand("/save_file", self.save_content)
    self.registerCommand("/get_file_list", self.get_file_list)
  #
  #
  def renew(self):
    self.server.stop()
    self.server=comm.SocketServer(self.reader, "Web", "", self.port)
    self.started=False
    return
  #
  #
  def registerCommand(self, name, func):
    if type(func) is str:
      try:
        func = eval(func)
      except:
        print("ERROR to register:", func)
        return

    self.server.reader.registerCommand(name, func)
    return
  
  def get_content(self, data):
    param = json.loads(data)
    #print(param)
    response = {}
    with open(param['file_name'], 'r') as file:
      response['data'] = file.read()
    return response
  
  def save_content(self, data):
    param = json.loads(data)
    res = False
    with open(param['file_name'], 'w') as file:
      file.write(param['data'])
      res = True
    return res
  
  def get_file_list(self, data):
    param = json.loads(data)
    dirname=param['dir_name']
    dir_list=os.listdir(param['dir_name'])
    flst=[]
    dlst=[]

    for x in dir_list:
        if (os.stat(f"{dirname}/{x}")[0] & 0x8000) == 0:
            dlst.append(x)
        else:
            flst.append(x)
    response = {'dir_list': dlst, "file_list": flst}
    return response
  #
  #
  def is_started(self):
    return self.started
  #
  #
  def start(self):
    self.server.start()
    self.started=True
    return
  #
  #
  def stop(self):
    try:
      self.server.terminate()
      self.started=False
    except:
      pass
    return
  #
  #
  def update(self, timeout=0.1):
    if self.started:
      self.server.spin_once(timeout)
    return
  
  def toggle_state(self):
    if self.started:
      self.started = False
      return "Web Off"
    else:
      self.started = True
      return "Web On"
    
