'''
Copyright 2025 Isao Hara, RT Corporation.

Licensed under the Apache License, Version 2.0 (the “License”);
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an “AS IS” BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.

'''
import M5
import time

#
# Unvisible Button
class Button:
  def __init__(self, name, x, y, w, h):
    self.name = name
    self.rect=[x, y, w, h]
    self.tapped=False
    self.callback=self.print_name
    self.tap_x = -1
    self.tap_y = -1
    self.event_time = time.time()
  #
  # Check tapped
  def is_tapped(self, x, y):
    w=self.rect[2]
    h=self.rect[3]
    return (self.rect[0] < x and self.rect[0]+w > x and self.rect[1] < y and self.rect[1]+h > y)
  #
  #  Execute callback function
  def check(self):
    if time.time() - self.event_time < 2:
      return
    self.event_time = time.time()
    if self.callback:
        if self.is_tapped(self.tap_x, self.tap_y):
            if self.tapped:
              try:
                self.callback()
              except:
                print("Fail to execute callback")
              self.tap_x = -1
              self.tap_y = -1
    else:
        print("Callback not fount")
    self.tapped = False
    return
  
  def execute(self):
    if time.time() - self.event_time < 2:
      return
    self.event_time = time.time()
    if self.callback:
      try:
        self.callback()
      except:
        print("Fail to execute callback")
      self.tap_x = -1
      self.tap_y = -1
    else:
        print("Callback not fount")
    self.tapped = False
    return
  #
  # Check tap button and set flag
  def check_tap(self):
    self.tap_x = M5.Touch.getX()
    self.tap_y = M5.Touch.getY()
    if self.is_tapped(self.tap_x, self.tap_y):
      self.tapped=True
    else:
      self.tapped=False
    return self.tapped
  #
  # Dummy callback
  def print_name(self, val=None):
    print(self.name)
  #
  # Set callback function
  def set_callback(self, obj):
    if isinstance(obj, str):
      self.callback = eval(obj)
    else:
      try:
        self.callback = obj.callback
      except:
        self.callback = None
    return
  #
  # Update 
  def update(self):
    M5.update()
    self.check()
    return