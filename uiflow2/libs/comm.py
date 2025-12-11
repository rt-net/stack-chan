# -*- coding: utf-8 -*-
#
#  PyWebScok Library
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
import json

from util import get_now_str, mount_sd
import _thread
import gc

######
# Thread Class
###
class Thread:
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
        self.target = target
        self.args = args
        self.kwargs = {} if kwargs is None else kwargs

    #def __delete__(self):
    #    _thread.exit()
  
    def start(self):
        try:
          _thread.start_new_thread(self.run, ())
        except:
          self.run()

    def run(self):
        self.target(*self.args, **self.kwargs)


#def start_thread(obj):
#  _thread.start_new_thread(obj.run, ())
#
#def stop_thread():
#  _thread.exit()
#
# Raw Socket Adaptor
#
#   threading.Tread <--- SocketPort
class SocketPort(Thread):
  #
  # Contsructor
  def __init__(self, reader, name, host, port):
    super().__init__(self)
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
  #
  #  Set values...
  def setClientMode(self):
    self.client_adaptor = True
    return 
  #
  #
  def setServerMode(self):
    self.client_adaptor = False
    return 
  #
  #
  def setServer(self, srv):
    self.server_adaptor = srv
    return 
  #
  #
  def getCommand(self):
    try:
      return self.reader.command
    except:
      return None
  #
  #
  def shutdown(self, cmd):
    if self.socket :
        self.socket.close()
        self.socket=None
    return
  #
  # Bind socket 
  def bind(self):
    try:
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self.socket.bind((self.host, self.port))
    except:
      print("Error in bind %s:%d" & (self.host, self.port))
      self.close()
      return -1
    return 1
  #
  # Connect
  def connect(self, async_flag=False):
    if self.mainloop :
      return 1
    try:
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socket.connect((self.host, self.port))
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
  def wait_for_read(self, timeout=1.0):
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
  def receive_data(self, bufsize=8192, timeout=10.0):
    data = None
    try:
      if self.wait_for_read(timeout) == 1  :
        data_ = self.socket.recv(bufsize)     # buffer size = 1024 * 8
        data = data_.decode()
        if len(data) != 0:
          return data
        else:
          return  -1
    except:
      print("Error in receive_data")
      self.terminate()
    return data
  #
  #  Thread oprations...
  def start(self):
    self.mainloop = True
    if self.socket :
      Thread.start(self)
  #
  #
  def run(self):
    if self.client_adaptor: 
      self.message_receiver()
    else:
      self.accept_service_loop()
  #
  #  Manage each service
  def remove_service(self, adaptor):
     try:
       self.com_ports.remove(adaptor)
     except:
       pass
  #
  #  Event loop: this metho should be overwrite by suceessing classes
  def accept_service_loop(self, lno=5, timeout=1.0):
    print("No accept_service_loop defined")
    return 
  #
  #  Background job ( message receiver )
  def message_receiver(self, timeout=1.0):
    while self.mainloop:
      #print("-- message_recv")
      data = self.receive_data(timeout=timeout)

      if data  == -1:
        self.terminate()
        return
      elif data or data is None:
        if data is None or self.reader.parse(data):
          self.mainloop=False
      else :
        print("Umm...: %s" % self.name)
        print(data)
    #print("terminate")
    gc.collect()
    gc.mem_free()
    self.terminate()
    return
  #
  #  close socket
  def close_service(self):
    for s in  self.com_ports :
      s.terminate()
  #
  #  close socket (lower operation)
  def close(self):
    while self.com_ports:
      sock=self.com_ports.pop()
      sock.shutdown(0)
      sock.close()

    if self.server_adaptor:
      self.server_adaptor.remove_service(self)

    if self.socket :
      self.socket.close()
      self.socket = None
  #
  #  Stop background job
  def terminate(self):
    #print("Call terminate", self)
    try:
      self.reader.terminate()
    except:
      pass
    self.close_service()
    self.mainloop = False
    self.close()
  #
  #  Send message
  def send(self, msg, name=None):
    if not self.socket :
      print( "Error: Not connected")
      return None

    try:
      if type(msg) == str: msg=msg.encode()
      self.socket.sendall(msg)
    except:
      print( "Socket error in send")
      self.close()
  # 
  #  find
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
  def __init__(self, reader, name, host, port, debug=False):
    SocketPort.__init__(self, reader, name, host, port)
    self.debug = debug
    self.module_name=__name__+'.SocketServer'

    self.setServerMode()
    self.bind()
    self.socket.listen(3)
    gc.enable()

    self.poll=select.poll()
  #
  # Accept new request, create a service 
  def accept_service(self, flag=True):
    try:
      conn, addr = self.socket.accept()
      self.service_id += 1
      name = self.name+":service:%d" % self.service_id
      reader = self.reader.duplicate()
      newadaptor = SocketService(self, reader, name, conn, addr)
      if flag :
        #newadaptor.start()
        newadaptor.run()
        return None
      return newadaptor
    except (Exception) as e:
      print("ERROR in accept_service")
      try:
        from utility import print_error_msg
        print_error_msg(e)
      except:
        pass
    return None
  #
  #  Wait request from a client 
  #      [Overwrite super's method]
  def accept_service_loop(self, lno=1, timeout=1.0):
    print( "Wait for accept: %s(%s:%d)" % (self.name, self.host, self.port))
    self.socket.listen(lno)
    while self.mainloop:
      self.spin_once(timeout)
    
    print( "Terminate all service %s(%s:%d)" % (self.name, self.host, self.port))
    self.close_service()
    self.close()
    print( "..Terminated")
    return 
  #
  #
  def spin_once(self, timeout=1.0):
    res = self.wait_for_read(timeout) 
    if res == 1:
      self.accept_service()
    elif res == -1:
      self.terminate()
    else:
      pass
    return
  #
  #
  def getServer(self):
    return self
  #
  #
  def registerCommand(self, cmd, func):
    try:
      self.reader.registCommand(cmd, func)
    except:
      print("Fail to register", cmd)
    return
  #
  #  Thread operations....
  def run(self):
    #self.mainloop=True
    self.accept_service_loop(timeout=-1)
    return
  #
  # 
  def remove_service(self, adaptor):
     try:
       if len(self.com_ports) > 0:
         self.com_ports.remove(adaptor)
     except:
       pass
  #
  #
  def getComPorts(self, klass):
    res=[]
    try:
      for x in self.com_ports:
        if isinstance(x.reader.command, klass) : res.append(x)
    except:
      pass
    return res
  
