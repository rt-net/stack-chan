'''
    Dynamixel motor driver
'''
import machine
from machine import UART
import struct
import math

########## Variables
#
INSTRUCTION = {
  'PING': 0x01,
  'READ': 0x02,
  'WRITE': 0x03,
  'REG_WRITE': 0x04,
  'ACTION': 0x05,
  'FACTORY_RESET': 0x06,
  'REBOOT': 0x08,
  'STATUS': 0x55,
  'SYNC_READ': 0x82,
  'SYNC_WRITE': 0x83,
  'BULK_READ': 0x92,
  'BULK_WRITE': 0x93,
}

OPERATING_MODE = {
  'CURRENT': 0x00,
  'VELOCITY': 0x01,
  'POSITION': 0x03,
  'EXTENDED_POSITION': 0x04,
  'CURRENT_BASED_POSITION': 0x05,
  'PWM': 0x10,
}

ADDRESS = {
  'MODEL_NUMBER': 0,
  'MODEL_INFORMATION': 2,
  'VERSION_OF_FIRMWARE': 6,
  'ID': 7,
  'BAUDRATE': 8,
  'RETURN_DELAY_TIME': 9,
  'DRIVE_MODE': 10,
  'OPERATING_MODE': 11,
  'HOMING_OFFSET': 20,
  'TORQUE_ENABLE': 64,
  'LED': 65,
  'GOAL_CURRENT': 102,
  'GOAL_POSITION': 116,
  'PROFILE_ACCELERATION': 108,
  'PROFILE_VELOCITY': 112,
  'PRESENT_CURRENT': 126,
  'PRESENT_VELOCITY': 128,
  'PRESENT_POSITION': 132,
}

######################
#
class Dynamixel(object):
    #
    #
    def __init__(self, id=1, rx=6, tx=7, baud_rate=1000000, bits=8, parity=None, stop=1, uart_id=1):
        self.uart=UART(uart_id, baud_rate)
        self.uart.init(baud_rate, bits=bits, parity=parity, stop=stop, rx=rx, tx=tx)
        self.id = id
    #
    #
    def checksum(self, data):
        end = len(data)
        crc16 = 0
        for i in range(end):
            n = int(data[i])
            crc16 = (crc16 ^ (n << 8)) & 0xffff
            for _ in range(8):
                if crc16 & 0x8000:
                    crc16 = ((crc16 << 1) ^ 0x8005) & 0xffff
                else:
                    crc16 = (crc16 << 1) & 0xffff
        return crc16
    #
    #
    def make_command(self, inst, addr, params):
        packet = bytearray([0xff,0xff,0xfd,0x00, self.id, 0, 0])
        packet.append(inst & 0xff)
        if addr:
            packet.append(addr & 0xff)
            packet.append((addr >> 8) & 0xff)
        for x in params:
            packet.append(x)
        len_ = len(packet) - 5
        packet[5] = (len_ & 0xff)
        packet[6] = ((len_ >> 8) & 0xff)
        crc16 = self.checksum(bytes(packet))
        packet.append(crc16 & 0xff)
        packet.append((crc16 >> 8) & 0xff)
        return packet
    #
    #
    def send_command(self, inst, addr, params):
        self.uart.write(self.make_command(inst, addr, params))
        res = ''
        while not res:
            res = self.uart.read()
        return res
    #
    #
    def parse(self, data):
        if data[:4] == b'\xff\xff\xfd\00':
            if self.checksum(data[:-2]) == struct.unpack('<H', data[-2:])[0]:
                len_ = struct.unpack('<H', data[5:7])[0]
                #print("OK", len_,  data)
                return len_
        print("Invalid packet", data)
        return  -1
    #
    #
    def readPresentPosition(self):
        res = self.send_command(INSTRUCTION['READ'], ADDRESS['PRESENT_POSITION'], b'\x04\x00')
        len_=self.parse(res)
        if len_ == 8:
            if res[7:9] == b'\x55\00':
                pos=struct.unpack('<i', res[9:13])[0]
                return pos
        return None
    #
    #
    def setOperatingMode(self, mode):
        res = self.send_command(INSTRUCTION['WRITE'], ADDRESS['OPERATING_MODE'], struct.pack('B', mode))
        return self.parse(res) > 0
    #
    #
    def setTorque(self, enable):
        res = self.send_command(INSTRUCTION['WRITE'], ADDRESS['TORQUE_ENABLE'], struct.pack('B', enable))
        return self.parse(res) > 0
	#
    #
    def setGoalPosition(self, pos):
        res = self.send_command(INSTRUCTION['WRITE'], ADDRESS['GOAL_POSITION'], struct.pack('<I', pos))
        return self.parse(res) > 0
    #
    #
    def setGoalCurrent(self, val):
        res = self.send_command(INSTRUCTION['WRITE'], ADDRESS['GOAL_CURRENT'], struct.pack('<H', val))
        return self.parse(res) > 0
    #
    #
    def setProfileAcceleration(self, val):
        res = self.send_command(INSTRUCTION['WRITE'], ADDRESS['PROFILE_ACCELERATION'],struct.pack('<I', val))
        return self.parse(res) > 0
    #
    #
    def setProfileVelocity(self, val):
        res = self.send_command(INSTRUCTION['WRITE'], ADDRESS['PROFILE_VELOCITY'],struct.pack('<I', val))
        return self.parse(res) > 0

