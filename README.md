#Weatherduino#

I've got a simple wireless weather station that transmits on 433MHz. We're having a hack week at work notionally related to the Internet Of Things, so I've decided to try and reverse engineer it using an off-the-shelf 433MHz receiver and an Arduino.

## Notes ##

**Monday morning**

Connected up the Arduino to the receiver (5V on the arduino to VCC, GND to GND, pin 2 [interrupt 0] to a data pin on the receiver).

Tried the [rc_switch](https://code.google.com/p/rc-switch/) library to see if we could trivially dump any data, but produced no results.

Wired an LED in parallel with the data pin; saw it flashing like crazy. Using a handheld radio confirmed loads of noise around 433Mhz.

After considerable mucking about, figured out the noise was coming from the USB power supply for the arduino - running the sketch (with debug LED) powered by battery gave a much cleaner output.

However, rc_switch is still not giving us anything useful.

Dumping the pulse-duration data (using the dump_433 sketch - assumes a 433MHz receiver on interrupt 0) shows the weather station appears to be transmitting PWM encoded data (see dump.dat). The interrupt is triggered on every transition, and every other value is ~1000ms, with ~500ms and ~1500ms pulses presumably encoding the data:

![](https://dl.dropboxusercontent.com/u/18971919/waveduino/pulses.png)

The next step is to decode this and try and correspond it to the data I see on the weather station base unit:

![](https://dl.dropboxusercontent.com/u/18971919/waveduino/base_unit_and_arduino.jpg)

**Monday afternoon**

Written a python script to decode the dumps making the assumptions above - working on 500ms == 0, 1500ms == 1.

Also assuming little-endian for the moment, but can change that later. Need to cross-correlate the dumps with actual data from the weather station next and see if I can reverse-engineer the format.

The dumps appear to be either 159 or 63 pulses (corresponding to 80 or 32 bits) - wondering if it might be a key-frame/delta type deal.

The longer pulses appear to have a common header: (sorry, the binary is backwards...)

    LSB           MSB
     0 0 0 0 0 0 0 0 | 0
     1 0 1 0 1 1 0 1 | 181
     0 0 1 1 1 1 0 1 | 188
     1 0 0 0 0 0 0 1 | 129
