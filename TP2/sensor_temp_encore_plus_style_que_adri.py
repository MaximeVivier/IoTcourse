import pycom as pc
import time
from machine import I2C
"""
Gérer les négatifs
WTF l'étalonnage
"""
resolution_temp = 0.0625 #augmentation de tempé pour une incrémentation dans le codage

i2c = I2C(0, pins=('P9','P10'))
i2c.init(I2C.MASTER, baudrate=20000)
scan = i2c.scan()[0] # contient l'adresse du capteur

adc = machine.ADC()
apin = adc.channel(pin='P13',attn=machine.ADC.ATTN_11DB)

HR = [  [0.76,0.73,0.70,0.67,0.63,0.60,0.56],
        [1.06,1.03,1.03,1.02,0.99,0.96,0.93],
        [1.36,1.34,1.35,1.36,1.34,1.32,1.29],
        [1.67,1.66,1.67,1.68,1.67,1.66,1.64],
        [1.97,1.97,1.98,1.98,1.98,1.98,1.96],
        [2.25,2.25,2.26,2.26,2.26,2.26,2.25],
        [2.51,2.51,2.50,2.51,2.50,2.50,2.48],
        [2.73,2.72,2.70,2.73,2.70,2.68,2.66]    ]

temp_list = [10,15,20,25,30,35,40]
HR_list = [20,30,40,50,60,70,80,90]

def compute_ratio(threshold1, threshold2, actual_value):
  return((actual_value - threshold1)/(threshold2 / threshold1))

def compute_value_from_ratio(volt1, volt2, ratio):
  return(volt1*ratio + volt2*(1-ratio))



while True:
    [MSB,LSB] = i2c.readfrom(scan,2) # On lit la derniere valeur dans le registre du capteur
    output_hex = hex(MSB) + hex(LSB)[2] # on se débarasse des 4 derniers bits du LSB
    output_dec = int(output_hex)
    temperature = output_dec * resolution_temp
    print(temperature)

    index_col1 = temp_list.index((temperature//5)*5)

    ratio = compute_ratio(temp_list[index_col1], temp_list[index_col1+1], temperature)

    volt1 = compute_value_from_ratio()

    output_RH_sensor = apin()*3.3/4096 # tension de sortie du capteur d'humidité

    time.sleep(0.1)