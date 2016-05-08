#!/usr/bin/env python
import serial
import time
import colorsys
import math

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
while 1: 
  ser.write(bytearray([0]))
  now = time.time()

  hueStart = (now / 30) % 1.0
  hueEnd = hueStart + .33
  hueStep = (hueEnd - hueStart) / ledsPerStrip

  ptr = 0
  for i in range(0, ledsPerStrip):
    (r, g, b) = colorsys.hsv_to_rgb(hueStart + i * hueStep, .75, .9999)
    buf[ptr] = int(r * 256)
    buf[ptr + 1] = int(g * 256)
    buf[ptr + 2] = int(b * 256)
    ptr += 3

  ser.write(buf)
