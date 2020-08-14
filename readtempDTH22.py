#!/usr/bin/python3

# readtempDTH22

import time
import RPi.GPIO as gpio
"""
DHT22 sends high bits first
DATA = 8 bit integral RH data + 8 bit decimal RH data + 8 bit integral T data + 8 bit decimal T data + 8 bit check sum
checksum is adding the 4 bytes and taking the last 8 bits

MCU send start signal (pulse low for 1 ms)
MCU wait 20-40 us for DHT22 response

DHT22 response is a low signal for 80us
then a high for 80 us
data bit start to follow

low signal for 50us
high signal (70us for a 1, or 26us to 28us for a 0)

"""

class Readtemp:
    def __init__(self, pin):
        self._pin = pin
        self._debug = False
        self._timmings:float = []
    
    def errorMsg(self, errorNo):
        if errorNo == -1:
            return("No response received back from DHT22")
        if errorNo == -2:
            return("Unsync between DTH22 and Pi")
        if errorNo == -3:
            return("Line stuck low")
        if errorNo == -4:
            return("Underrun (no more bit)")
        if errorNo == -5:
            return("Checksum error")
        return("No error")

    def setDebug(self, setit):
        self._debug = setit

    def _getbit(self):
        # it should always be LOW at this point, but let's check it anyway
        if gpio.input(self._pin):
            return("S") # line is stuck high before the bit So maybe we missed the beginning of it
        # ok, the line was LOW. wait for the bit now
        start = time.time()
        while not gpio.input(self._pin): # wait to go HIGH (beginning of the bit)
            if time.time() - start > 0.0001:
                return("T") # stuck while waiting for the line to go HIGH
        # now it's HIGH, calculate the length of the HIGH
        start = time.time() # ok, the line is HIGH. Let's measure its width
        while  gpio.input(self._pin):
            if time.time() - start > 0.0001: # more than 1ms, it's stuck
                return("U") # line got stuck HIGH while waiting for the end of the bit
        tim = time.time() - start
        self._timmings.append(tim)
        if (tim) > 0.0000400: # 0 = 26-28us,  1=70us
            return("1")
        else:
            return("0")

    def _sendStartbit(self):
        gpio.setup(self._pin, gpio.OUT, initial=gpio.LOW)
        #gpio.output(BIT,0)
        time.sleep(0.001) # keep it low for 1ms at least
        gpio.output(self._pin,1) # then back HIGH
        gpio.setup(self._pin, gpio.IN, pull_up_down = gpio.PUD_UP)

    def _waitResponse(self):
        # response should come within 20-40 us from DTH
        start = time.time() # lockup protection
        while gpio.input(18): # Should be low pretty soon now
            if (time.time() - start) > 0.001: # if more than 1ms, it's too long
                return(0)
        # we are now at the beginning of its response of 80 us
        return(1)

    def _getData(self):
        st = ''
        for _ in range(40):
            st += self._getbit()
        return(st)

    def _validateData(self, data):
        if self._debug:
            print(data[0:8], data[8:16], data[16:24], data[24:32], data[32:40])
        for i in range(len(data)):
            if (data[i] < "0") or (data[i] > "1"):
                if data[i] == 'S':
                    return(-2) # unsync
                if data[i] == 'T':
                    return(-3) # line stuck low
                if data[i] == 'U':
                    return(-4) # underrun (no more bit)
        tl = 0
        for i in range(4):
            tl += int(data[i*8:i*8+8], 2)
        while tl > 255:
            tl -= 256
        if self._debug:
            print("Total added:",tl, "Chksum:",int(data[32:40], 2))
        if tl == int(data[32:40], 2): # compare total to checksum
            return(0)
        return(-5) # bad checksum

    def temp(self, retry = 3):
        # set the line normal HI (pulled up)
        for tr in range(retry):
            self._timmings.clear()
            gpio.setup(self._pin, gpio.IN, pull_up_down = gpio.PUD_UP)
            time.sleep(0.5) # wait for stabilized
            #print(self._startbit())
            #return(1,1)
            self._sendStartbit()
            if not self._waitResponse():
                if tr == retry-1:
                    return(85, -1) # error
                time.sleep(1.5)
                continue
            time.sleep(0.000050) # the response if 80us long, so wait a bit before getting the bits
            st = self._getData() # go get the 40 bits
            er = self._validateData(st)
            if er < 0:
                if tr == retry - 1:
                    return(85, er) # timeout error
                time.sleep(1.5)
                continue
            hum = int(st[0:16], 2) / 10
            temp = int(st[16:32], 2) / 10
            #print(st)
            return(temp,hum)
