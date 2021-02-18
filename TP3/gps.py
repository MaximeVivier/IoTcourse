import pycom as pc
import time
import machine
from machine import I2C

i2c = I2C(0, mode = I2C.MASTER, pins=('P9','P10'))
scan = i2c.scan()

print(len(scan))

# [MSB,LSB] = i2c.readfrom(scan,2) # On lit la derniere valeur dans le registre du capteur
# output_hex = hex(MSB) + hex(LSB)[2] # on se débarasse des 4 derniers bits du LSB
# output_dec = int(output_hex)