###########################
#  Service Adaptor
#
class SocketService(SocketPort):
  #
  # Constructor
  def __init__(self, server, reader, name, sock, addr):
    SocketPort.__init__(self, reader, name, addr[0], addr[1])
    self.module_name=__name__+'.SocketService'
    self.socket = sock
    self.server_adaptor = server
    self.name=''
    #self.server_adaptor.com_ports.append(self)
  #
  # Threading...
  def run(self):
    self.mainloop=True
    self.message_receiver(timeout=1.0)
    return
  #
  #
  def getServer(self):
    return self.server_adaptor
  #
  #
  def terminate(self):
    self.mainloop=False
    super().terminate()
    # self.server_adaptor.com_ports.remove(self)
    gc.mem_free()
    return
  
##########################
#  Foundmental reader class 
#
class CommReader:
  #
  # Constructor
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
  def parse(self, data):
    if self.debug:
      print( data )
    if data : self.appendBuffer( data )
    return self.checkBuffer()
  #
  #  Usually 'owner' is a controller
  def setOwner(self, owner):
    self.owner = owner
  #
  #
  def setBuffer(self, buff):
    if self._buffer : del self._buffer
    self._buffer=buff
    self.bufsize = len(buff)
    self.current=0
  #
  #
  def getServer(self):
    return  self.owner.getServer()
  #
  #
  def getCommand(self):
    return self.command
  #
  #  duplicate...
  def duplicate(self):
    #reader = copy.copy(self)
    reader = self.__class__(self.owner, self.command)
    if self.command:
      #reader.command = copy.copy(self.command)
      reader.command = self.command.duplicate()
      reader.command.reader = reader
    return reader
  #
  # Buffer operations
  def appendBuffer(self, buff):
    self._buffer += buff
    self.bufsize = len(self._buffer)
  #
  #
  def skipBuffer(self, n=4, flag=1):
    self.current += n
    if flag :
      self._buffer = self._buffer[self.current:]
      self.current = 0
      self.bufsize = len(self._buffer)
    return 
  #
  #
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
      #print( "ERR in checkBuffer")
      self._buffer=""
      pass
    return False
  #
  # Send response message
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
  def sendResponse(self, res, flag=True):
    self.response = res
    self.send(flag)
    return
  #
  # Append response message
  def setResponse(self, msg):
    self.response += msg
    return
  #
  # Clear response message
  def clearResponse(self):
    self.response=""
    return
  #
  #  extract data from self.buffer 
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
  def __init__(self, dirname="html"):
    CommReader.__init__(self, None, HttpCommand(dirname))
    self.dirname = dirname

    self.commands={
        '/hello' : self.hello,
                  } 
  #
  #  duplicate...
  def duplicate(self):
    reader = self.__class__(self.dirname)
    reader.commands = self.commands
    return reader
  #
  #
  def setDocumentRoot(self, name):
    self.command.setRootDir(name)
    return
  #
  #
  def doProcess(self, header, data):
    self.clearResponse()
    cmd = header["Http-Command"]
    fname = header["Http-FileName"].split('?')
    if cmd == "GET":
      contents = get_file_contents(fname[0], self.dirname)
      ctype = get_content_type(fname[0])

      if contents is None:
        response = response404()
      else:
        if ctype.startswith('image'):
          response = response200(ctype, contents)
        else:
          response = response200(ctype, contents.decode())
      self.sendResponse(response)

    elif cmd == "POST":
      if fname[0] in self.commands :
        callback_func_ = self.commands[fname[0]]
        if isinstance(callback_func_, Command):
          response = callback_func_.execute(data)
        else:
          response = callback_func_(data)
        if response:
          if response is True:
            self.sendResponse(response200('application/json', json.dumps({"result": "OK"})))
          elif isinstance(response, dict):
            self.sendResponse(response200('application/json', json.dumps(response)))
          else:
            self.sendResponse(response)
        else:
          self.sendResponse(response500())
      else:
          contents = "Hello, No such action defined"
          response = response200("text/plain", contents)
          self.sendResponse(response)

    else:
      response = response400()
      self.sendResponse(response)

    return True
  #
  #
  def registerCommand(self, ctype, obj):
    self.commands[ctype] = obj
  #
  #
  def hello(self, data):
    print("Hello:", data)
    response = response200('application/json', json.dumps({"result": "OK"}))
    return response

