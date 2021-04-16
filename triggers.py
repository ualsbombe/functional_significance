#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from psychopy import parallel
import platform
import serial
from subprocess import check_output
from os import listdir
from os.path import join

user = check_output('uname -n', shell=True)

PLATFORM = platform.platform()
if 'Linux' in PLATFORM:
    if user == b'stimpc-08\n':
        port = parallel.ParallelPort(address='/dev/parport0')  # on MEG stim PC
    elif user == b'lau\n': # testing with serial at home
        device_path = '/dev'
        devices = listdir('/dev')
        for device in devices:
            if 'ttyUSB' in device:
                break
    else:
        raise NameError('The current user: ' + str(user) + \
                        ' has not been prepared')
        address = join(device_path, device)
        port = serial.Serial(address=address, baudrate=38400, timeout=1)
else:  # on Win this will work, on Mac we catch error below
    port = parallel.ParallelPort(address=0xDFF8)  # on MEG stim PC


# NB problems getting parallel port working under conda env
# from psychopy.parallel._inpout32 import PParallelInpOut32
# port = PParallelInpOut32(address=0xDFF8)  # on MEG stim PC
# parallel.setPortAddress(address='0xDFF8')
# port = parallel

# Figure out whether to flip pins or fake it
try:
    port.setData(128)
except: # NotImplementedError:
    def setParallelData(code=1):
        if code > 0:
            # logging.exp('TRIG %d (Fake)' % code)
            print('TRIG %d (Fake)' % code)
            pass
else:
    port.setData(0)
    setParallelData = port.setData
