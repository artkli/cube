import socket
import json
import paho.mqtt.client as mqtt


cube_on = False
second_slide = False


def lirc_send(key):
#    print("IR send: " + key)	
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect("/var/run/lirc/lircd")
    s.sendall("SEND_ONCE tv " + key + "\n")
    s.close()


def on_message(mqttc, obj, msg):
    global cube_on
    global second_slide
	
    j = json.loads(str(msg.payload.decode("utf-8", "ignore")))

    if j["action"] == "shake":
        cube_on = not cube_on

    if cube_on:
        if not second_slide and j["action"] == "slide":
            second_slide = True
        else:
            if j["action"] == "tap":
                lirc_send("KEY_POWER")
            elif j["action"] == "rotate_right" and j["angle"] > 35.:
                lirc_send("KEY_VOLUMEUP")
            elif j["action"] == "rotate_left" and j["angle"] < -35.:
                lirc_send("KEY_VOLUMEDOWN")
            elif j["action"] == "flip180":
                lirc_send("KEY_1")
            elif j["action"] == "flip90":
                lirc_send("KEY_CHANNELUP")
            elif j["action"] == "slide":
                lirc_send("KEY_CHANNELDOWN")
            second_slide = False

#    print("action: " + j["action"] + " ON: " + repr(cube_on))


mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.connect("127.0.0.1", 1883, 60)
mqttc.subscribe("zigbee2mqtt/cube", 0)

mqttc.loop_forever()
