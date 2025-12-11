# -*- coding: utf-8 -*-
#
#  PyWebScok Library
#  Communication Adaptor for WebSocket
#
#   Copyright(C) 2015, Isao Hara, AIST, All Right Reserved
#   Licensed under the MIT License.
#   http://www.opensource.org/licenses/MIT
#

################################
import sys
import os
import socket
import select
import time
import threading
import struct
import copy
import json

# for ssl
import ssl

# for WebSocket
import binascii
import random
from hashlib import sha1


DAY_A = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
MON_A = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


#def get_now_str():
#    lt=g_rtc.datetime()
#    return "%s, %02d %s %d %02d:%02d:%02d GMT" % (DAY_A[lt[3]], lt[2], MON_A[lt[1]-1], lt[0], lt[4], lt[5], lt[6])

def get_now_str():
    lt=list(time.localtime())
    return "%s, %02d %s %d %02d:%02d:%02d GMT" % (DAY_A[lt[6]], lt[2], MON_A[lt[1]-1], lt[0], lt[3], lt[4], lt[5])

#
# Raw Socket Adaptor
#
#   threading.Tread <--- SocketPort
#
class SocketPort(threading.Thread):
  #
  # Contsructor
  #
  def __init__(self, reader, name, host, port, ssl=False):
    threading.Thread.__init__(self)
    self.module_name=__name__+'.SocketPort'
    self.reader = reader
    if self.reader:
      self.reader.setOwner(self)
    self.name = name
    self.host = host
    self.port = port
    self.socket = None
    self.com_ports = []
    self.service_id = 0
    self.client_adaptor = True
    self.server_adaptor = None
    self.mainloop = False
    self.debug = False
    self.ssl = ssl

    if self.ssl == True:
      self.ssl_dir = "ssl/"
      self.ssl_cert = self.ssl_dir + "server.crt"
      self.ssl_key = self.ssl_dir + "server.key"
      #self.ssl_cert = self.ssl_dir + "certificate.pem"
      #self.ssl_key = self.ssl_dir + "private-key.pem"
      if not os.path.isfile(self.ssl_cert) or not os.path.isfile(self.ssl_key) :
        print("Cert or Key file not found.")
        self.ssl = False

      # for 2.7 or later
      #
      #self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
      #self.context.load_cert_chain(certfile=self.ssl_cert, keyfile=self.ssl_key)

  #
  #  Set values...
  #
  def setHost(self, name):
    self.host = name
    return 

  def setPort(self, port):
    self.port = port
    return 

  def setClientMode(self):
    self.client_adaptor = True
    return 

  def setServerMode(self):
    self.client_adaptor = False
    return 

  def setServer(self, srv):
    self.server_adaptor = srv
    return 

  def getCommand(self):
    try:
      return self.reader.command
    except:
      return None

  def shutdown(self, cmd):
    if self.socket :
        self.socket.close()
        self.socket=None
        #self.socket.shutdown(cmd)
    return
  #
  # Bind socket 
  #
  def bind(self):
    try:
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self.socket.bind((self.host, self.port))

    except socket.error:
      print("Socket error in bind")
      self.close()
      return 0

    except:
      print("Error in bind %s:%d" & (self.host, self.port))
      self.close()
      return -1

    return 1

  #
  # Connect
  #
  def connect(self, async_flag=True):
    if self.mainloop :
      return 1

    try:
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socket.connect((self.host, self.port))

    except socket.error:
      print("Socket error in connect")
      self.close()
      return 0

    except:
      print("Error in connect %s:%d "  % (self.host, self.port))
      self.close()
      return -1

    if async_flag :
      print("Start read thread %s" % self.name)
      self.start()

    return 1

  #
  #  Wait for comming data...
  #
  def wait_for_read(self, timeout=0.1):
    try:
      rready, wready, xready = select.select([self.socket],[],[], timeout)
      if len(rready) :
        return 1
      return 0
    except:
      self.terminate()
      return -1

  #
  # Receive data
  #
  def receive_data(self, bufsize=8192, timeout=1.0):
    data = None
    try:
      if self.wait_for_read(timeout) == 1  :
        data_ = self.socket.recv(bufsize)     # buffer size = 1024 * 8
        data = data_.decode()
        if len(data) != 0:
          return data
        else:
          return  -1

    except socket.error:
      print("socket.error in receive_data")
      self.terminate()

    except:
      self.terminate()

    return data

  #
  #  Thread oprations...
  #
  def start(self):
    self.mainloop = True
    if self.socket :
      threading.Thread.start(self)

  def run(self):
    if self.client_adaptor: 
      self.message_receiver()
    else:
      self.accept_service_loop()

  #
  #  Manage each service
  #
  def remove_service(self, adaptor):
     try:
       self.com_ports.remove(adaptor)
     except:
       pass

  #
  #  Event loop: this metho should be overwrite by suceessing classes
  #
  def accept_service_loop(self, lno=5, timeout=1.0):
    print("No accept_service_loop defined")

    return 

  #
  #  Background job ( message receiver )
  #
  def message_receiver(self):
    while self.mainloop:
      data = self.receive_data() 

      if data  == -1:
        self.terminate()

      elif data or data is None:
        self.reader.parse(data)

      else :
        print("Umm...: %s" % self.name)
        print(data)

    print("Read thread terminated: %s" % self.name)

  #
  #  close socket
  #
  def close_service(self):
    for s in  self.com_ports :
      s.terminate()

  #
  #  close socket (lower operation)
  #
  def close(self):
    while self.com_ports:
      sock=self.com_ports.pop()
      #sock.shutdown(socket.SHUT_RDWR)
      sock.shutdown(0)
      sock.close()

    if self.server_adaptor:
      self.server_adaptor.remove_service(self)

    if self.socket :
      self.socket.close()
      self.socket = None

  #
  #  Stop background job
  #
  def terminate(self):
    try:
      self.reader.terminate()
    except:
      pass
    self.close_service()
    self.mainloop = False
    self.close()

  #
  #  Send message
  #
  def send(self, msg, name=None):
    if not self.socket :
      print( "Error: Not connected")
      return None
    try:
      if type(msg) == str: msg=msg.encode()
      self.socket.sendall(msg)

    except socket.error:
      print( "Socket error in send")
      self.close()

  # 
  #  find
  #
  def readers(self):
    res = []
    for p in self.com_ports:
       res.append(p.reader)

    return flatten(res)


