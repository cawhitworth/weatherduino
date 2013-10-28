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