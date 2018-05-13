#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pigpio
import sys

TXGPIO = 18  # 433.42 MHz emitter on GPIO 4

# Button values
btnUp = 0x2
btnMyStop = 0x1
btnDown = 0x4
btnProg = 0x8

frame = bytearray(7)

def sendCommand(telco, bouton, repetition):  # Sending a frame
    # Sending more than two repetitions after the original frame means a button kept pressed and moves the blind in steps
    # to adjust the tilt. Sending the original frame and three repetitions is the smallest adjustment, sending the original
    # frame and more repetitions moves the blinds up/down for a longer time.
    # To activate the program mode (to register or de-register additional remotes) of your Somfy blinds, long press the
    # prog button (at least thirteen times after the original frame to activate the registration.

    checksum = 0

    with open("somfy/" + telco + ".txt", 'r') as file:  # the files are in a subfolder "somfy"
        data = file.readlines()

    teleco = int(data[0], 16)
    code = int(data[1])
    data[1] = str(code + 1)

    print hex(teleco)
    print code

    with open("somfy/" + telco + ".txt", 'w') as file:
        file.writelines(data)

    pi = pigpio.pi()  # connect to Pi

    if not pi.connected:
        exit()

    pi.wave_add_new()
    pi.set_mode(TXGPIO, pigpio.OUTPUT)

    print "Remote  :      " + "0x%0.2X" % teleco
    print "Button  :      " + "0x%0.2X" % bouton
    print "Rolling code : " + str(code)
    print ""

    frame[0] = 0xA7;  # Encryption key. Doesn't matter much
    frame[1] = bouton << 4  # Which button did  you press? The 4 LSB will be the checksum
    frame[2] = code >> 8  # Rolling code (big endian)
    frame[3] = (code & 0xFF)  # Rolling code
    frame[4] = teleco >> 16  # Remote address
    frame[5] = ((teleco >> 8) & 0xFF)  # Remote address
    frame[6] = (teleco & 0xFF)  # Remote address

    print "Frame  :    ",
    for octet in frame:
        print "0x%0.2X" % octet,
    print ""

    for i in range(0, 7):
        checksum = checksum ^ frame[i] ^ (frame[i] >> 4)

    checksum &= 0b1111;  # We keep the last 4 bits only

    frame[1] |= checksum;

    print "With cks  : ",
    for octet in frame:
        print "0x%0.2X" % octet,
    print ""

    for i in range(1, 7):
        frame[i] ^= frame[i - 1];

    print "Obfuscated :",
    for octet in frame:
        print "0x%0.2X" % octet,
    print ""

    # This is where all the awesomeness is happening. You're telling the daemon what you wanna send
    wf = []
    wf.append(pigpio.pulse(1 << TXGPIO, 0, 9415))  # wake up pulse
    wf.append(pigpio.pulse(0, 1 << TXGPIO, 89565))  # silence
    for i in range(2):  # hardware synchronization
        wf.append(pigpio.pulse(1 << TXGPIO, 0, 2560))
        wf.append(pigpio.pulse(0, 1 << TXGPIO, 2560))
    wf.append(pigpio.pulse(1 << TXGPIO, 0, 4550))  # software synchronization
    wf.append(pigpio.pulse(0, 1 << TXGPIO, 640))

    for i in range(0, 56):  # manchester enconding of payload data
        if ((frame[i / 8] >> (7 - (i % 8))) & 1):
            wf.append(pigpio.pulse(0, 1 << TXGPIO, 640))
            wf.append(pigpio.pulse(1 << TXGPIO, 0, 640))
        else:
            wf.append(pigpio.pulse(1 << TXGPIO, 0, 640))
            wf.append(pigpio.pulse(0, 1 << TXGPIO, 640))

    wf.append(pigpio.pulse(0, 1 << TXGPIO, 30415))  # interframe gap

    for j in range(1, repetition):  # repeating frames
        for i in range(7):  # hardware synchronization
            wf.append(pigpio.pulse(1 << TXGPIO, 0, 2560))
            wf.append(pigpio.pulse(0, 1 << TXGPIO, 2560))
        wf.append(pigpio.pulse(1 << TXGPIO, 0, 4550))  # software synchronization
        wf.append(pigpio.pulse(0, 1 << TXGPIO, 640))

        for i in range(0, 56):  # manchester enconding of payload data
            if ((frame[i / 8] >> (7 - (i % 8))) & 1):
                wf.append(pigpio.pulse(0, 1 << TXGPIO, 640))
                wf.append(pigpio.pulse(1 << TXGPIO, 0, 640))
            else:
                wf.append(pigpio.pulse(1 << TXGPIO, 0, 640))
                wf.append(pigpio.pulse(0, 1 << TXGPIO, 640))

        wf.append(pigpio.pulse(0, 1 << TXGPIO, 30415))  # interframe gap


    pi.wave_add_generic(wf)
    wid = pi.wave_create()
    pi.wave_send_once(wid)
    while pi.wave_tx_busy():
        pass
    pi.wave_delete(wid)

    pi.stop()

command = btnUp

if sys.argv[2] == "up":
    command = btnUp
if sys.argv[2] == "down":
    command = btnDown
if sys.argv[2] == "stop":
    command = btnMyStop
if sys.argv[2] == "prog":
    command = btnProg

sendCommand(sys.argv[1], command, 2)