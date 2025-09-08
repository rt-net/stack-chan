"""
file     FaceClass
time     2025-06-28
author   
email   
license  MIT License
"""

from M5 import *
import random
import machine
import time
import math
import gc
import util

INFO_COLOR=0xffff00
MSG_COLOR=0xffffff
DEFAULT_COLOR=0xffffff
DEFAULT_BG_COLOR=0x000000

################
# Stack-chan Face with double buffering
class Face:
    #
    #
    def __init__(self):
        self.buffer=Display.newCanvas(320,188,16,True)
        self.blink=-100
        self.blink_start_flag=0
        self.update_rate=1
        self.next_blink=(200 + random.random()*40)*self.update_rate
        self.top=26
        self.center=[160,120-self.top]
        self.eye_=[self.center[0],self.center[1]-20]
        self.eye_dist=70
        self.mouse_pos=[self.center[0],self.center[1]+28]
        self.mouse_type={'x': [0,0], 'a':[0.8,0.5], 'i':[0.1,0.5],'u':[0.6,-0.5],'e':[0.2,0.8],'o':[0.4,-0.3],'n':[-0.1,0.7]}
        self.face_type=0
        self.mouse_flag=0
        self.talk_intval=0.1
        self.count=0
        self.talk_timer=machine.Timer(0)
        self.blink_timer=machine.Timer(1)
        self.motions_all=['', 'look_r', 'look_l', 'look_u', 'look_d', 'wink_r', 'wink_l', 'anger', 'surprise', 'unhappy', 'smile']
        self.motions=['', 'look_d','smile']
        self.top_buffer=Display.newCanvas(320,26,16,True)
        self.bottom_buffer=Display.newCanvas(320,26,16,True)
        self.top_buffer.setFont(Widgets.FONTS.EFontJA24)
        self.bottom_buffer.setFont(Widgets.FONTS.EFontJA24)
        self.current_face='normal'
        self.prev_face=None
        self.message=''
        self.info=''
        self.moving = False
        self.start_time=time.time_ns()
        self.buffer.setFont(Widgets.FONTS.EFontJA24)
    #
    #
    def set_center(self, x, y):
        self.center=[x,y]
        self.eye_=[self.center[0],self.center[1]-20]
        self.mouse_pos=[self.center[0],self.center[1]+28]
        return
    #
    #
    def rot_pos(self, p, angle, center=None):
        if center is None: center=self.center
        x=p[0] - center[0]
        y=p[1] - center[1]
        s1=math.sin(angle * math.pi/180.0)
        c1=math.cos(angle * math.pi/180.0)
        x2=int(x*c1 - y*s1)
        y2=int(x*s1 + y*c1)
        return x2+center[0], y2+center[1]
    #
    #
    def callback_blink(self, tm):
        if self.blink > 6:
            self.blink_timer.deinit()
            self.stop_blink()
            return
        self.blink += 2
        self.drawFace()
        return
    #
    #
    def start_blink(self):
        self.moving = True
        self.blink=0
        self.blink_start_flag = -100
        self.blink_timer.init(mode=machine.Timer.PERIODIC,
                              period=50,
                              callback=self.callback_blink)
        return
    #
    #
    def stop_blink(self):
        self.blink_start_flag=0
        self.next_blink=80 + random.random()*40
        self.blink=-100
        self.draw(self.current_face)
        self.moving = False
        self.print_message()
        self.print_info()
        return
    #
    #
    def random_type(self):
        try:
            idx=int(random.random() * len(self.motions))
            return self.motions[idx]
        except:
            return ""
    #
    #
    def start_motion(self, direction=1):
        if self.moving: return
        self.moving=True
        self.current_angle = 0
        self.move_reverse = direction
        self.blink_timer.init(mode=machine.Timer.PERIODIC,
                              period=40,
                              callback=self.callback_motion)
        self.draw(self.current_face)
        return
    #
    #
    def callback_motion(self,tm):
        self.current_angle += 4 * self.move_reverse
        self.draw(self.current_face,angle=self.current_angle)
        if self.current_angle > 10:
            self.move_reverse = -1
        elif self.current_angle < -10:
            self.move_reverse = 1
        if self.current_angle == 0:
            self.blink_timer.deinit()
            self.stop_motion()
        return
    #
    #
    def stop_motion(self):
        self.draw(self.current_face)
        self.moving=False
        return
    #
    #
    def drawEye(self, param0: int=0, r: int=8, pos: int=0,
             angle1: int=0, angle2: int=0, xpos: int=0, eye_dist=70):
        xl=self.eye_[0]- eye_dist + xpos
        yl=self.eye_[1]- pos
        xr=self.eye_[0]+ eye_dist + xpos
        yr=self.eye_[1]- pos

        xl, yl = self.rot_pos([xl, yl], angle1)
        xr, yr = self.rot_pos([xr, yr], angle1)
        l=r*2

        if param0 == 1:   #  ^ ^
            for i in range(3):
              self.buffer.drawArc(xl, yl, r-1+i, r+i, 180+angle1, 360+angle1, DEFAULT_COLOR)
              self.buffer.drawArc(xr, yr, r-1+i, r+i, 180+angle1, 360+angle1, DEFAULT_COLOR)

        elif param0 == 2:  # o -
            self.buffer.fillRect(xl-(r+l)//2, yl-r//2, r+l, r, DEFAULT_COLOR)
            self.buffer.fillCircle(xr, yr, r, DEFAULT_COLOR)

        elif param0 == 3:   # - o
            self.buffer.fillRect(xr-(r+l)//2, yr-r//2, r+l, r, DEFAULT_COLOR)
            self.buffer.fillCircle(xl, yl, r, DEFAULT_COLOR)

        elif param0 == 4:  # - -
            self.buffer.fillRect(xl-(r+l)//2, yl-r//2, r+l, r, DEFAULT_COLOR)
            self.buffer.fillRect(xr-(r+l)//2, yr-r//2, r+l, r, DEFAULT_COLOR)

        elif param0 == 5:  # + +
            self.buffer.fillRect(xl-(r+l)//2, yl-r//2, r+l, r, DEFAULT_COLOR)
            self.buffer.fillRect(xl-r//2, yl-(r+l)//2, r, r+l, DEFAULT_COLOR)
            self.buffer.fillRect(xr-(r+l)//2, yr-r//2, r+l, r, DEFAULT_COLOR)
            self.buffer.fillRect(xr-r//2, yr-(r+l)//2, r, r+l, DEFAULT_COLOR)

        elif param0 == 6: # / \ or \ /
            self.fillRectRot(xl-(r+l)//2, yl-r//2, r+l, r, -angle2, DEFAULT_COLOR)
            self.fillRectRot(xr-(r+l)//2, yr-r//2, r+l, r, angle2, DEFAULT_COLOR)

        else:  # o o
            self.buffer.fillCircle(xl, yl, r, DEFAULT_COLOR)
            self.buffer.fillCircle(xr, yr, r, DEFAULT_COLOR)
            if self.is_blinking():
                self.buffer.fillCircle(xl, yl-self.blink, r, DEFAULT_BG_COLOR)
                self.buffer.fillCircle(xr, yr-self.blink, r, DEFAULT_BG_COLOR)
                self.update_blinking(r*2 + 2)
    #
    #
    def check_blink_time(self):
        return (self.blink_start_flag > self.next_blink)
    #
    #
    def is_blinking(self):
        return (self.blink > 0)
    #
    #
    def update_blinking(self, thr=20):
        if self.blink > thr:
            self.stop_blinking()
        self.blink += 10
        return
    #
    #
    def stop_blinking(self):
        self.blink=-100
        self.blink_start_flag=0
        self.next_blink=(200 + random.random()*100)*self.update_rate
        if self.message: self.print_message()
        if self.info: self.print_info()
        return
    #
    #
    def drawMouse(self, oRatio=0, oRatio2=0, angle=0, pos=0,
                 mouse_flag=0, xpos=0, dw=0):
        if mouse_flag == 1 or mouse_flag == 'v':  # v
            r=80
            x=self.mouse_pos[0] + xpos
            y=self.mouse_pos[1] - r -pos
            x, y = self.rot_pos([x, y], angle)
            for i in range(4):
              self.buffer.drawArc(x, y, r+i, r+i+1, 70+angle, 110+angle, DEFAULT_COLOR)

        elif mouse_flag == 2 or mouse_flag == '^': # ^
            r=80
            x=self.mouse_pos[0] +xpos
            y=self.mouse_pos[1] + r -pos
            x, y = self.rot_pos([x, y], angle)
            for i in range(4):
              self.buffer.drawArc(x, y, r+i, r+i+1, 250+angle, 290+angle, DEFAULT_COLOR)

        elif mouse_flag == 3 or mouse_flag == 'o': # ^
            x=self.mouse_pos[0] + xpos
            y=self.mouse_pos[1] -pos
            rx=10
            ry=20
            for i in range(4):
              self.buffer.drawEllipse(x, y, rx+i, ry+i, DEFAULT_COLOR)
       
        else:  # -
            minWidth=50
            maxWidth=90
            minHeight=8
            maxHeight=58
            if oRatio2 == 0: oRatio2=oRatio
            h = int(minHeight + (maxHeight - minHeight) * oRatio)
            w = int(minWidth + (maxWidth - minWidth) * oRatio2) +dw
            x=self.mouse_pos[0] - w // 2 + xpos
            y=self.mouse_pos[1] - h // 2 - pos
            if angle == 0:
              self.buffer.fillRect(x, y, w, h, DEFAULT_COLOR)
            else:
              for i in range(h):
                x1, y1 = self.rot_pos([x, y+i], angle)
                x2, y2 = self.rot_pos([x+w, y+i], angle)
                self.buffer.drawLine(x1, y1, x2, y2, DEFAULT_COLOR)
        return
    #
    #
    def fillRectRot(self, x, y, w, h, angle=0, color=DEFAULT_COLOR):
        center = [x+w//2, y+h//2]
        for i in range(h):
            x1, y1 = self.rot_pos([x, y+i], angle, center)
            x2, y2 = self.rot_pos([x+w, y+i], angle, center)
            self.buffer.drawLine(x1, y1, x2, y2, color)
        return
    #
    #
    def talk(self, seq, speed=0):
        if self.moving: return
        if not speed: speed=self.talk_intval
        self.moving=True
        for x in seq:
            if not x in self.mouse_type: continue
            self.drawFace(x)
            time.sleep(speed)
        self.drawFace('x')
        self.moving=False
        return
    #
    #
    def setFaceType(self, n: int=0):
        self.face_type=0
        return True
    #
    #
    def drawFace(self, idx='x', angle=0, flush=True):
        if flush:
            self.buffer.clear()
        self.drawEye(self.face_type, angle1=angle)
        self.drawMouse(*self.mouse_type[idx], angle=angle)
        if flush:
            self.flush()
        return
    #
    #
    def clear(self):
        self.buffer.clear()
        return True
    #
    #
    def set_face_id(self, val):
        self.prev_face = self.current_face
        self.current_face = val
        return True
    #
    #
    def draw(self, id: str='x', angle: int=0):
        self.buffer.clear()
        if id == 'talk':
            try:
                idx=list(self.mouse_type.keys())[round(random.random() * len(self.mouse_type))]
            except:
                idx='x'
            self.drawFace(idx, flush=False)

        elif id == 'smile':
            self.drawEye(1, angle1=angle)
            self.drawMouse(mouse_flag='v', angle=angle)

        elif id == 'anger':
            self.drawEye(6, angle2=-10)
            self.drawMouse(mouse_flag='^')

        elif id == 'unhappy':
            self.drawEye(6, angle2=10)
            self.drawMouse(mouse_flag='^')

        elif id == 'surprise':
            self.drawEye(5)
            self.drawMouse(mouse_flag='o')

        elif id == 'wink_r':
            self.drawEye(2)
            self.drawMouse(angle=angle+5)

        elif id == 'wink_l':
            self.drawEye(3)
            self.drawMouse(angle=angle-5)

        elif id == 'look_l':
            self.drawEye(xpos=-50, eye_dist=30, angle1=angle)
            self.drawMouse(pos=-10, xpos=-40, dw=20, angle=angle)

        elif id == 'look_r':
            self.drawEye(xpos=50, eye_dist=30, angle1=angle)
            self.drawMouse(pos=-10, xpos=40, dw=20,angle=angle)

        elif id == 'look_u':
            self.drawEye(pos=30, eye_dist=60, angle1=angle)
            self.drawMouse(pos=20,dw=-10, angle=angle)

        elif id == 'look_d':
            self.drawEye(pos=-30, eye_dist=60, angle1=angle)
            self.drawMouse(pos=-20,dw=-10,angle=angle)

        else:
            self.drawFace(angle=angle, flush=False)
            if  (not self.is_blinking()) and self.check_blink_time():
                self.blink = 1

        self.flush()
        return
    #
    #
    def flush(self):
        self.buffer.push(0,self.top)
        #self.top_buffer.push(0,0)
        #self.bottom_buffer.push(0,214)
        return
    #
    #
    def print_message(self, msg=''):
        self.message=msg
        if msg:
            self.top_buffer.fillRect(0,0,320,26,0xffffff)
            self.top_buffer.setCursor(0,2)
            self.top_buffer.setTextColor(0, 0xffffff)
            self.top_buffer.print(msg)
            self.top_buffer.push(0,0)
        else:
            self.top_buffer.clear()
        self.top_buffer.push(0,0)
        return
    #
    #
    def print_info(self, msg=''):
        self.info=msg
        if msg:
            self.bottom_buffer.fillRect(0,0,320,26,0xffff00)
            self.bottom_buffer.setCursor(0,2)
            self.bottom_buffer.setTextColor(0, 0xffff00)
            self.bottom_buffer.print(msg)
        else:
            self.bottom_buffer.clear()
        self.bottom_buffer.push(0,214)
        return
    #
    #
    def update_motion_interval(self):
        if self.current_face == 'normal':
            self.blink_start_flag += 1
        else:
            self.blink_start_flag=0
        return
    #
    #
    def update(self):
        if self.moving: return
        if self.prev_face != self.current_face or self.check_blink_time():
            #if (time.time_ns()-self.start_time)/1000000000 > 86400:
            #    self.start_time=time.time_ns()
            #print("draw", (time.time_ns()-self.start_time)/1000000000,
            #       util.get_now_str2(), Power.getBatteryLevel())
            self.draw(self.current_face)
            self.set_face_id(self.current_face)
        self.update_motion_interval()
        return