############################################
#  Server Adaptor
#     SocketPort <--- SocketServer
#
class SocketServer(SocketPort):
  #
  # Constructor
  #
  def __init__(self, reader, name, host, port, ssl=False, debug=False):
    SocketPort.__init__(self, reader, name, host, port, ssl)
    self.debug = debug
    self.module_name=__name__+'.SocketServer'

    self.setServerMode()
    self.cometManager = CometManager(self)
    self.bind()

  #
  # Accept new request, create a service 
  #
  def accept_service(self, flag=True):
    try:
      conn, addr = self.socket.accept()
      self.service_id += 1
      name = self.name+":service:%d" % self.service_id
      reader = self.reader.duplicate()

      if self.ssl == True:
        # for 2.7 or lator
        #sslconn = self.context.wrap_socket(conn, server_side=True)
        sslconn = ssl.wrap_socket(conn, server_side=True,
                     certfile=self.ssl_cert, keyfile=self.ssl_key)

        newadaptor = SocketService(self, reader, name, sslconn, addr)
      else:
        newadaptor = SocketService(self, reader, name, conn, addr)

      if flag :
        newadaptor.start()
      return newadaptor

    except:
      print("ERROR in accept_service")
      pass

    return None

  #
  #  Wait request from a client 
  #      [Overwrite super's method]
  #
  def accept_service_loop(self, lno=5, timeout=1.0):
    if self.ssl:
      print( "Wait for accept with SSL: %s(%s:%d)" % (self.name, self.host, self.port))
    else:
      print( "Wait for accept: %s(%s:%d)" % (self.name, self.host, self.port))
    self.socket.listen(lno)
    while self.mainloop:
      res = self.wait_for_read(timeout) 
      if res == 1:
        self.accept_service()
      elif res == -1:
        self.terminate()
      else:
        pass
    
    print( "Terminate all service %s(%s:%d)" % (self.name, self.host, self.port))
    self.close_service()
    self.close()
    print( "..Terminated")
    return 

  #
  #
  #
  def getServer(self):
    return self

  #
  #  Thread operations....
  #
  def run(self):
    self.accept_service_loop()

  #
  # 
  #
  def remove_service(self, adaptor):
     try:
       if len(self.com_ports) > 0:
         self.com_ports.remove(adaptor)
         print( "Terminate Service %s" % adaptor.name )
     except:
       pass

  def getComPorts(self, klass):
    res=[]
    try:
      for x in self.com_ports:
        if isinstance(x.reader.command, klass) : res.append(x)
    except:
      pass
    return res
  #
  #
  #
  def getWSList(self):
    res = []
    try:
      comports = self.getComPorts(WebSocketCommand)
      for port in comports:
        res.append(port.reader.command)
      return res
    except:
      print( "Error in getWSList()")
      return None

  def getWS(self, n):
    lst = self.getWSList()
    try:
      return lst[n]
    except:
      print( "Error: invalid index in getWS()")
      return None 
   
#
#  Service Adaptor
#
class SocketService(SocketPort):
  #
  # Constructor
  #
  def __init__(self, server, reader, name, sock, addr):
    SocketPort.__init__(self, reader, name, addr[0], addr[1])
    self.module_name=__name__+'.SocketService'
    self.socket = sock
    self.server_adaptor = server
    self.name=''
    server.com_ports.append(self)

  #
  # Threading...
  #
  def run(self):
    self.message_receiver()

  #
  #
  #
  def getServer(self):
    return self.server_adaptor

  #
  #
  #
  def terminate(self):
    self.mainloop=False
    return

#
#  Commands (Comet)
#
CloseCodeNum={
     'Normal':1000,
     'GoingAway':1001,
     'ProtocolError':1002,
     'UnsupportedData':1003,
     'Reserved':1004,
     'NoStatus':1005,
     'Abnormal':1006,
     'InvalidFrame':1007,
     'PolicyViolation':1008,
     'MessageTooBig':1009,
     'MandatoryExt.':1010,
     'InetranalError.':1011,
     'ServiceRestart.':1012,
     'TryAgain.':1013,
     'TLS_handshake.':1015,
}

