# Maxime VIVIER
# Adrien LAFFARGUE
import pycom as pc
import time
import machine
from machine import I2C

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

# Calcul de la position en % de actual_value sur l'intervalle [threshold1, threshold1]
def compute_ratio(threshold1, threshold2, actual_value):
  return((actual_value - threshold1)/(threshold2 - threshold1))


while True:
    [MSB,LSB] = i2c.readfrom(scan,2) # On lit la derniere valeur dans le registre du capteur
    output_hex = hex(MSB) + hex(LSB)[2] # on se débarasse des 4 derniers bits du LSB
    output_dec = int(output_hex)
    temperature = output_dec * resolution_temp
    print('Temp ', temperature)

    volt_RH_sensor = apin()*3.3/4096 # tension de sortie du capteur d'humidité

    print('Voltage ', volt_RH_sensor)

    index_HR, volt_diff_min = 0, 10000

    round_temp = (temperature // 5)*5 + 5*round((temperature%5)/5)

    col_temp = temp_list.index(round_temp)

    if volt_RH_sensor < HR[0][col_temp]:
      # En dessous du seuil d'humidité msurable on renvoie 20% avec un message
      print('En dessous du seuil d\'humidité mesurable')
      HR_final = HR_list[0]
    elif volt_RH_sensor > HR[-1][col_temp]:
      # Au dessus du seuil d'humidité msurable on renvoie 90% avec un message
      print('Au dessus du seuil d\'humidité mesurable')
      HR_final = HR_list[-1]
    else:
      # Toujours à température mesurée, on repère ici l'index de la ligne pour lequel la
      # tension du potar (donc du capteur d'humidité) est compris entre les valeurs de
      # tension à index_HR et index_HR + 1.
      for lgn_HR in range(len(HR_list)-1):
        diff1 = HR[lgn_HR][col_temp] - volt_RH_sensor
        diff2 = HR[lgn_HR+1][col_temp] - volt_RH_sensor
        if diff1*diff2 < 0:
          index_HR = lgn_HR
          break
      
      # On récupère de la boucle précédante les deux tensions qui entourent l'output du potar.
      # On calcul ici la position de la valeur de tension dans l'intervalle déterminé.
      # On obtient un ratio.
      ratio = compute_ratio(HR[lgn_HR][col_temp], HR[lgn_HR+1][col_temp], volt_RH_sensor)

      # On applique le ratio aux valeurs rondes d'humidité pour en retirer une valeur interpolée
      # Nous avons décidé de faire une interpolation pour l'humidité car les écarts de tension
      # entre deux valeurs étaient élevés. Nous avons décidé seulement d'arrondir à la température
      # la plus proche car les écarts de valeur de tension entre 2 temprératures voisines peuvent
      # être négligeables.
      HR_final = HR_list[index_HR] + 10*ratio

    print('Humidite ', HR_final)
    print('\n')

    time.sleep(0.2)