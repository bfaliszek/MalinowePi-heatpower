#!/bin/bash

modprobe w1-gpio
modprobe w1-therm
sleep 2

python pi.py

