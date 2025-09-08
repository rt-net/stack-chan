#
'''
  Web Server
'''
from M5 import *
import machine
import time
import comm

#####################
#
class WebServer:
  #
  #
  def __init__(self, port=80, top="/sd/html"):
    if type(port) == str: port = int(port)
    self.port = port
    self.reader = comm.HttpReader(top)
    self.server = comm.SocketServer(self.reader, "Web", "", port)
    self.started=False
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
    self.server.spin_once(timeout)
    return#
