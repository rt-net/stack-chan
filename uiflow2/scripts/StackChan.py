'''
  Stack-chan Main Class
'''
import M5
import json
import time
import binascii
import camera
import gc

import Face
import util
import WebServer


#
# Stack-chan Main
class StackChan:
  #
  #
  def __init__(self):
    util.mount_sd()
    gc.enable()
    try:
      self.config=json.loads(util.get_file_contents("/sd/stackchan.json"))
    except:
      self.config={}
    # WLAN
    self.wlan = util.connect_wlan()
    #
    # camera
    camera.init(pixformat=camera.RGB565, framesize=camera.QVGA)
    #
    # face, motors, TTS client, ASR client
    self.face=Face.Face()
    self.web_server=None
    self.motor=None
    self.set_motor()
    self.tts=None
    self.set_tts()
    self.asr=None
    self.set_asr()
  #
  # Create web server
  def init_web(self, n=80, start=False):
    if  'web_server' in self.config:
      try:
        port = int(self.config['web_server'])
      except:
        port = n
    else:
      port = n
  
    self.web_server=WebServer.WebServer(port)
    #
    # Register REST API
    self.web_server.registerCommand("/move", self.set_goal_position)
    self.web_server.registerCommand("/face", self.face.set_face_id)
    self.web_server.registerCommand("/get_camera_image", self.capture_image)
    self.web_server.registerCommand("/set_message", self.set_message)

    if self.tts:
        self.web_server.registerCommand("/tts", self.tts.set_request)
    if self.asr:
        self.web_server.registerCommand("/asr", self.asr.set_request)

    if start:
      self.start_web_server()
    return
  #
  # Start web service thread.
  def start_web_server(self):
    if self.web_server is None:
      self.init_web(start=False)

    if self.isconnected_wlan():
        self.face.print_info("IP:" + self.wlan.ifconfig()[0])
        #self.web_server.start()
    else:
      if self.connect_wlan(10):
        self.face.print_info("IP:" + self.wlan.ifconfig()[0])
        #self.web_server.start()
    return
  #
  # Setup motor driver
  def set_motor(self):
    try:
      if self.config['motor'] == 'Dynamixel':
        import DynamixelDriver
        self.motor = DynamixelDriver.DynamixelDriver()
      elif self.config['motor'] == 'SG90':
        import SG90Driver
        try:
          self.motor = SG90Driver.SG90Driver(
                          h_port=int(self.config['sg90_pan']),
                          v_port=int(self.config['sg90_tilt']))
        except:
          self.motor = SG90Driver.SG90Driver()
      else:
        self.motor = None
    except:
      self.motor = None
    return
  #
  # Setup Text-to-speach(TTS) client
  def set_tts(self, name='google'):
    tts_name = name
    if 'tts' in self.config:
      tts_name = self.config['tts']

    if tts_name == 'voicevox':
      import Voicevox
      self.tts = Voicevox.Voicevox(self.config['tts_ip'])
    elif tts_name == 'melo_tts':
      import MeloTts
      self.tts = MeloTts.MeloTts()
    else:
      import Gtts
      self.tts = Gtts.Gtts()
    return
  #
  # Setup Automatic-speech-recognition(ASR) client
  def set_asr(self, name='google'):
    asr_name = name
    if 'asr' in self.config:
      asr_name = self.config['asr']

    if asr_name == 'vosk':
      import VoskAsr
      self.asr = VoskAsr.VoskAsr(self.config['asr_ip'])
    elif asr_name == 'llm_asr':
      print("LLM-ASR not supported")
      self.asr = None
    elif asr_name == 'llm_whisper':
      print("LLM-Wisper not supported")
      self.asr = None
    else:
      import Gasr
      self.asr = Gasr.Gasr()
    return    
  #
  # Connect Wireless LAN
  def connect_wlan(self, trial=10):
    for _ in range(trial):
      if self.wlan and self.wlan.isconnected():
        self.face.print_info("IP:" + self.wlan.ifconfig()[0])
        return True
      else:
        self.face.print_info("Connecting...")
        self.wlan = util.connect_wlan(self.wlan)
        time.sleep(1)
    self.face.print_info("WLAN not connected")
    return False
  #
  # Check connection of wireless LAN
  def isconnected_wlan(self):
    if self.wlan:
      return self.wlan.isconnected()
    return False
  #
  # Servo on/off (for Dynamixel motor)
  def set_torque(self, val):
    try:
      if isinstance(val, str): val = eval(val)
      self.motor.setTorque(val)
    except:
      pass
    return True
  #
  # Teminate web service
  def stop_web(self):
    self.web_server.stop()
    return
  #
  # Tarminate web service and motor control
  def stop(self):
    self.web_server.stop()
    self.set_torque(False)
    return
  #
  # Set goal position: pose=[Pan(degree), Tilt(degree)]
  def set_goal_position(self, pose):
    if self.motor:
      if isinstance(pose, str):
        pose = eval(pose)
      self.motor.move(pose[0], pose[1])
      return True
    return False
  #
  # Set goal posirion
  def move(self, p_deg, t_deg):
    self.motor.move(p_deg, t_deg, True)
    return
  #
  # Show ASR result
  def show_asr_result(self, result):
    if result and result['error'] == '':
      self.face.info=result['result']
      self.face.print_info(result['result'])
    return True
  #
  # Capture an image
  def capture_image(self, arg):
    frame = camera.snapshot()
    raw_bytes = frame.bytearray()
    encoded = binascii.b2a_base64(raw_bytes, newline=False).decode()
    response = {
        'width': frame.width(),
        'height': frame.height(),
        'data': encoded
    }
    return response
  #
  # Set message
  def set_message(self, data):
    try:
      msg = json.loads(data)
      if msg['type'] == 'info':
        self.face.info = msg['message']
      elif msg['type'] == 'message':
        self.face.message = msg['message']
      else:
        self.face.message=''
        self.face.info=''
    except:
      pass
    return True
  #
  #
  def show_battery_level(self):
    self.face.print_message('Battery: %d' % M5.Power.getBatteryLevel())
    return
  #
  # Spin once
  def update(self):
    if self.web_server:
      self.web_server.update()
    self.face.update()
    if self.motor:
      self.motor.update()
    if self.tts:
      self.tts.check_request()
    if self.asr:
      res=self.asr.check_request()
      self.show_asr_result(res)
    return
