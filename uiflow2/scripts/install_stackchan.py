import os
import requests2


def basename(fname):
    return fname.split("/")[-1]

def save_file(data, fname, to_dir):
    to_file = to_dir+"/"+ basename(fname)
    ft = open(to_file, 'w')
    ft.write(data)
    ft.close()

def fetch_file(fname, to_dir):
    url_base="https://raw.githubusercontent.com/haraisao/stackchan-uiflow2/refs/heads/main/"
    #url_base="https://raw.githubusercontent.com/rt-net/stack-chan/refs/heads/uiflow2/uiflow2"
    url_ = url_base+fname
    res = requests2.get(url_)
    if res.status_code == 200:
        save_file(res.text, fname, to_dir)

def install_files(src_files,to_dir='/flash/libs'):
    for fname in src_files:
        print("Get file: "+fname+" to "+ to_dir)
        fetch_file(fname, to_dir)

def append_prefix(pref, flist):
    return [pref+x for x in flist]

def setup():
    lib_list=["Button.py", "Chatgpt.py", "comm.py", "DynamixelDriver.py", "Face.py", 
              "Gasr.py", "Gemini.py", "Gtts.py", "SG90Driver.py", "StackChan.py",
              "util.py", "WebServer.py", "Voicevox.py", "VoskAsr.py"]
    app_list=["stackchan_app.py"]
    install_files(append_prefix('libs/', lib_list), '/flash/libs')
    install_files(append_prefix('apps/', app_list), '/flash/apps')

if __name__=='__main__':
  try:
    setup()
  except (Exception, KeyboardInterrupt) as e:
    try:
      from utility import print_error_msg
      print_error_msg(e)
    except ImportError:
      print("please update to latest firmware")