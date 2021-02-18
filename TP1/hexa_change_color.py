import pycom as pc
import time
import machine

adc = machine.ADC()             # create an ADC object
apin = adc.channel(pin='P13',attn=machine.ADC.ATTN_11DB)   # create an analog pin on P16

def getRGB(h,s,l):
    # h angle en degrés, s et l de 0 à 1
    h = 0 if h==360 else h
    c = (1-abs(2*l-1))*s
    x = c*(1-abs((h/60)%2-1))
    m = l-c/2
    if h>=0 and h<60:
        (Rp,Gp,Bp) = (c,x,0)
    if h>=60 and h<120:
        (Rp,Gp,Bp) = (x,c,0)
    if h>=120 and h<180:
        (Rp,Gp,Bp) = (0,c,x)
    if h>=180 and h<240:
        (Rp,Gp,Bp) = (0,x,c)
    if h>=240 and h<300:
        (Rp,Gp,Bp) = (x,0,c)
    if h>=300 and h<360:
        (Rp,Gp,Bp) = (c,0,x)
    rgb_val = ((round(Rp+m)*255),round((Gp+m)*255),round((Bp+m)*255))
    return(rgb_val)

while True:
    time.sleep(0.1)
    val = apin()
    angle = round(val*360/4096)
    rgb = getRGB(angle,1,0.5)
    hexa = ''.join(['0x'] + [hex(value)[2:] for value in rgb])
    pc.heartbeat(False)
    pc.rgbled(int(hexa,16))