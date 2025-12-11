'''
    Utilities
'''
import os
import sys
import json

from machine import Pin, SDCard, RTC
from hardware import sdcard
import network
import ntptime
import socket
import esp32

#
#
def reload(mod):
    mod_name = mod.__name__
    del sys.modules[mod_name]
    return __import__(mod_name)
#
#
def del_mod(mod):
    try:
        del sys.modules[mod.__name__]
    except:
        print("No such module". mod.__name__)
    return
#
#
def load_conf(fname):
    with open(fname, "r", encoding='utf-8') as f:
        conts = f.read()
    keys=conts.split("\n")
    res={}
    for x in keys:
        try:
            k,v = x.split("=")
            res[k]=v
        except:
            pass
    return res

def save_conf(fname, conf):
    with open(fname, "w", encoding='utf-8') as file:
        for k in conf:
            file.write(f"{k}={conf[k]}\n")
    return
#
#
def get_file_contents(fname):
    with open(fname, "r", encoding="utf-8") as f:
        conts = f.read()
    return conts

def load_json(fname):
    data_ = get_file_contents(fname)
    data = []
    for line in data_.split("\n"):
        pos = line.find("#")
        if pos >= 0:
            data.append(line[:pos])
        else:
            data.append(line)
    return json.loads("\n".join(data))

def save_json(fname, conf):
    with open(fname, "w", encoding='utf-8') as file:
        file.write(json.dumps(conf))
    return
#
#
def mount_sd():
    if "sd" in os.listdir("/"):
        return
    sdcard.SDCard(slot=3, width=1, miso=35, mosi=37, sck=36, cs=4)
    return
#
#
def get_config(val, key, default_val=None):
    if type(key) is list:
        keys_ = key
    else:
        keys_ = key.split("/")
    val_ = val
    for k in keys_:
        val_=val_.get(k)
        if val_ is None: return default_val
    return val_

def set_config(conf, key, val):
    if type(key) is list:
        keys_ = key
    else:
        keys_ = key.split("/")
    k_ = keys_[-1]
    conf_=conf
    for k in keys_[:-1]:
        if conf_.get(k) is None:
            conf_[k]={}
        conf_=conf_[k]
    conf_[k_]=val
    return

#
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
#
def setup_wlan(apoint="Home", passwd="", n=3):
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
    wlan.config(reconnects=n)
    print("Connect:", apoint_, passwd_)
    try:
        wlan.connect(apoint_, passwd_)
    except:
        pass
    return wlan
#
#
def connect_wlan(wlan=None,apoints=["Firmware", "Home", "Work", "Mobile"], retry=3):
    conf = get_wlan_conf()
    if wlan is None:
        wlan=network.WLAN(network.STA_IF)
    if wlan.isconnected():
        wlan.disconnect()
    wlan.config(reconnects=retry)
    aps_ = scan_wlan(wlan)

    for name in apoints:
        if get_config(conf, [name,'essid'])  in aps_:
            try:
                wlan.connect(conf[name]['essid'], conf[name]['passwd'])
                if wlan.isconnected():
                    print(wlan.ifconfig())
                    return wlan
            except:
                pass
    print("Fail to connect wlan")
    return None
#
#
def scan_wlan(wlan=None):
    if wlan is None:
        wlan=network.WLAN(network.STA_IF)
        wlan.config(reconnects=3)
    aps_=wlan.scan()
    return [x[0].decode() for x in aps_]

def wifi_connect(ssid, passwd):
    wlan=network.WLAN(network.STA_IF)
    aps_ = scan_wlan(wlan)
    if ssid in aps_:
        wlan.connect(ssid, passwd)
        if wlan.isconnected():
            print(wlan.ifconfig())
        else:
            print("Fail to connect Wifi")
    else:
        print("Can't find access_point", ssid)
    return wlan

######
#
DAY_A = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
MON_A = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
g_rtc = RTC()

TZONE=9
#
#
def setDatetime(year, month, date, hour, minite, second):
  g_rtc.init((year, month, date, hour, minite, second, 0, 0))
  return
#
#
def set_ntptime():
  tm=ntptime.gmtime()
  g_rtc.init(tm)
  return
#
#
def get_now_str():
    lt=g_rtc.datetime()
    if lt[0] < 2000:
        try:
            ntptime.settime()
        except:
            pass
    return "%s, %02d %s %d %02d:%02d:%02d GMT" % (DAY_A[lt[3]], lt[2], MON_A[lt[1]-1], lt[0], lt[4], lt[5], lt[6])
#
#
def get_now_str2():
    lt=g_rtc.datetime()
    if lt[0] < 2000:
        try:
            ntptime.settime()
        except:
            pass
    return "%s, %02d %s %d %02d:%02d:%02d.%d GMT" % (DAY_A[lt[3]], lt[2], MON_A[lt[1]-1], lt[0], lt[4], lt[5], lt[6], lt[7])

def set_env(pth='/sd/scripts', init=True):
    mount_sd()
    if not pth in sys.path:
        sys.path.append(pth)
    if init:
        init_M5()

def init_M5(rot=3):
    import M5
    from M5 import Widgets
    M5.begin()
    Widgets.setRotation(rot)
    Widgets.fillScreen(0x000000)

def copy_file(frm, to):
    ff = open(frm)
    ft = open(to, 'w')
    ft.write(ff.read())
    ff.close()
    ft.close()

def remove_all_file(dir):
    os.chdir(dir)
    for fname in os.listdir():
        os.remove(fname)

def reset_m5():
    nvs = esp32.NVS("uiflow")
    nvs.set_u8("boot_option", 1)

def check_connection(host, port):
    try:
        sock_ = socket.socket()
        sock_.connect(socket.getaddrinfo(host, port)[0][-1])
        sock_.close()
        return True
    except:
        return False
    
def make_dirs(path):
    paths = path.split("/")
    p="/"
    for f in paths:
        if f:
            print(p)
            if not f in os.listdir(p):
                os.mkdir(p+f)
            p = p+f+"/"
    return True
    