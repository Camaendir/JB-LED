from time import sleep
import copy

from strip import *
import paho.mqtt.client as mqtt

from MainLamp import *

global layer
global brightnis

def on_message(client, userdata, msg):   
    topic = msg.topic
    if topic == "strip/command":
        print(msg.payload)
        if msg.payload == "update":
            publishState()
        elif msg.payload == "reset":
            pixels.blackout()
    elif topic.startswith("strip/color/"):
        topic = topic[12:]
        if topic == "brightnis":
            print(int(msg.payload))
            brightnis= int(msg.payload)
    elif topic.startswith("strip/effekt/"):
        topic = topic[13:]
        for subengine in layer:
            if topic.startswith(subengine.mqttTopic+"/"):
                t = topic[len(subengine.mqttTopic)+1:]
                subengine.on_message(t,msg.payload)

def publishState():
    client.publish(topic="strip/info/color/brightnis",payload=brightnis)
    for subengine in layer:
        tp = subengine.getStates()
        for subj in tp:
            client.publish(topic=subj[0], payload=subj[1])


layer = [Fading(), Lamp(), Alarm()]
brightnis = 100 
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
client.subscribe("strip/color/#")
client.loop_start()
publishState()


lastpixel =[[-1,-1,-1]] * pixellength
while True:
    frame =[[-1,-1,-1]] * pixellength
    for subengine in layer:
        if subengine.isEnabled:
            subengine.update()
            sub_frame = subengine.getFrame()
            
            index = 0
            for pixel in sub_frame:
                if -1 not in pixel:
                    frame[index] = pixel
                index = index + 1
    index = 0

    for pixelcolor in frame:
        br = 255- brightnis 
        for rgb in range(len(pixelcolor)):
            
            pixelcolor[rgb] = max(pixelcolor[rgb],0)

        if pixelcolor is not lastpixel[index]:
            pixels.setPixel(index, color=pixelcolor)
        index = index + 1
    pixels.show()
    lastpixel = copy.deepcopy(frame)
    sleep(0.01)