Opcode={
     'ContinuationFrame.':0,
     'TextFrame.':1,
     'BinaryFrame.':2,
     'ConnectionCloseFrame.':8,
     'PingFrame.':9,
     'PongFrame.':10,
}

#
#  Foundmental reader class 
#
class CommReader:
  #
  # Constructor
  #
  def __init__(self, owner=None, command=None):
    self.module_name=__name__+'.CommReader'
    self._buffer = ""
    self.bufsize = 0
    self.current=0
    self.response=""
    self.owner = owner
    if command is None:
      self.command = CommCommand('')
    else:
      self.command = command
    self.debug = False

  #
  #  parse received data, called by SocketPort
  #
  def parse(self, data):
    if self.debug:
      print( data )
    if data : self.appendBuffer( data )
    self.checkBuffer()

  #
  #  Usually 'owner' is a controller
  #
  def setOwner(self, owner):
    self.owner = owner

  def setBuffer(self, buff):
    if self._buffer : del self._buffer
    self._buffer=buff
    self.bufsize = len(buff)
    self.current=0

  def getServer(self):
    return  self.owner.getServer()

  def getCommand(self):
    return self.command


 #
 #  duplicate...
 #
  def duplicate(self):
    reader = copy.copy(self)
    #reader = self
    if self.command:
      reader.command = copy.copy(self.command)
      #reader.command = self.command
      reader.command.reader = reader
    return reader

  #
  # Buffer operations
  #
  def appendBuffer(self, buff):
    self._buffer += buff
    self.bufsize = len(self._buffer)

  def skipBuffer(self, n=4, flag=1):
    self.current += n
    if flag :
      self._buffer = self._buffer[self.current:]
      self.current = 0
      self.bufsize = len(self._buffer)
    return 

  def clearBuffer(self, n=0):
    if n > 0 :
      self._buffer = self._buffer[n:]
      self.bufsize = len(self._buffer)
      self.current = 0
    else:
      if self._buffer : del self._buffer
      self._buffer = ""
      self.current = 0
      self.bufsize = 0

  #
  #  Main routine ?
  #
  def checkBuffer(self):
    try:
      if len(self._buffer) > self.current :
        res = self.command.checkMessage(self._buffer, self.current, self)
        if res == 0:
          return False
        self._buffer = self._buffer[res:]
        self.current = 0
        return True
      else:
        pass
    except:
      print( "ERR in checkBuffer")
      self._buffer=""
      pass

    return False
     
  #
  # Send response message
  #
  def send(self, flag=False):
    if self.owner :
      if type(self.response) == str:
        res=self.response.encode()
      else:
        res=self.response
      self.owner.send(res)
    else:
      print( "No owner" )

    if flag:
      self.owner.close()
    return
  #
  #
  #
  def sendResponse(self, res, flag=True):
    self.response = res
    self.send(flag)

  #
  # Append response message
  #
  def setResponse(self, msg):
    self.response += msg
    return

  #
  # Clear response message
  #
  def clearResponse(self):
    self.response=""
    return

  #
  #  extract data from self.buffer 
  #
  def read(self, nBytes, delFlag=1):
    start = self.current
    end = start + nBytes

    if self.bufsize < end :
      end = self.bufsize

    data = self._buffer[start:end]
    self.current = end

    if  delFlag :
      self._buffer =  self._buffer[end:]
      self.current =  0
    return data

  #
  #
  #
  def closeSession(self, flag=False):
    self.owner.close()
    if flag:
      self.owner.getServer().terminate()
    return

  #
  #
  def terminate(self):
    return


