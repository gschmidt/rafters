#!/usr/bin/env python
import serial
import time
import colorsys
import math
import OSC
import threading

receive_port = 7000
send_port = 9000

sat_ = .75
br_ = .9999
hueWidth_ = .33

# OSC

osc = OSC.OSCServer(('0.0.0.0', receive_port))
osc.addDefaultHandlers()

def default_handler(addr, tags, stuff, source):
  print addr, stuff
  return None

def test_handler(addr, tags, stuff, source):
  c = OSC.OSCClient()
  c.connect((source[0], send_port))
  msg = OSC.OSCMessage()
  msg.setAddress("/2/test2")
  msg.append(stuff)
  c.send(msg)
  return None

def br_handler(addr, tags, stuff, source):
  global br_
  br_ = min(stuff[0], .9999)
  return None

def sat_handler(addr, tags, stuff, source):
  global sat_
  sat_ = stuff[0]
  return None

def width_handler(addr, tags, stuff, source):
  global hueWidth_
  hueWidth_ = stuff[0]
  return None

osc.addMsgHandler("/1/brightness", br_handler)
osc.addMsgHandler("/1/fader1", sat_handler)
osc.addMsgHandler("/1/fader2", width_handler)
osc.addMsgHandler("/2/test1", test_handler)
osc.addMsgHandler("default", default_handler)

oscThread = threading.Thread( target = osc.serve_forever )
oscThread.start()

# LED rendering

ser = serial.Serial(
  port='/dev/ttyACM0',
  baudrate = 115200 * 2,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=0
)

ledsPerStrip = 240
strips = 8
totalLeds = ledsPerStrip * strips

buf = bytearray(totalLeds * 3)

# sync up
for i in range(0, totalLeds * 3):
  buf[i] = 255
ser.write(buf)
ser.write(bytearray([0]))

# here we go
frame = 0
hueCenter = 0
lastTime = time.time()
try:
  while 1: 
    ser.write(bytearray([0]))
    now = time.time()
    hueCenter = (hueCenter + (now - lastTime) / 30) % 1.0

    hueStart = hueCenter - hueWidth_ / 2 + 1.0
    hueEnd = hueCenter + hueWidth_ / 2
    hueStep = (hueEnd - hueStart) / ledsPerStrip

    ptr = 0
    for i in range(0, ledsPerStrip):
      (r, g, b) = colorsys.hsv_to_rgb(hueStart + i * hueStep, sat_, br_)
      buf[ptr] = int(r * 256)
      buf[ptr + 1] = int(g * 256)
      buf[ptr + 2] = int(b * 256)
      ptr += 3

    ser.write(buf)
except KeyboardInterrupt:
  osc.close()
  print "Waiting for server to finish.."
  oscThread.join()
  print "done"
