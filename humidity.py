#!/usr/bin/python3

import time
import RPi.GPIO as gpio
import readtempDTH22

def main():
    try:
        readtemp = readtempDTH22.Readtemp(18)
        gpio.setmode(gpio.BCM)
        time.sleep(1)
        while True:
            temp, hum = readtemp.temp()
            if hum < 0:
                print(readtemp.errorMsg(hum))
            else:
                print("Temp: "+str(temp)+"C  Humidity:"+str(hum)+"%")
            time.sleep(2) # datasheet specifies no less than 2 seconds between calls
    except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
        print("Cleaning up")
        gpio.cleanup()

if __name__ == '__main__':
    main()