######################################
#  Reader class for Http
#
class HttpReader(CommReader):
  #
  # Constructor
  #
  def __init__(self, dirname="html"):
    CommReader.__init__(self, None, HttpCommand(dirname))
    self.dirname = dirname

    self.WSCommand = WebSocketCommand(None, None)
    self.WS_KEY = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    self.WS_VERSION = (8, 13)

    self.AlexaCommand = AlexaCommand(None, None)

    self.commands={
        '/hello' : self.hello,
        '/seat' : self.requestSeat,
        '/comet_request' : self.cometRequest,
        '/comet_event' : self.cometTrigger 
                  } 
    self.asr = None

  #
  #
  #
  def doProcess(self, header, data):
    self.clearResponse()
    cmd = header["Http-Command"]
    fname = header["Http-FileName"].split('?')

    if cmd == "GET":
      if 'Connection' in header and header['Connection'] == "Upgrade" and 'Upgrade' in header:
        if header['Upgrade'] == "websocket":
          self.webSocketRequest(header, fname[0])
        else:
          response = self.command.response404()
      else:
        contents = get_file_contents(fname[0], self.dirname)
        ctype = get_content_type(fname[0])
        if contents is None:
          response = self.command.response404()
        else:
          if ctype.startswith("image"):
            response = self.command.response200(ctype, contents)
          else:
            response = self.command.response200(ctype, contents.decode())
        self.sendResponse(response)

    elif cmd == "POST":
      #print("Request POST: %s" % fname[0])
      if fname[0] in self.commands:
        #print("CALL", self.commands[fname[0]])
        response = self.commands[fname[0]](data)
        if response: self.sendResponse(response)

      elif fname[0] == "/asr" :
        try:
          if 'audio/l16' in header['Content-Type'] :
            result = self.asr.request_asr(data)
            response = self.command.response200('application/json; charset=utf-8', result)

            self.sendResponse(response)
          else:
            esponse = self.command.response400()
            self.sendResponse(response)
        except:
          response = self.command.response400()
          self.sendResponse(response)
      else:
          contents = "Hello, No such action defined"
          response = self.command.response200("text/plain", contents)
          self.sendResponse(response)

    else:
      response = self.command.response400()
      self.sendResponse(response)

    return
  #
  #
  #
  def registerCommand(self, ctype, obj):
    self.commands[ctype] = obj

  #
  #
  #
  def webSocketRequest(self, header, fname):
    try:
      key = header['Sec-WebSocket-Key']
      version = header['Sec-WebSocket-Version']
      func = fname.split('/')[-1]

      responseHeaders = {}
      responseHeaders['Content-Type'] = 'text/plain'
      responseHeaders['Upgrade'] = 'websocket'
      responseHeaders['Connection'] = 'Upgrade'
      responseHeaders['Sec-WebSocket-Version'] = str(version)
      response_key = binascii.b2a_base64(sha1(key.encode('utf-8') + self.WS_KEY).digest())

      responseHeaders['Sec-WebSocket-Accept'] = response_key
      
      response = self.command.response101(responseHeaders, "")

      self.command = self.WSCommand.duplicate(self, func)
      self.sendResponse(response, False)
      try:
        self.command.init(func)
      except:
        pass

    except:
      self.sendResponse(self.command.response404())

  ###############
  # for SEAT-Alexa
  #
  def requestSeat(self, data):
    res = self.AlexaCommand.service(data)
    response = self.command.response200('application/json;charset=UTF-8', json.dumps(res))
    return response

  def hello(self, data):
    print("Hello:", data)
    response = self.command.response200('application/json;charset=UTF-8', json.dumps({"result": "OK"}))
    return response

  ###############
  # for COMET
  #
  def cometRequest(self, data):
    Data = parseData(data)
    if "id" in Data :
      self.registerHandler(Data)
      return None
    else:
      return self.command.response400()
      #response = self.command.response400()
      #self.sendResponse(response)

  #
  #
  #
  def cometTrigger(self, data):
    Data = parseData(data)
    res = {}
    if "id" in Data:
      self.callHandler(Data)
      res["result"] = "OK"
    else:
      res["result"] = "ERROR"

    res["date"] = get_now_str()
    return  self.command.response200("application/json", json.dumps(res))
    #response = self.command.response200("application/json", json.dumps(res))
    #self.sendResponse(response)

  #
  #
  #
  def registerHandler(self, data):
    server = self.getServer()
    server.cometManager.registerHandler(self, data['id'], data)
    return

  #
  #  for WebSocket
  #
  def callHandler(self, data):
    server = self.getServer()
    server.cometManager.callHandler(data['id'], data)
    return

  #
  #
  def terminate(self):
    try:
      self.asr.terminate()
    except:
      pass
    return

############################################
# CommCommand: parse the reveived message
#
class CommCommand:
  #
  #  Costrutor
  #
  def __init__(self, buff, rdr=None):
    self.module_name=__name__+'.ComCommand'
    self._buffer=buff
    self.bufsize = len(buff)
    self.reader = rdr

    self.offset=0
    self.cmdsize = 0

    self.encbuf=None
    self.encpos=0

  #
  #  for buffer
  #
  def setBuffer(self, buff):
    if self._buffer : del self._buffer
    self._buffer=buff
    self.bufsize = len(buff)
    self.offset=0

  def clearBuffer(self):
    self.setBuffer("")

  def appendBuffer(self, buff):
    self._buffer += buff
    self.bufsize = len(self.buff)

  def skipBuffer(self, n=0):
      #print( "call skipBuffer %d" % n )
      data = ""
      if self.bufsize > n :
        data = self._buffer[:n]
        self.setBuffer(self._buffer[n:])
      #print( data )
      return data

  #
  #  check message format (cmd encoded_args)
  #
  def checkMessage(self, buff, offset=0, reader=None):
    print("CommCommand.checkMessage")
    return None

  #
  # set/get operations...
  #
  def setReader(self, rdr):
    self.reader=rdr

  def getServer(self):
    if self.reader:
      return self.reader.getServer()
    return None

  def getComPorts(self):
    srvr=self.getServer()
    if srvr:
      return srvr.com_ports
    return None

  def getMyService(self):
    return self.reader.owner

  def getMyServiceName(self):
    try:
      return self.reader.owner.name
    except:
      print( "Error in getMyServiceName()")
      return None

  def getComPortNames(self):
    try:
      comports = self.getComPorts()
      res = map(lambda n:n.name, comports)
      return res
    except:
      print( "Error in getComPortNames()")
      return None

  def getCommandList(self):
    try:
      comports = self.getComPorts()
      res = map(lambda n:n.reader.command, comports)
      return res
    except:
      print( "Error in getCommandList()")
      return None

