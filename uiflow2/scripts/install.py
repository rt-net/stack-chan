import os
from hardware import sdcard

def mount_sd():
    if "sd" in os.listdir("/"):
        return
    sdcard.SDCard(slot=3, width=1, miso=35, mosi=37, sck=36, cs=4)
    return

def basename(fname):
    return fname.split("/")[-1]

def copy_file(fname, to_dir):
    ff = open(fname)
    to_file = to_dir+"/"+ basename(fname)
    ft = open(to_file, 'w')
    ft.write(ff.read())
    ff.close()
    ft.close()

def install_files(src_dir,to_dir='/flash/libs'):
    files = os.listdir(src_dir)
    for fname in files:
        print("Copy file: "+fname+" to "+ to_dir)
        copy_file(src_dir+"/"+fname, to_dir)

def setup():
    install_files('libs', '/flash/libs')
    #copy_file('config/stackchan.json', '/sd')
    #copy_file('config/wlan.json', '/sd')
    #copy_file('config/apikey.txt', '/sd')
    install_files('apps', '/flash/apps')