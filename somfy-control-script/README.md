# Requirements

## pigpio
Install pigpio see http://abyz.me.uk/rpi/pigpio/download.html

### Autostart pigpiop

`sudo crontab -e`

Add

`@reboot /usr/local/bin/pigpiod -x -1`

# Connect 433 MHZ transmitter

Get a 433 MHZ transmitter like https://www.aliexpress.com/item/RF-wireless-receiver-module-transmitter-module-board-Ordinary-super-regeneration-315-433MHZ-DC5V-ASK-OOK-for/32271996421.html?spm=a2g0s.9042311.0.0.THH0rF

Note: The frequency of somfy is slightly different but it will work.

Connect the transmitter to your PI. Pin numbers:

* GND -> 2
* VVC -> 6
* DATA -> 12

Layout:

![https://docs.microsoft.com/en-us/windows/iot-core/learn-about-hardware/pinmappings/pinmappingsrpi](rp2_pinout.png)

# Copy files to PI
You need to copy somfy.py AND the folder somfy with its content to your PI. Default location

`/home/pi/somfy`

The structure looks like this:

/home/pi/somfy  
-- somfy.py  
-- somfy  
---- main.txt  

# Bind Remote Control
For the first time usage you have to bind your PI as a new remote control to your somfy motor:

* Get your normal Remote and long press the prog button on the baack side until the blinds move slightly
* Send the prog command from your PI `python somfy.py main prog`
* The blinds move slightly again
* Your PI is ready now

You can program multiple channels. Use any name you want in replacement of 'main' above. e.g.

`python somfy.py yourChannelName prog`

For each channel you need to create a file like [main.txt](somfy/main.txt). Just copy this file and rename it like yourChannelName.txt.
It contains the remote ID and a number that is incremented each time a command is send. This is needed to work with the somfy receiver. 
For more information about the protocol check [this](https://pushstack.wordpress.com/somfy-rts-protocol/)

# Run

## Move blinds down
`python somfy.py main down`

## Move blinds up
`python somfy.py main up`

## Stop blinds
`python somfy.py main stop`

# Source
This is based on [Pi-Somfy](https://github.com/Nickduino/Pi-Somfy)