#############################################
#  Httpd  
#     CommCommand <--- HttpCommand
#
class HttpCommand(CommCommand):
  #
  # Constructor
  #
  def __init__(self, dirname=".", buff=''):
    CommCommand.__init__(self, buff)
    self.dirname=dirname
    self.module_name=__name__+'.HttpCommand'

  #
  #
  #
  def setRootDir(self, dirname):
    self.dirname=dirname

  #
  #
  #
  def checkMessage(self, buff, offset=0, reader=None):
    #print("HttpCommand.checkMessage")
    pos = self.parseHttpdHeader( buff, offset)
    if pos > 0 :
      self.reader.doProcess(self.header, self.data)
      return pos
    return 0

  #
  #
  #
  def parseHttpdHeader(self, buff, offset=0):
    #print("HttpCommand.parseHttpdHeader")
    self.header = {}
    self.data = ""

    pos =  buff[offset:].find("\r\n\r\n")

    if pos > 0:
      pos += offset + 4
      self.headerMsg = buff[offset:pos]
      self._buffer = buff[pos:]

      header = self.headerMsg.split("\r\n")
      cmds = header[0].split(' ')
      cmd = cmds[0].strip()
      fname = cmds[1].strip()
      if fname == "/" : fname = "/index.html"
      proto = cmds[2].strip()

      header.remove( header[0] )
      self.header = self.parseHeader(header)
      self.header["Http-Command"] = cmd
      self.header["Http-FileName"] = fname
      self.header["Http-Proto"] = proto

      if "Content-Length" in self.header :
        contentLen = int(self.header["Content-Length"])
        pos += contentLen
        self.data = self._buffer[:contentLen]
        if len(self.data) < contentLen:
          return 0
      return pos
    return 0

  #
  #  parse HTTP Header
  #
  def parseHeader(self, header):
    res = {}
    for h in header:
      if h.find(":") > 0 :
        key, val = h.split(':', 1)
        res[key.strip()] = val.strip()
    return res

  ##################################
  # Generate response message
  #
  def response101(self, header, contents=""):
    date = get_now_str()
    res  = "HTTP/1.1 101 Switching Protocols\r\n"
    res += "Date: "+date+"\r\n"
    for key,val in header.items():
      res += key+": "+val+"\r\n"
    res += "Content-Length: "+str(len(contents.encode()))+"\r\n"
    res += "\r\n"
    res += contents

    return res

  def response200(self, ctype, contents):
    date = get_now_str()
    res  = "HTTP/1.0 200 OK\r\n"
    res += "Date: "+date+"\r\n"
    res += "Content-Type: "+ctype+"\r\n"
    if type(contents) is str:
      res += "Content-Length: "+str(len(contents.encode()))+"\r\n"
      res += "\r\n"
      return res + contents
    else:
      res += "Content-Length: "+str(len(contents))+"\r\n"
      res += "\r\n"
      return res.encode() + contents

  def response404(self):
    date = get_now_str()
    res  = "HTTP/1.0 404 Not Found\r\n"
    res += "Date: "+date+"\r\n"
    res += "\r\n"
    return res

  def response400(self):
    date = get_now_str()
    res  = "HTTP/1.0 400 Bad Request\r\n"
    res += "Date: "+date+"\r\n"
    res += "\r\n"
    return res