############################################
# CommCommand: parse the reveived message
#
class CommCommand:
  #
  #  Costrutor
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
  #
  def duplicate(self):
    command = self.__class__(self.buffer, self.reader)
    return command
  #
  #  for buffer
  def setBuffer(self, buff):
    if self._buffer : del self._buffer
    self._buffer=buff
    self.bufsize = len(buff)
    self.offset=0
  #
  #
  def clearBuffer(self):
    self.setBuffer("")
  #
  #
  def appendBuffer(self, buff):
    self._buffer += buff
    self.bufsize = len(self.buff)
  #
  #
  def skipBuffer(self, n=0):
      data = ""
      if self.bufsize > n :
        data = self._buffer[:n]
        self.setBuffer(self._buffer[n:])
      return data
  #
  #  check message format (cmd encoded_args)
  def checkMessage(self, buff, offset=0, reader=None):
    print("CommCommand.checkMessage")
    return None
  #
  # set/get operations...
  def setReader(self, rdr):
    self.reader=rdr
  #
  #
  def getServer(self):
    if self.reader:
      return self.reader.getServer()
    return None
  #
  #
  def getComPorts(self):
    srvr=self.getServer()
    if srvr:
      return srvr.com_ports
    return None
  #
  #
  def getMyService(self):
    return self.reader.owner
  #
  #
  def getMyServiceName(self):
    try:
      return self.reader.owner.name
    except:
      print( "Error in getMyServiceName()")
      return None
  #
  #
  def getComPortNames(self):
    try:
      comports = self.getComPorts()
      res = map(lambda n:n.name, comports)
      return res
    except:
      print( "Error in getComPortNames()")
      return None
  #
  #
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
  def __init__(self, dirname=".", buff=''):
    CommCommand.__init__(self, buff)
    self.dirname=dirname
    self.module_name=__name__+'.HttpCommand'
  #
  #
  def duplicate(self):
    command = self.__class__(self.dirname, self.buffer)
    command.reader = self.reader
    return command
  #
  #
  def setRootDir(self, dirname):
    self.dirname=dirname
  #
  #
  def checkMessage(self, buff, offset=0, reader=None):
    pos = self.parseHttpdHeader( buff, offset)
    if pos > 0 :
      if reader is None: reader=self.reader
      reader.doProcess(self.header, self.data)
      return pos
    return 0
  #
  #
  def parseHttpdHeader(self, buff, offset=0):
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
        self.data = self._buffer.encode()[:contentLen]
        if len(self.data) < contentLen:
          return 0
        self.data=self.data.decode()
      return pos
    return 0
  #
  #  parse HTTP Header
  def parseHeader(self, header):
    res = {}
    for h in header:
      if h.find(":") > 0 :
        key, val = h.split(':', 1)
        res[key.strip()] = val.strip()
    return res

##################################################
# Functoins
#
def get_file_contents(fname, dirname="."):
  contents = None
  try:
    with open(dirname+fname,'rb') as file:
      contents = file.read()
  except:
    pass
  return contents
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
  elif ext in imgext:
    ctype = "image/"+ext
  else:
    pass
  return ctype
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
def flatten(lst):
  res=[]
  for x in lst:
    if type(x) is list:
      res += flatten(x)
    else:
      res.append(x)
  return res
#
#
def findall(func, lst):
  res = []
  for x in lst:
    if func(x) : res.append(x)
  return res

##################
#  Response
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
#
#
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
#
#
def response404():
  date = get_now_str()
  res  = "HTTP/1.0 404 Not Found\r\n"
  res += "Date: "+date+"\r\n"
  res += "\r\n"
  return res
#
#
def response400():
  date = get_now_str()
  res  = "HTTP/1.0 400 Bad Request\r\n"
  res += "Date: "+date+"\r\n"
  res += "\r\n"
  return res
#
#
def response500():
  date = get_now_str()
  res  = "HTTP/1.0 500 Internal Server Error\r\n"
  res += "Date: "+date+"\r\n"
  res += "\r\n"
  return res
#
#  Command class
class Command:
  #
  #
  def __init__(self):
    self.name="Command"
  #
  #
  def execute(self, data):
    print(data)
    pass

######################################
#  HTTP Server
#
def create_httpd(num=80, top="/flash/html/", command=None, host=""):
  #mount_sd()
  if type(num) == str: num = int(num)
  reader = HttpReader(top)
  return SocketServer(reader, "Web", host, num)
