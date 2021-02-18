# Maxime VIVIER
# Adrien LAFFARGUE
import pycom as pc
import time
import machine

# Initialiser la lecture du pin analogique
adc = machine.ADC()             # create an ADC object
apin = adc.channel(pin='P13',attn=machine.ADC.ATTN_11DB)   # create an analog pin on P16

# Désactiver le clignotment de la LED du au fonctionnement classique de la pycom
pc.heartbeat(False)

# Fonction qui applique des formules afin de tranposer des valeurs de HSL en RGB
# Lien vers la formule : https://www.rapidtables.com/convert/color/hsl-to-rgb.html
# L'objectif est de fixer la saturation et la luminense et uniquement faire varier HUE
# On fait varier l'angle HUE entre 0 et 359 degré pour balayer l'ensemble des couleurs
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
    rgb_val = (round((Rp+m)*255),round((Gp+m)*255),round((Bp+m)*255))
    return(rgb_val)


while True:
    # Empiriquement, avec notre potentiomètre on a trouvé que les couleurs
    # que nous voulons balayer ici entre le bleu et le rouge sont obtenues
    # en faisant varier l'angle HUE entre 0 et 235 degrés.
    # 
    # Nous fixons la sauration et la luminense à 0.8 et 0.4, les couleurs
    # sont assez vives.
 
    red_value_angle = 235
    saturation = 0.8
    luminense = 0.4

    # On lit la valeur du pin.
    val = apin()

    # On établie une "bijection" (discrètement) entre les valeurs du pin qui
    # vont de 0 à 4095 et les valeurs d'angle voulues entre 0 et 235.
    angle = round(val*red_value_angle/4096)

    # On calcule les valeurs RGB correspondantes grâce à notre focntion.
    rgb = getRGB(angle, saturation, luminense)

    # Enfin on la transforme en format hexadécimal.
    hexa = ''.join(['0x'] + [hex(value)[2:] for value in rgb])

    # print('Potar : ', val)
    # print('Angle : ', angle)
    # print('RGB : ', rgb)
    # print('\n')

    # On allume la LED avec la couleur trouvée.
    pc.rgbled(int(hexa,16))

    # Répeter cette opération tous les dixièmes de seconde
    time.sleep(0.1)