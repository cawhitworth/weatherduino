#Weatherduino#

I've got a simple wireless weather station that transmits on 433MHz. We're having a hack week at work notionally related to the Internet Of Things, so I've decided to try and reverse engineer it using an off-the-shelf 433MHz receiver and an Arduino.

## Notes ##

**Tuesday end-of-day**

A bit frustrated; I'm failing to see any clear pattern in the logs/captures I've got. Probably best put it to bed for now and try again tomorrow.

**Tuesday afternoon - Interlude**

[David Dunn](http://twitter.com/dcdunn) from [Electric Imp](http://electricimp.com) dropped by Red Gate to give a quick demonstration of their Internet of Things platform and leave a couple of devkits behind - the intention is to get the arduino uploading data to the cloud using this if I can ever decode the data format.

**Tuesday afternoon**

Trying various types of data analysis. It's confusing. For example, a change of humidity from 41% to 42% (and no change in anything else) causes the final two nibbles to change thus:

    1001 1110   Before
    1101 1010   After
    -X-- -X--   Changed bits
    
However, a change of temperature from 24.2C to 24.3C (and no change in anything else) causes the final two nibbles to change thus:

    1001 1110   Before
    1100 1001   After
    -X-X -XXX   Changed bits

Which is - bit 2 of each word changes when either the humidity or the temperature changes, but there are no changes in the data for humidity that aren't also in the changes for the temperature.

I've now written a script which determines which bits in the data change over time. For steady wind/rain, the pattern appears to be:

    Long diffs:
    - - - -   - - - -   - - - -   - - - -
    - - - -   - - - -   X X X X   X X X X
    - - - -   X X X X   - - - -   - - - -
    - - - -   - - - -   - - - -   - - - -
    - - - -   - - - -   X X X X   X X X X
    Short diffs:
    - - - -   - - - -   - - - -   - - - -
    - - - -   - - - -   X X X X   X X X X

**Tuesday morning**

Diffing between packets of data added, along with various readability improvements for the serial logger.

We appear to see either 80-bit or 32-bit bursts of data from the transmitter, so the serial logger recognises these. Additionally, the 32-bit bursts appear to be identical to the last 32-bits of the 80-bit bursts.

The serial logger now diffs the packets it receives - the first 48-bits of a long packet get compared to the first 48-bits of the previous long packet; short packets or the last 32-bits of a long packet get compared to the last short packet or last 32-bits of a long packet received.

At the same time, a webcam is now pointed at the base station and captures an image every time the serial logger registers a snapshot:

![](https://dl.dropboxusercontent.com/u/18971919/waveduino/2013-10-29-12-24-33.jpg)

The serial logger also logs the time/date, so we can correlate the two:

    LONG PACKET @ 2013-10-29-12-24-33
    0 0 0 0 | 0 0 0 0 | 1 0 1 0 | 1 0 1 0
    0 1 1 1 | 1 1 0 1 | 0 1 1 1 | 1 0 1 0
    1 1 0 1 | 1 0 0 0 | 1 1 1 1 | 1 1 1 1
    1 1 1 1 | 1 1 1 1 | 1 1 1 1 | 1 1 1 1
    1 1 1 1 | 1 1 1 1 | 1 0 1 1 | 1 1 0 0
    
    0000 | 0000 | 1010 | 1010 | 0111 | 1101 | 0111 | 1010 |
    0000 | 0000 | 1010 | 1010 | 0111 | 1101 | 0111 | 1001 |
    ---- | ---- | ---- | ---- | ---- | ---- | ---- | --XX |
    
    1101 | 1000 | 1111 | 1111 |
    1101 | 1000 | 1111 | 1111 |
    ---- | ---- | ---- | ---- |
    
    
    1111 | 1111 | 1111 | 1111 | 1111 | 1111 | 1011 | 1100 |
    1111 | 1111 | 1111 | 1111 | 1111 | 1111 | 0100 | 0101 |
    ---- | ---- | ---- | ---- | ---- | ---- | XXXX | X--X |

However, correlation is proving tricky. Nearly everything results in a change of nibbles 7 and 8 of the short packet. Changes in windspeed result in changes in nibble 2 of the short packet.

The changes in nibbles 7 and 8 would suggest some kind of checksum (they change whenever any value changes - humidity, temperature, windspeed - rain is so far untested) but no other value appears to change in the short packet, and the display definitely updates when these packets are received.

Further work is evidently required to decode the transmission...

**Monday evening**

Now have a python script that monitors the serial port for the arduino's output and "decodes" the packets as best we know how at the moment.

I'm really not convinced the decoding is "real" at the moment but I'm basically relying on watching the difference in the bits by eye - for constant conditions, the packets really vary very little, so verifying bit differences for small changes should be possible.

**Monday afternoon**

Written a python script to decode the dumps making the assumptions above - working on 500ms == 0, 1500ms == 1.

Also assuming little-endian for the moment, but can change that later. Need to cross-correlate the dumps with actual data from the weather station next and see if I can reverse-engineer the format.

The dumps appear to be either 159 or 63 transitions (corresponding to 80 or 32 bits) - wondering if it might be a key-frame/delta type deal.

The longer pulses appear to have a common header: (sorry, the binary is backwards...)

    LSB           MSB
     0 0 0 0 0 0 0 0 | 0
     1 0 1 0 1 1 0 1 | 181
     0 0 1 1 1 1 0 1 | 188
     1 0 0 0 0 0 0 1 | 129

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

