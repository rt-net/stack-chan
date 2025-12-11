'''
   SG90 compatible motor dirver
'''
from M5 import *
import machine
import time
import random

######
#
def sign(x):
    return (x > 0) - (x < 0)

##########
#
class SG90Driver:
  #
  #
  def __init__(self, offset=56, h_port=2, v_port=9):
    self.min = 500 * 65535 // 20000
    self.max = 2500 * 65535 // 20000
    self.zero = (1500+offset) * 65535 // 20000
    self.ddeg = (self.max -self.min) / 180.0
    self.delay = 0.01
    self._last_h_deg = 0
    self._last_v_deg = 0
    self._target_h_deg = 0
    self._target_v_deg = -5
    self.h_port = h_port
    self.v_port = v_port
    self.moving=False
    self.current_pos=[0,0]
    self.start_time=time.time()
    self.rand_motion = False
    self.rand_motion_time = None
    self.max_sp_v = 50
    self.max_sp_h = 50
    self.motor_state=False
    self.motor(True)
  #
  #
  def create_pwm(self, pin):
    return machine.PWM(pin, freq=50, duty_u16=self.zero)
  #
  #
  def move_direct(self, h_deg, v_deg):
    self.h_motor.duty_u16(self.zero + int(self.ddeg * h_deg))
    self.v_motor.duty_u16(self.zero + int(self.ddeg * v_deg))
    self.current_pos=[h_deg, v_deg]
    return
  #
  #
  def move(self, h_deg, v_deg, scale=1.0, force=False):
    if not force and self.moving:
      return

    h_deg = max(min(h_deg, 90), -90)
    v_deg = max(min(v_deg, -5), -30)

    self._target_h_deg = h_deg
    self._target_v_deg = v_deg

    sp_v = self.delay * self.max_sp_v * scale
    sp_h = self.delay * self.max_sp_h * scale

    n = max(abs(h_deg - self.current_pos[0]) /sp_h, 
              abs(v_deg - self.current_pos[1]) /sp_v)
    if n == 0:
      return
    
    h_dg = (h_deg - self.current_pos[0]) / n
    v_dg = (v_deg - self.current_pos[1]) / n

    #print("move:", n, h_dg, v_dg,abs(h_deg - self.current_pos[0]) /sp_h, abs(v_deg - self.current_pos[1]) /sp_v)
    self.moving=True
    for x in range(0, n):
      h_target_ = self.current_pos[0] + h_dg
      self.h_motor.duty_u16(self.zero + int(self.ddeg * h_target_))
      v_target_ = self.current_pos[1] + v_dg
      self.v_motor.duty_u16(self.zero + int(self.ddeg * v_target_))
      time.sleep(self.delay)
      self.current_pos = [h_target_, v_target_]
      #print("move:", self.current_pos, h_dg, v_dg)
    self._last_h_deg = h_deg
    self._last_v_deg = v_deg
    self.moving=False
    self.start_time=time.time()
    return
  #
  #
  def motor(self, flag=True):
    if flag:
        if self.motor_state: return
        self.h_motor=self.create_pwm(self.h_port) # PortA-> 2, PortC -> 17
        self.v_motor=self.create_pwm(self.v_port)  # PortB -> 9
        self.motor_state=True
        self.move(self._target_h_deg, self._target_v_deg)
    else:
        self.motor_state=False
        self.h_motor.deinit()
        self.v_motor.deinit()
    return
  
  def random_motion(self):
    self._target_h_deg = int(random.random() * 20) - 10
    self._target_v_deg = int(random.random() * (-30) )
    #print("Move:", self._target_h_deg, self._target_v_deg)

  def toggle_rand_motion(self):
    self.rand_motion = not self.rand_motion
    print("Random Motion", self.rand_motion)
    if self.rand_motion:
      self.rand_motion_time = time.time()
    else:
       self.rand_motion_time = None

  #
  #
  def update(self, tm=0):
      if self._last_h_deg != self._target_h_deg or self._last_v_deg != self._target_v_deg:
          #print("===Move", self._target_h_deg, self._target_v_deg)
          if self.motor_state:
              self.move(self._target_h_deg, self._target_v_deg)
          else:
              print("wake up", self._target_h_deg, self._target_v_deg)
              self.motor(True)
              self.move(self._target_h_deg, self._target_v_deg, force=True)
      else:
          spend_time = time.time() - self.start_time
          if self.motor_state and self.rand_motion_time and  time.time() - self.rand_motion_time > 900:
             self.toggle_rand_motion()
          if self.rand_motion and spend_time > random.random() * 30 + 10:
              self.motor(True)
              self.random_motion()
              return True
          elif self.motor_state and spend_time > 120:
              print("sleep...")
              self.motor(False)
              self.moving=False
      return