import os, sys, io
import M5
from M5 import *
from StackChan import StackChan
from Button import Button
import time


stackchan_0 = None
button_0 = None
button_1 = None

def setup():
  global stackchan_0, button_0, button_1

  M5.begin()
  Widgets.setRotation(1)
  Widgets.fillScreen(0x000000)

  stackchan_0 = StackChan()
  stackchan_0.init_web(80)
  button_0 = Button('Btn1', 0, 220, 100, 20)
  button_0.set_callback('stackchan_0.start_web_server')
  button_1 = Button('Btn2', 220, 220, 100, 20)
  button_1.set_callback('stackchan_0.show_battery_level')


def loop():
  global stackchan_0, button_0, button_1

  M5.update()
  if 0 < (M5.Touch.getCount()):
    button_0.check_tap()
    button_1.check_tap()
  else:
    button_0.check()
    button_1.check()
    stackchan_0.update()
    time.sleep_ms(150)


if __name__ == '__main__':
  try:
    setup()
    while True:
      loop()
  except (Exception, KeyboardInterrupt) as e:
    try:
      from utility import print_error_msg
      print_error_msg(e)
    except ImportError:
      print("please update to latest firmware")