##############
#  Position Control
class PConrtol:
    #
    #
    def __init__(self, servo, gain, saturation,
                  name='servo', offset_pos=2048,
                  min_pos=-180, max_pos=180):
        self.servo = servo
        self.gain = gain
        self.saturation = saturation
        self.name = name
        self._offset = offset_pos
        self.goalPosition = 0
        self.presentPosition = 0
        self._lastGoalPosition = 0
        self.init_pos = 0
        self.min_pos = min_pos
        self.max_pos = max_pos
    #
    #
    def init(self):
        result = self.servo.readPresentPosition()
        if result is not None:
            while result - self._offset > 4096:
                self._offset += 4096
            while result + self._offset < -4096:
                self._offset -= 4096
        else:
            print("Fail to initialize")
            return
        self.goalPosition = 0
        self.servo.setOperatingMode(OPERATING_MODE['CURRENT_BASED_POSITION'])
        self.servo.setTorque(True)
        return
    #
    #
    def update(self):
        if self._lastGoalPosition != self.goalPosition:
            self.servo.setGoalPosition(self.goalPosition+self._offset)
            self._lastGoalPosition = self.goalPosition
        result = self.servo.readPresentPosition()
        if result is None:
            return
        self.presentPosition = result - self._offset
        current = min(abs(self.goalPosition - self.presentPosition) * self.gain, self.saturation )
        self.servo.setGoalCurrent(int(current))
    #
    #
    def getPresentPosition(self):
        return (self.presentPosition * 360) // 4096
    #
    #
    def setTorque(self, flag):
        self.servo.setTorque(flag)
        return
    #
    #
    def setGoalPosition(self, angle):
        self.goalPosition = math.floor((min(max(angle, self.min_pos), self.max_pos)) * 4096 / 360)

########################
#  Pan-Tilt Control
class DynamixelDriver:
    #
    #
    def __init__(self):
        self._pan = Dynamixel(1)
        self._tilt = Dynamixel(2)
        pan_offset = self._pan.readPresentPosition()
        tilt_offset = self._tilt.readPresentPosition()
        self._controls = [
                            PConrtol(self._pan, 0.15, 80, 'pan', pan_offset, -180, 180),
                            PConrtol(self._tilt, 4, 800, 'tilt', tilt_offset, -20, 7)
                          ]
        self._torque = True
        self._initialzed = False
        self.control_timer=machine.Timer(2)
    #
    #
    def setTorque(self, flag):
        self._torque = flag
        [x.setTorque(self._torque) for x in self._controls]
        return
    #
    #
    def onAttached(self):
        self.control_timer.init(mode=machine.Timer.PERIODIC,period=125,callback=self.control)
        return
    #
    #
    def onDetached(self):
        self.control_timer.deinit()
        return
    #
    #
    def control(self, tm=0):
        if not self._initialzed :
            self._initialzed = True
            for ctrl in self._controls:
                ctrl.init()
            self._pan.setProfileAcceleration(20)
            self._pan.setProfileVelocity(100)
        for ctrl in self._controls:
            ctrl.update()
        return
    #
    #
    def applyRotation(self, pose):
        panAngle = pose[0] * 180/math.pi
        tiltAngle = pose[1] * 180/math.pi
        self._controls[0].setGoalPosition(panAngle)
        self._controls[1].setGoalPosition(tiltAngle)
        return
    #
    #
    def getRotation(self):
        p1, p2 =  [x.getPresentPosition()  for x in self._controls]
        return { 'r': 0.0, 'y': p1 * math.pi / 180, 'p': p2 * math.pi / 180}
    #
    #
    def move(self, h_deg, v_deg, force_update=False):
        self._controls[0].setGoalPosition(h_deg)
        self._controls[1].setGoalPosition(v_deg)
        if force_update:
            for ctrl in self._controls:
                ctrl.update()
        return
    #
    #
    def get_position(self):
        return [x.getPresentPosition()  for x in self._controls]
    #
    #
    def update(self):
        self.control()
        return
