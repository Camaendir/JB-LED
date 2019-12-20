from time import sleep
import copy

from strip import *
import paho.mqtt.client as mqtt

from MainLamp import *

def on_message(client, userdata, msg):
    topic = msg.topic
    if topic == "strip/command":
        print(msg)
    elif msg.topic.startswith("strip/effekt"):
        topic = topic[13:]
        for subengine in layer:
            if topic.startswith(subengine.mqtttopic):
                subengine.onmessage(topic=topic[len(subengine.mqtttopic):], payload=msg.payload)

def publishState():
    for subengine in layer:
        tp = subengine.getState()
        for subj in tp:
            client.publish(topic=subj[0], payload=[])

layer = [Fading()]
pixellength = 450

lastpixel = []

pixels = Strip()
pixels.create()
pixels.blackout()

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("strip/effekt/#")
client.subscribe("strip/command")
client.loop_start()



lastpixel =[[-1,-1,-1]] * pixellength
while True:
    frame =[[-1,-1,-1]] * pixellength
    for subengine in layer:
        if subengine.isEnabled:
            subengine.update()
            sub_frame = subengine.getFrame()
            print(sub_frame)
            index = 0
            for pixel in sub_frame:
                if -1 not in pixel:
                    frame[index] = pixel
                index = index + 1
    index = 0

    for pixelcolor in frame:
        for rgb in range(len(pixelcolor)):
            pixelcolor[rgb] = max(pixelcolor[rgb],0)

        if pixelcolor is not lastpixel[index]:
            pixels.setPixel(index, color=pixelcolor)
        index = index + 1
    pixels.show()
    lastpixel = copy.deepcopy(frame)
    sleep(0.01)
