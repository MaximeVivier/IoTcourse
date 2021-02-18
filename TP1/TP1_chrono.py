from machine import Timer
import time

chrono = Timer.Chrono()

chrono.start()
while True:
    time.sleep(0.1)
    print(chrono.read())
