import os, sys, io
import M5
from M5 import *
import m5ui
import lvgl as lv

import time
import esp32
import json
import network
import requests2

#
page0 = None
dropdown0 = None
label0 = None
button0 = None
textarea0 = None
label1 = None
dropdown1 = None
button1 = None
label2 = None
label3 = None

#
repositories={
    "1.RT-NET": "https://raw.githubusercontent.com/rt-net/stack-chan/refs/heads/uiflow2/uiflow2",
    "2.Orig": "https://raw.githubusercontent.com/haraisao/stackchan-uiflow2/refs/heads/main/"
}

#
def basename(fname):
  return fname.split("/")[-1]
#
def save_file(data, fname, to_dir, bin_flag=False):
  make_dirs(to_dir)
  to_file = to_dir+"/"+ basename(fname)
  if bin_flag :
    ft = open(to_file, 'wb')
  else:
    ft = open(to_file, 'w', encoding='utf-8')
  ft.write(data)
  ft.close()
#
def make_dirs(path):
    paths = path.split("/")
    p="/"
    for f in paths:
        if f:
            if not f in os.listdir(p):
                os.mkdir(p+f)
            p = p+f+"/"
    return True

def is_image_file(fname):
  ext = basename(fname).split('.')[-1]
  if ext in ['ico', 'png', 'jpg']:
    return True
  return False
#
def fetch_file(fname, to_dir, repo="2.Orig"):
  global repositories
  url_base=repositories.get(repo)
  if url_base:
    url_ = url_base+fname
    res = requests2.get(url_)
    if res.status_code == 200:
      if is_image_file(fname):
        save_file(res.content, fname, to_dir, True)
      else:
        save_file(res.text, fname, to_dir)
    else:
       print("request error")
#
def install_files(src_files,to_dir='/flash/libs', repo="2.Orig"):
  global textarea0
  for fname in src_files:
      try:
        textarea0.add_text(f"Get file: {fname} to {to_dir}\n")
      except:
         pass
      print(f"Get file: {fname} to {to_dir}")
      fetch_file(fname, to_dir, repo)
#
def append_prefix(pref, flist):
    return [pref+x for x in flist]
#
def install_all_files( repo="2.Orig" ):
  lib_list=["Button.py", "Chatgpt.py", "comm.py", "DynamixelDriver.py", "Face.py", 
            "Gasr.py", "Gemini.py", "Gtts.py", "SG90Driver.py", "StackChan.py",
            "util.py", "WebServer.py", "Voicevox.py", "VoskAsr.py"]
  app_list=["stackchan_app.py"]
  config_list=["stackchan.json", "wlan.json", "apikey.txt"]
  html_list=["index.html", "asr_tts.html", "favion.ico", "edit_file.html", "params.html"]
  js_list=["joy.min.js"]
  image_list=["face.png"]

  install_files(append_prefix('libs/', lib_list), '/flash/libs', repo)
  install_files(append_prefix('apps/', app_list), '/flash/apps', repo)
  install_files(append_prefix('config/', config_list), '/flash', repo)
  install_files(append_prefix('html/', html_list), '/flash/html', repo)
  install_files(append_prefix('html/js/', js_list), '/flash/html/js', repo)
  install_files(append_prefix('html/images/',image_list), '/flash/html/images', repo)

def test_dl( repo="2.Orig"):
  image_list=["face.png"]
  html_list=[ "favion.ico"]
  install_files(append_prefix('html/', html_list), '/flash/html', repo)
  install_files(append_prefix('html/images/',image_list), '/flash/html/images', repo)

#
def get_file_contents(fname):
  with open(fname, "r") as f:
      conts = f.read()
  return conts
#
def get_config(val, key):
  if type(key) is list:
    keys_ = key
  else:
    keys_ = key.split("/")
  val_ = val
  for k in keys_:
    val_=val_.get(k)
    if val_ is None: return None
  return val_
#
def get_wlan_conf(file="/flash/wlan.json"):
  nvs = esp32.NVS("uiflow")
  res = {"Firmware": {"essid": nvs.get_str("ssid0"), "passwd": nvs.get_str("pswd0")}}
  try:
      conf=json.loads(get_file_contents(file))
      res |= conf
  except:
      pass
  return res
#
def setup_wlan(apoint="Firmware", passwd="", n=3):
  apoint_ = apoint
  passwd_ = passwd
  try:
      wlan_conf=get_wlan_conf()
      if apoint in wlan_conf:
          apoint_ = wlan_conf[apoint]["essid"]
          passwd_ = wlan_conf[apoint]["passwd"]
  except:
      pass
      
  wlan=network.WLAN(network.STA_IF)
  if wlan.isconnected():
    wlan.disconnect()
    print("disconnect wlan")
  wlan.config(reconnects=n)
  print("Connect:", apoint_, passwd_)
  try:
      wlan.connect(apoint_, passwd_)
  except:
      print("Fail to connect")
  return wlan
