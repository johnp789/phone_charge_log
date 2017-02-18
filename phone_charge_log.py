#!/usr/bin/env python

import datetime
import signal
import sys
import time
import gpib

dc1 = gpib.dev(0, 1) # Agilent 66332A on GPIB bus 0, address 1

# thanks to http://stackoverflow.com/questions/8600161/executing-periodic-actions-in-python
def do_every(period, count, f, *args):
    def g_tick():
        t = time.time()
        count = 0
        while True:
            count += 1
            yield max(t + count * period - time.time(), 0)
    g = g_tick()
    for i in range(count):
        time.sleep(next(g))
        f(*args)

t0 = None

def meas():
    gpib.write(dc1, 'MEAS:CURR?')
    s = gpib.read(dc1, 1000)
    global t0
    if t0 is None:
        t0 = datetime.datetime.now()
        t = datetime.timedelta(0)
    else:
        t = datetime.datetime.now() - t0
    print('{}.{:06d},{}'.format(t.seconds, t.microseconds, s.decode().rstrip()))
    sys.stdout.flush()

gpib.write(dc1, '*IDN?')
s = gpib.read(dc1, 1000)
print('#', s.decode().rstrip())

gpib.write(dc1, 'SENS:CURR:DET DC')
gpib.write(dc1, 'SENS:CURR:DET?')
s = gpib.read(dc1, 1000)
print('#', s.decode().rstrip())

gpib.write(dc1, 'VOLT 5.0')
gpib.write(dc1, 'VOLT?')
s = gpib.read(dc1, 1000)
print('#', s.decode().rstrip(), 'V')

gpib.write(dc1, 'CURR 2.0')
gpib.write(dc1, 'CURR?')
s = gpib.read(dc1, 1000)
print('#', s.decode().rstrip(), 'A')

def output_off(dev):
    gpib.write(dev, 'OUTP OFF')

def handler(signum, frame):
    output_off(dc1)
    sys.exit(1)

signal.signal(signal.SIGINT, handler)
gpib.write(dc1, 'OUTP ON')
do_every(period = 1/2, count = 2 * 4 * 3600, f = meas)

output_off(dc1)