################################################
#  WebSocket Command
#     CommCommand <--- WebSocketCommand
#
class WebSocketCommand(CommCommand):
  #
  # Constructor
  #
  def __init__(self, reader, func, buff=''):
    CommCommand.__init__(self, buff, reader)
    self.module_name = __name__+'.WebSocketCommand'
    self.func_name = func
    self.current_data_frame = 0x01
    self.data=""
    self.requestReturn=False
    self.seqMgr = seqManager()
    self.syncQ  = syncQueue()
    self.terminateFlag  = False
    self.manager  = None

  #
  #
  #
  def setFunction(self, func):
    self.func_name = func
  #
  #
  #
  def duplicate(self, rdr, func=""):
    command = copy.copy(self)
    #command = self
    command.reader = rdr
    command.func_name = func
    return command
  #
  #
  #
  def getWSList(self):
    res = []
    try:
      comports = self.getComPorts()
      for port in comports:
        if isinstance(port.reader.command, WebSocketCommand) :
          res.append(port.reader.command)
      return res
    except:
      print( "Error in getWSList()")
      return None

  #
  #
  #
  def parseHeader(self, buff):
    fragment = True
    mask_data = None

    val = buff[:2]

    if ord(val[0]) & 0x80 :
      fragment = False

    data_type = ord(val[0]) &0x0f
    masked = ord(val[1]) & 0x80
    buflen = ord(val[1]) & 0x7f
    size = 2
 
    if buflen == 126:
      buflen = struct.unpack_from('>H', buff[2:])[0]
      size += 2
    elif buflen == 127:
      buflen = struct.unpack_from('>Q', buff[2:])[0]
      size += 8

    if masked :
      mask_data = buff[size:size+4]
      size += 4

    return [size, fragment, data_type, mask_data, buflen]

  def json_decode(self, msg):
    try:
      res = json.loads(msg)
    except:
      res = msg
    return res

  #
  #  data_type 
  #     0x00:  Continue
  #     0x01:  Text
  #     0x02:  Binary
  #     0x01:  Text
  #     0x08:  Close
  #     0x09:  Ping
  #     0x0a:  Pong
  #
  def checkMessage(self, buff, offset=0, reader=None):
    try:
      size, fragment, data_type, mask_data, datalen = self.parseHeader(buff)

      if datalen > len(buff) : return 0

      if data_type == 0x01:  # Text
        if self.current_data_frame == data_type: self.data=""
        self.data += self.parseDataFrame(size, mask_data, datalen, buff)


        #
        # call function...
        if not fragment :
          self.data = self.json_decode(self.data)

          if type(self.data) == dict :
            if  'Status' in self.data and self.data['Status'] == "Opening" :
              self.sendDataFrame('{"Status": "Opened"}')
              self.connection_id=self.data['ID']

            elif 'seq' in self.data and 'result' in self.data :
              self.seqMgr.putResult(self.data['seq'], self.data['result'])

            elif 'request_seq' in self.data and 'args' in self.data :
              self.applyFunction(self.data['request_seq'], self.data['args'])

            elif 'result' in self.data :
              if self.requestReturn : self.syncQ.put(self.data['result'])

            elif 'op' in self.data and 'topic' in self.data:
              self.terminateFlag  = True
              if not self.manager :
                self.manager = ROS_BridgeManager(self)

              if 'msg' in self.data :
                self.manager.call( self.data )
              else:
                self.manager.add( self.data )

            else:
              self.callOtherFunc(self.data)

          else:
            self.callFunction(self.data)

      elif data_type == 0x02:  # Binary
        if self.current_data_frame == data_type: self.data=""
        self.data += self.parseDataFrame(size, mask_data, datalen, buff)
        #
        # call function...
        if not fragment : self.callFunction(self.data)

      elif data_type == 0x00:  # Continue
        self.data += self.parseDataFrame(size, mask_data, datalen, buff)
        if not fragment : self.callFunction(self.data)
        pass

      elif data_type == 0x08:  # Close
        print( "Catch Closeing Frame")
        self.reader.closeSession(self.terminateFlag)

      elif data_type == 0x09:  # Ping
        print( "Catch PingFrame" )
        self.sendPongFrame()

      elif data_type == 0x0a:  # Pon
        print( "Catch PongFrame")

      else:
        pass

      if not fragment : self.data = ""
      size += datalen
      return size
    except:
      print( "Error in WebSocket.checkMessage")

    return 0

  def callOtherFunc(self,data):
    print( "Error: invalid message")
    
  #
  #
  #
  def parseDataFrame(self, size, mask_data, data_len, buff):
    data = buff[size:size+data_len]
    data_text =""
    for i in range(data_len):
      if mask_data :
        data_text += chr(ord(data[i]) ^ ord(mask_data[i % 4]))
      else:
        data_text += chr(ord(data[i]))
    return data_text

  #
  #
  #
  def sendDataFrame(self, msg, masked=False):
    if masked :
      buf = self.genMaskedDataFrame(msg)
    else:
      buf = self.genDataFrame(msg)
    self.reader.sendResponse(buf, False)
    return
  #
  #
  #
  def sendCloseFrame(self):
    buf = "\x88\x00"
    self.reader.sendResponse(buf)
    return

  #
  #
  #
  def sendPingFrame(self):
    buf = "\x89\x00"
    self.reader.sendResponse(buf,False)
    return

  #
  #
  #
  def sendPongFrame(self):
    buf = "\x8a\x00"
    self.reader.sendResponse(buf, False)
    return

  #
  #
  #
  def genDataFrame(self, msg, opcode="\x81"):
    buf=opcode
    slen = len(msg)
    if slen > 65535: 
      buf = buf+chr(127)+struct.pack('>Q',slen)+msg
    elif slen > 125:
      buf = buf+chr(126)+struct.pack('>H',slen)+msg
    else:
      buf = buf +chr(slen) +msg
    return buf
  #
  #
  #
  def genMaskedDataFrame(self, msg, opcode="\x81"):
    mask = ""
    for i in range(4):
      mask += chr(int(random.random()*256))

    buf=opcode
    slen = len(msg)
    if slen > 65535: 
      buf = buf+chr(127 | 0x80)+struct.pack('>Q',slen)
    elif slen > 125:
      buf = buf+chr(126 | 0x80)+struct.pack('>H',slen)
    else:
      buf = buf +chr(slen | 0x80)

    buf += mask
    for i in range(slen):
      buf += chr(ord(msg[i]) ^ ord(mask[i % 4]))

    return buf

  #
  # call own method
  #
  def callFunction(self, msg):
    if self.func_name in dir(self.__class__):
      return getattr(self.__class__, self.func_name)(self, msg)
    else:
      print( "No such method %s" % self.func_name)

  def applyFunction(self, seq, msg):
    if self.func_name in dir(self.__class__):
      return getattr(self.__class__, self.func_name)(self, msg, seq)
    else:
      print( "No such method %s" % self.func_name)

  #
  # 
  #
  def funcCall(self, funcname,  *args, **keyargs):
     seq = self.seqMgr.request()
     if type(seq) == int and seq >= 0 :
       cmd={"seq":seq, "func": funcname, "args": args}
       cmdData = json.dumps(cmd)
       self.sendDataFrame(cmdData) 
       res=self.seqMgr.getResult(seq)
       print( res )
     else:
       print( "Too much request!")

     return
  #
  #
  def getResult(self, seq):
     return self.seqMgr.getResult()

  #
  #
  #
  def waitResult(self, tout=None):
     res = None
     if self.requestReturn :
       res=self.syncQ.get(tout)
       self.requestReturn=False
     return res

  def call_snap(self, cmd, *args, **keyargs):
     self.requestReturn=True
     self.sendDataFrame(cmd) 
     return self.waitResult()

  def snap_broadcast(self, msg, requestRet=True, tout=None):
     self.requestReturn=requestRet
     self.sendDataFrame('this.broadcast("'+msg+'")') 
     return self.waitResult(tout)

  def push_value_to_snap(self, data, *args, **keyargs):
     self.requestReturn=False
     self.sendDataFrame('this.push_value("'+data+'")') 
     return 

  #
  # Sample Function...
  #
  def echo(self, msg):
    if msg == "Close":
      self.sendCloseFrame()
    else:
      self.sendDataFrame(msg)
    return

  def hello(self, msg):
    print(msg)


