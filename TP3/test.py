import machine
from machine import I2C
import pycom
import sys
import time

pycom.heartbeat(True)

i2c = machine.I2C(0, mode=I2C.MASTER, pins=('P22', 'P21'))
scan = i2c.scan()

while True:
  trame = i2c.readfrom(scan[1],255)
  print(trame)
  print(trame.decode().replace('\n',''))
  print('\n')
  time.sleep(0.2)