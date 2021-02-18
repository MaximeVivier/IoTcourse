import pycom
import time
import upip

pycom.heartbeat(False)
pycom.rgbled(0x111111)
time.sleep(1)
print('ouloulou')
c = Color(hsl=(1,1,1))