#############################################
#
#
class AlexaCommand(CommCommand):
  #
  # Constructor
  #
  def __init__(self, reader, func, buff=''):
    CommCommand.__init__(self, buff, reader)
    self.module_name = __name__+'.AlexaCommand'
    self.func_name = func
    self.data=""
    self.requestReturn=False
    self.seqMgr = seqManager()
    self.syncQ  = syncQueue()
    self.terminateFlag  = False

  def service(self, data):
    msg = json.loads(data)
    if msg['request']['type'] == 'LaunchRequest' :
      res = self.start_service("サービスをはじめます")
    elif msg['request']['type'] == 'IntentRequest' :
      if msg['request']['intent']['name'] == 'RequestRobot' :
        slots = msg['request']['intent']['slots']
        command = None
        subject = None
        action = None
        if 'value' in slots['command']:
          command = slots['command']['value'].encode("utf-8")
        if 'value' in slots['subject']:
          subject = slots['subject']['value'].encode("utf-8")
        if 'value' in slots['action']:
          action = slots['action']['value'].encode("utf-8")

        if command :
          res = self.mkResponse(command + "を実行します", False)
        elif subject :
          if action :
            res = self.mkResponse(subject + "を" + action, False)
          else:
            res = self.mkResponse("目的語は、" + subject + "です", False)
        elif action:
            res = self.mkResponse("アクションは、" + action + "です", False)
        else:
          res = self.mkResponse("コマンドが見つかりません", False)

      elif msg['request']['intent']['name'] == 'SearchItemIntent' :
        name = msg['request']['intent']['slots']['ItemName']['value'].encode("utf-8")
        res = self.mkResponse(name + "を探します", False)
      elif msg['request']['intent']['name'] == 'SearchIntent' :
        res = self.mkResponse("何を探すのですか？", False)
      elif msg['request']['intent']['name'] == 'Greeting' :
        res = self.mkResponse("こんにちは", False)
      elif msg['request']['intent']['name'] == 'Thanks' :
        res = self.mkResponse("どういたしまして", False)
      else:
        res = self.start_service("はい")
    elif msg['request']['type'] == 'SessionEndedRequest' :
      print(msg)
      res = self.end_service("終わりました")

    return res

  def start_service(self, msg):
    return self.mkResponse(msg, False);

  def end_service(self, msg):
    return self.mkResponse(msg, True);

  def mkResponse(self, msg, endSession=True):
    res = {}
    _response={}

    res["version"] = "1.0";
    _response['outputSpeech']=self.mkOutputSpeech(msg)
    if not endSession : _response['shouldEndSession']=False

    res["response"] = _response;

    return res

  def mkOutputSpeech(self, msg):
    out={}
    out['type'] = 'SSML'
    out['ssml'] = "<speak>"+msg+"</speak>"
    return out


######################################33
#     CometManager
#
class CometManager:
  #
  # Constructor
  #
  def __init__(self, server):
    self.server = server
    self.long_pollings = {}

  #
  #
  #
  def resieter(self, reader, id):
    self.long_pollings[id] = reader

  #
  #
  #
  def registerHandler(self, reader, id, data):
    self.long_pollings[id] = reader
    return

  #
  #
  #
  def callHandler(self, id, data):
    res = {}
    res['date'] = get_now_str()
    res['message'] = "Push message"

    if id == "all":
      self.response_all(res, "application/json")
    else:
      self.response(id, res, "application/json")
    return

  #
  #
  #
  def response(self, id, json_data, ctype="text/plain"):
    reader = self.long_pollings[id]
    if reader :
      json_data['id'] = id
      json_data['result'] = ""

      contents = json.dumps(json_data)
      responsemsg = reader.command.response200(ctype, contents)
      reader.sendResponse(responsemsg)
      self.long_pollings[id] = None

  #
  #
  #
  def response_all(self, json_data, ctype="text/plain"):
    keys = self.long_pollings.keys()
    for k in  keys :
      self.response(k, json_data, ctype)

