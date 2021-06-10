import os
import sys
import telnetlib
import json
import requests
import paho.mqtt.client as mqtt
import eiscp

from samsungtvws import SamsungTVWS

from h import TVHOST, TVPORT, VSXHOST, BDHOST, BDPORT, DHOST


PLAY  = b"/A181AF39/RU\n\r"
PAUSE = b"/A181AF3A/RU\n\r"
NEXT  = b"/A181AF3D/RU\n\r"
PREV  = b"/A181AF3E/RU\n\r"

TV  = "tv"
BD  = "bd"
SAT = "sat"
CD  = "cd"
FM  = "fm"
AM  = "am"
NET = "net"
PC  = "game"
USB = "usb"
BT  = "bluetooth"

cube_on = False
second_slide = False
pause_on = False
last_volume = 80
sys.path.append('../')
token_file = os.path.dirname(os.path.realpath(__file__)) + '/tv-token'
tvr = SamsungTVWS(host=TVHOST, port=TVPORT, token_file=token_file)
vsxr = eiscp.eISCP(VSXHOST)
dr = 'http://' + DHOST + ':8080/control/rcu'

def bd_send(command):
    bdr = telnetlib.Telnet(BDHOST, BDPORT)
    bdr.write(command)
    bdr.close()

def bd_channel_up():
    bd_send(NEXT)

def bd_channel_down():
    bd_send(PREV)

def bd_pause():
    global pause_on
    if pause_on:
        bd_send(PLAY)
        pause_on = False
    else:
        bd_send(PAUSE)
        pause_on = True

def get_volume():
    return int(vsxr.command("volume query")[1])

def set_volume(vol):
    if vol < 0:
        vol = 0
    if vol > 164:
        vol = 164
    return vsxr.command("volume " + str(vol))

def volume_up():
    set_volume(get_volume() + 1)

def volume_down():
    set_volume(get_volume() - 1)

def decode(tuple):
    if CD in tuple[1]:
        return CD
    if BD in tuple[1]:
        return BD
    if PC in tuple[1]:
        return PC
    if NET in tuple[1]:
        return NET
    if SAT in tuple[1]:
        return SAT
    if USB in tuple[1]:
        return USB
    return tuple[1]

def get_source():
    return decode(vsxr.command("source query"))

def tv_channel_up():
    tvr.shortcuts().channel_up()

def tv_channel_down():
    tvr.shortcuts().channel_down()

def tv_channel_1():
    tvr.shortcuts().channel(1)

def tv_pause():
    global pause_on
    if pause_on:
        requests.post(dr, data={'Keypress': 'Key' + 'Play'}, timeout=2)
        pause_on = False
    else:
        requests.post(dr, data={'Keypress': 'Key' + 'Pause'}, timeout=2)
        pause_on = True

def radio_channel_up():
    vsxr.command("preset up")

def radio_channel_down():
    vsxr.command("preset down")

def radio_channel_1():
    vsxr.command("preset 1")

def radio_mute():
    global pause_on
    global last_volume
    if pause_on:
        set_volume(last_volume)
        pause_on = False
    else:
        last_volume = get_volume()
        set_volume(0)
        pause_on = True

def tap(src):
    if src == SAT:
        tv_pause()
    if src == FM:
        radio_mute()
    elif src == CD:
        bd_pause()

def rotate_right():
    volume_up()

def rotate_left():
    volume_down()

def flip180(src):
    if src == SAT:
        tv_channel_1()
    elif src == FM:
        radio_channel_1()

def flip90(src):
    if src == SAT:
        tv_channel_up()
    elif src == FM:
        radio_channel_up()
    elif src == CD:
        bd_channel_up()   

def slide(src):
    if src == SAT:
        tv_channel_down()
    elif src == FM:
        radio_channel_down()
    elif src == CD:
        bd_channel_down()

def on_message(mqttc, obj, msg):
    global cube_on
    global second_slide
	
    j = json.loads(str(msg.payload.decode("utf-8", "ignore")))

    if j["action"] == "shake":
        cube_on = not cube_on

    if cube_on:
        src = get_source()
        if not second_slide and j["action"] == "slide":
            second_slide = True
        else:
            if j["action"] == "tap":
                tap(src)
            elif j["action"] == "rotate_right" and j["angle"] > 3.:
                rotate_right()
            elif j["action"] == "rotate_left" and j["angle"] < -3.:
                rotate_left()
            elif j["action"] == "flip180":
                flip180(src)
            elif j["action"] == "flip90":
                flip90(src)
            elif j["action"] == "slide":
                slide(src)
            second_slide = False

#    print("action: " + j["action"] + " ON: " + repr(cube_on))


mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.connect("127.0.0.1", 1883, 60)
mqttc.subscribe("zigbee2mqtt/cube", 0)

mqttc.loop_forever()
