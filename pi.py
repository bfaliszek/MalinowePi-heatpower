#!/usr/bin/python

from decimal import Decimal
import sys
import RPi.GPIO as GPIO
from time import sleep

class HD44780:

    def __init__(self, pin_rs=7, pin_e=8, pins_db=[25, 24, 23, 18]):
        
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = pins_db

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_e, GPIO.OUT)
        GPIO.setup(self.pin_rs, GPIO.OUT)
        for pin in self.pins_db:
            GPIO.setup(pin, GPIO.OUT)

        # przygotuj diody do jarania
        GPIO.setup(17, GPIO.OUT)
        GPIO.setup(22, GPIO.OUT)

        self.clear()

    def clear(self):
        """ Reset LCD """
        self.cmd(0x33) 
        self.cmd(0x32) 
        self.cmd(0x28) 
        self.cmd(0x0C) 
        self.cmd(0x06) 
        self.cmd(0x01) 
        
    def cmd(self, bits, char_mode=False):
        """ Command to LCD """

        sleep(0.011)
        bits=bin(bits)[2:].zfill(8)
        
        GPIO.output(self.pin_rs, char_mode)

        for pin in self.pins_db:
            GPIO.output(pin, False)

        for i in range(4):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i], True)

        GPIO.output(self.pin_e, True)
        GPIO.output(self.pin_e, False)

        for pin in self.pins_db:
            GPIO.output(pin, False)

        for i in range(4,8):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i-4], True)

        GPIO.output(self.pin_e, True)
        GPIO.output(self.pin_e, False)

    def jaraj_diode(self, color='red'):
        pins = [17,22]
        [GPIO.output(pin, False) for pin in pins]

        if color == 'green':
            pin = 17
        elif color == 'red':
            pin = 22
        else:
            pin = None
        if pin:
            GPIO.output(pin, True)
        
    def message(self, text):
        """ Send string to LCD """

        for char in text:
            if char == '\n':
                self.cmd(0xC0) # next line
            else:
                self.cmd(ord(char),True)

if __name__ == '__main__':

    lcd = HD44780()
    record = 0
    # start heat game, beat the sun

    # @author Lukasz
    # @author Marcin
    # @author Marek (onjin)


    print
    print "-" * 80
    print " cel gry: osiagnac najwyzsza temperatury uzywajac tylko ludzkiego ciala ;)"
    print "-" * 80
    print
    while True:
        with open("/sys/bus/w1/devices/28-0000054e97d9/w1_slave") as f:
            temp = Decimal(f.readlines()[1].split('=')[1])
            temp = temp/1000

            # store record
            if temp > record:
                record = temp
                for i in range(5):
                    lcd.jaraj_diode('red')
                    sleep(.1)
                    lcd.jaraj_diode('green')
                    sleep(.1)
                lcd.jaraj_diode('none')
            lcd.clear()

            # display "current record"
            msg = "%-7s  %7s" % (str(temp), str(record))
            lcd.message(msg)
            lcd.message("\n")

            # display temp as bar in second line
            bar = int((temp - 20) * 16 / 80)
            lcd.message(str('*' * bar))
        sleep(2)