##################################################
#
# Functoins
#
def get_file_contents(fname, dirname="."):
  contents = None
  try:
    with open(dirname+fname,'rb') as file:
      contents = file.read()
  except:
    print( "ERROR!! get_file_contents [%s, %s] " % (dirname, fname))
    pass
  return contents

#
#
#
def get_content_type(fname):
  imgext=["jpeg", "gif", "png", "bmp"]
  htmext=["htm", "html"]
  ctype = "text/plain"
  ext=fname.split(".")[-1]
  if htmext.count(ext) > 0:
    ctype = "text/html"
  elif ext == "txt" :
    ctype = "text/plain"
  elif ext == "css" :
    ctype = "text/css"
  elif ext == "js" :
    ctype = "text/javascript"
  elif ext == "csv" :
    ctype = "text/csv"
  elif ext == "jpg" :
    ctype = "image/jpeg"
  elif ext == "ico" :
    ctype = "image/x-icon"
  elif imgext.count(ext) > 0:
    ctype = "image/"+ext
  else:
    pass
  return ctype

#
#
#
def parseData(data):
  res = {}
  ar = data.split("&")
  for a in ar:
    try:
      key, val = a.split("=")
      res[key.strip()] = val.strip()
    except:
      pass
  return res

#
#
#
class syncQueue:
  def __init__(self):
    self.cv = threading.Condition()
    self.queue = []

  def put(self, item):
    with self.cv:
      self.queue.append(item)
      self.cv.notifyAll()

  def get(self, timeout=None):
    with self.cv:
      while not len(self.queue) > 0:
        self.cv.wait(timeout)
        return None

      return self.queue.pop(0)

class seqManager():
  def __init__(self, n=10):
    self.seq_queue=[]
    self.sq=[]
    self.released=[]
    self.next_id=0
    for i in range(n):
      self.sq.append( syncQueue() )
      if i < n-1:
        self.seq_queue.append(i+1)
      else:
        self.seq_queue.append(-1)
        self.last_id=i

  def request(self):
    if self.seq_queue[self.next_id] == -1: return None
    res = self.next_id
    self.next_id = self.seq_queue[self.next_id]
    self.seq_queue[res] = -1
    return res

  def release(self,val):
    if self.last_id == val: return
    if self.seq_queue[val] == -1:
      self.seq_queue[self.last_id] = val
      self.last_id = val
    else:
      print( "Error in Release[%d]" % val)
    return

  def registCommand(self):
    seq = self.request()
    return seq

  def putResult(self, seq, val):
    self.sq[seq].put(val)
    return

  def getResult(self,val):
    res = self.sq[val].get()
    self.release(val)
    return res


def flatten(lst):
  res=[]
  for x in lst:
    if type(x) is list:
      res += flatten(x)
    else:
      res.append(x)
  return res

def findall(func, lst):
  res = []
  for x in lst:
    if func(x) : res.append(x)
  return res

####################
def response101(header="text/plain", contents=""):
  date = get_now_str()
  res  = "HTTP/1.1 101 Switching Protocols\r\n"
  res += "Date: "+date+"\r\n"
  for key,val in header.items():
    res += key+": "+val+"\r\n"
  res += "Content-Length: "+str(len(contents.encode()))+"\r\n"
  res += "\r\n"
  res += contents
  return res

def response200(ctype="text/plain", contents=""):
  date = get_now_str()
  res  = "HTTP/1.0 200 OK\r\n"
  res += "Date: "+date+"\r\n"
  res += "Content-Type: "+ctype+"\r\n"
  if type(contents) is str:
    res += "Content-Length: "+str(len(contents.encode()))+"\r\n"
    res += "\r\n"
    return res + contents
  else:
    res += "Content-Length: "+str(len(contents))+"\r\n"
    res += "\r\n"
    return res.encode() + contents

def response404():
  date = get_now_str()
  res  = "HTTP/1.0 404 Not Found\r\n"
  res += "Date: "+date+"\r\n"
  res += "\r\n"
  return res

def response400():
  date = get_now_str()
  res  = "HTTP/1.0 400 Bad Request\r\n"
  res += "Date: "+date+"\r\n"
  res += "\r\n"
  return res

def response500():
  date = get_now_str()
  res  = "HTTP/1.0 500 Internal Server Error\r\n"
  res += "Date: "+date+"\r\n"
  res += "\r\n"
  return res

######################################
#  HTTP Server
#
def create_httpd(num=80, top="/sd/html/", command=WebSocketCommand, host="", ssl=False):
  if type(num) == str: num = int(num)
  reader = HttpReader(top)
  #reader.WSCommand = command(reader,None)
  return SocketServer(reader, "Web", host, num, ssl)
#  return SocketServer(reader, "Web", socket.gethostname(), num)


