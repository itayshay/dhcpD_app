#!/usr/bin/python3.6

import os.path, time
import random
import time
import sys
import shutil

examFile = '/etc/sysconfig/dhcpd'
prevMod = ''
lastMod = ''

print("last modified: %s" % time.ctime(os.path.getmtime(examFile)))
# print("created: %s" % time.ctime(os.path.getctime(examFile)))

while(True):
    lastMod = time.ctime(os.path.getmtime(examFile))
    # print ("lastMod =", lastMod)
    if not lastMod==prevMod:
        prevMod = lastMod
        os.system('service networkd restart')
    time.sleep(15)