#
def button0_pressed_event(event_struct):
    global page0, button0, label2, dropdown0
    idx = dropdown0.get_selected()
    wlan=setup_wlan(dropdown0.get_options()[idx], n=10)
    for _ in range(3):
      if wlan.isconnected():
        ipaddr = wlan.ifconfig()
        break
      else:
        try:
          wlan.connect()
        except:
          pass
        ipaddr = ["no connection"]
      time.sleep(1)
    label2.set_text(str("IP: "+ ipaddr[0]))
#
def button0_event_handler(event_struct):
    global page0, button0, label2
    event = event_struct.code
    if event == lv.EVENT.PRESSED and True:
        label2.set_text(str("IP: connecting..."))
    if event == lv.EVENT.RELEASED and True:
        button0_pressed_event(event_struct)
    return
#
def button1_pressed_event(event_struct):
    global page0, button1, dropdown1, textarea0
    idx=dropdown1.get_selected()
    repo = dropdown1.get_options()[idx]
    textarea0.add_text("Reop:"+repo+"\n")
    install_all_files(repo)
    textarea0.add_text("\n ...finished")
#  
def button1_event_handler(event_struct):
    global page0, button1,textarea0
    event = event_struct.code
    if event == lv.EVENT.PRESSED and True:
        textarea0.set_text("Installing...")

    if event == lv.EVENT.RELEASED and True:
        button1_pressed_event(event_struct)
    return
#
def setup():
  global page0, dropdown0, label0, button0, textarea0, label1, dropdown1, button1, label2, label3, repositories

  M5.begin()
  Widgets.setRotation(1)
  m5ui.init()
  page0 = m5ui.M5Page(bg_c=0xffffff)
  textarea0 = m5ui.M5TextArea(
        text="", placeholder="Placeholder...",x=14, y=145, w=294, h=83,
        font=lv.font_montserrat_14, bg_c=0xffffff, border_c=0xe0e0e0, text_c=0x212121, parent=page0)
  dropdown0 = m5ui.M5Dropdown(
      x=90, y=18, w=100, h=lv.SIZE_CONTENT, 
      options=list(get_wlan_conf().keys()), 
      direction=lv.DIR.BOTTOM, show_selected=True, font=lv.font_montserrat_14, parent=page0)
  label0 = m5ui.M5Label("Wifi AP:", x=15, y=22, text_c=0x000000, bg_c=0xffffff, bg_opa=0, font=lv.font_montserrat_14, parent=page0)
  button0 = m5ui.M5Button(text="Connect", x=213, y=17, bg_c=0x2196f3, text_c=0xffffff, font=lv.font_montserrat_14, parent=page0)
  label1 = m5ui.M5Label("Repository:", x=14, y=108, text_c=0x000000, bg_c=0xffffff, bg_opa=0, font=lv.font_montserrat_14, parent=page0)
  dropdown1 = m5ui.M5Dropdown(
      x=111, y=103, w=100, h=lv.SIZE_CONTENT, 
      options=list(repositories.keys()), 
      direction=lv.DIR.TOP, show_selected=True, font=lv.font_montserrat_14, parent=page0)
  button1 = m5ui.M5Button(text="Install", x=225, y=103, bg_c=0x2196f3, text_c=0xffffff, font=lv.font_montserrat_14, parent=page0)
  label2 = m5ui.M5Label("IP:", x=43, y=65, text_c=0x000000, bg_c=0xffffff, bg_opa=0, font=lv.font_montserrat_14, parent=page0)
  label3 = m5ui.M5Label("...", x=76, y=65, text_c=0x000000, bg_c=0xffffff, bg_opa=0, font=lv.font_montserrat_14, parent=page0)

  button0.add_event_cb(button0_event_handler, lv.EVENT.ALL, None)
  button1.add_event_cb(button1_event_handler, lv.EVENT.ALL, None)
  page0.screen_load()


def loop():
  global page0, dropdown0, label0, button0, textarea0, label1, dropdown1, button1, label2, label3
  M5.update()


if __name__ == '__main__':
  try:
    setup()
    while True:
      loop()
  except (Exception, KeyboardInterrupt) as e:
    try:
      m5ui.deinit()
      from utility import print_error_msg
      print_error_msg(e)
    except ImportError:
      print("please update to latest firmware")
