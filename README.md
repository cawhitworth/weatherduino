#Weatherduino#

I've got a simple wireless weather station (the [Maplin
N25FR](http://www.maplin.co.uk/professional-wireless-weather-centre-220865)
"Professional Weather Station" - it appears to be a generic unit that's also
sold as a bunch of other things; the receiver unit identifies it as a "WH1050")
that transmits on 433MHz. We're having a hack week at work notionally related
to the Internet Of Things, so I've decided to try and reverse engineer it using
an off-the-shelf 433MHz receiver and an Arduino.

## Notes ##

**Monday morning**

Connected up the Arduino to the receiver (5V on the arduino to VCC, GND to GND,
pin 2 [interrupt 0] to a data pin on the receiver).

Tried the [rc_switch](https://code.google.com/p/rc-switch/) library to see if
we could trivially dump any data, but produced no results.

Wired an LED in parallel with the data pin; saw it flashing like crazy. Using a
handheld radio confirmed loads of noise around 433Mhz.

After considerable mucking about, figured out the noise was coming from the USB
power supply for the arduino - running the sketch (with debug LED) powered by
battery gave a much cleaner output.

However, rc_switch is still not giving us anything useful.

Dumping the pulse-duration data (using the dump_433 sketch - assumes a 433MHz
receiver on interrupt 0) shows the weather station appears to be transmitting
PWM encoded data (see dump.dat). The interrupt is triggered on every
transition, and every other value is ~1000us, with ~500us and ~1500us pulses
presumably encoding the data:

![](https://dl.dropboxusercontent.com/u/18971919/waveduino/pulses.png)

The next step is to decode this and try and correspond it to the data I see on
the weather station base unit:

![](https://dl.dropboxusercontent.com/u/18971919/waveduino/base_unit_and_arduino.jpg)

**Monday afternoon**

Written a python script to decode the dumps making the assumptions above -
working on 500us == 0, 1500us == 1.

Also assuming little-endian for the moment, but can change that later. Need to
cross-correlate the dumps with actual data from the weather station next and
see if I can reverse-engineer the format.

The dumps appear to be either 159 or 63 transitions (corresponding to 80 or 32
bits) - wondering if it might be a key-frame/delta type deal.

The longer pulses appear to have a common header: (sorry, the binary is
backwards...)

    LSB           MSB
     0 0 0 0 0 0 0 0 | 0
     1 0 1 0 1 1 0 1 | 181
     0 0 1 1 1 1 0 1 | 188
     1 0 0 0 0 0 0 1 | 129

**Monday evening**

Now have a python script that monitors the serial port for the arduino's output
and "decodes" the packets as best we know how at the moment.

I'm really not convinced the decoding is "real" at the moment but I'm basically
relying on watching the difference in the bits by eye - for constant
conditions, the packets really vary very little, so verifying bit differences
for small changes should be possible.

**Tuesday morning**

Diffing between packets of data added, along with various readability
improvements for the serial logger.

We appear to see either 80-bit or 32-bit bursts of data from the transmitter,
so the serial logger recognises these. Additionally, the 32-bit bursts appear
to be identical to the last 32-bits of the 80-bit bursts.

The serial logger now diffs the packets it receives - the first 48-bits of a
long packet get compared to the first 48-bits of the previous long packet;
short packets or the last 32-bits of a long packet get compared to the last
short packet or last 32-bits of a long packet received.

At the same time, a webcam is now pointed at the base station and captures an
image every time the serial logger registers a snapshot:

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

However, correlation is proving tricky. Nearly everything results in a change
of nibbles 7 and 8 of the short packet. Changes in windspeed result in changes
in nibble 2 of the short packet.

The changes in nibbles 7 and 8 would suggest some kind of checksum (they change
whenever any value changes - humidity, temperature, windspeed - rain is so far
untested) but no other value appears to change in the short packet, and the
display definitely updates when these packets are received.

Further work is evidently required to decode the transmission...

**Tuesday afternoon**

Trying various types of data analysis. It's confusing. For example, a change of
humidity from 41% to 42% (and no change in anything else) causes the final two
nibbles to change thus:

    1001 1110   Before
    1101 1010   After
    -X-- -X--   Changed bits

However, a change of temperature from 24.2C to 24.3C (and no change in anything
else) causes the final two nibbles to change thus:

    1001 1110   Before
    1100 1001   After
    -X-X -XXX   Changed bits

Which is - bit 2 of each word changes when either the humidity or the
temperature changes, but there are no changes in the data for humidity that
aren't also in the changes for the temperature.

I've now written a script which determines which bits in the data change over
time. For steady wind/rain, the pattern appears to be:

    Long diffs:
    - - - -   - - - -   - - - -   - - - -
    - - - -   - - - -   X X X X   X X X X
    - - - -   X X X X   - - - -   - - - -
    - - - -   - - - -   - - - -   - - - -
    - - - -   - - - -   X X X X   X X X X
    Short diffs:
    - - - -   - - - -   - - - -   - - - -
    - - - -   - - - -   X X X X   X X X X

**Tuesday afternoon - Interlude**

[David Dunn](http://twitter.com/dcdunn) from [Electric
Imp](http://electricimp.com) dropped by Red Gate to give a quick demonstration
of their Internet of Things platform and leave a couple of devkits behind - the
intention is to get the arduino uploading data to the cloud using this if I can
ever decode the data format.

**Tuesday end-of-day**

A bit frustrated; I'm failing to see any clear pattern in the logs/captures
I've got. Probably best put it to bed for now and try again tomorrow.

**Wednesday**

No real progress; interview in morning and other work took up the afternoon.

Plan of attack for tomorrow - try and get inside the sensors and see if any of
the parts have useful looking datasheets anywhere.

**Thursday morning**

It's amazing what a day off and a bit of googling will do.

So, I took various things apart and didn't get very far, unsurprisingly. Then I
went back to staring at the bitstreams - I've had a niggling feeling for the
past couple of days that the short packets might be a red herring, so I went
back to the logs and webcam grabs of the receiver I had, and tried correlating
the two. Suddenly, it all becomes clear.

When temperatures change, I observe changes in nibbles 6 and 7 of the long
packet as well as changes in the the final two nibbles. The changes in nibbles
6 and 7 seem to be changes by 1 when the temperature changes by 0.1C. *AHA!*

So my theory is now:

 * The last two nibbles are a checksum
 * The short packets are a red herring

Googling around, I found [this
page](http://www.susa.net/wordpress/2012/08/raspberry-pi-reading-wh1081-weather-sensors-using-an-rfm01-and-rfm12b/)
where someone else has had some success reverse engineering a (different)
Maplin weather station and has come to very similar conclusions to me. Their
conclusion is that the temperature is 3 nibbles, and to get the temperature,
you subtract 400 (0x190) and divide by ten. Well, does that work?

I've got a log with:

    1101 0111 1100

for nibbles 5, 6 and 7 (assuming the LSN is the last of the three) and a
screenshot showing 24.3C. Given the conversion above, this gives us a
temperature of... 305.2C. That's not right.

Wait. I've previously made assumptions about the mapping of short/long pulses
to 1s and 0s. Maybe I got that wrong?

    0010 1000 0011

...which is 0x283, which is 643. (643 - 400) / 10 = **24.3C**

Woop! Got it. Right, now to do something useful with this knowledge...

**Thursday lunchtime**

OK, so my intention was to use the Electric Imp that Dave dropped off on
tuesday to get this data onto the internet - basically, implement a simple
serial protocol between the Arduino and the Imp, and have the Imp push data
up to the cloud when it receives a message from the Arduino.

Unfortunately, the Imp is 3.3v and the Arduino is 5v and I lack a suitable
level shifter (or the components to build one) so that idea will have to go
on hold for the moment.

Meanwhile, I've written a more special-purpose Arduino sketch that receives
data from the weather station, decodes it and writes the temperature and
humidity data to the serial port.

In the absence of being able to use the Imp for anything, I now need to
decide what to do next - I have an SD card board, so I could use that to
log data when not connected to a serial console...

**Thursday mid-afternoon**

So, it turns out a trivial voltage divider is enough to get the Arduino
talking to the Imp - the Arduino is happy enough with the 3.3V level the
Imp puts out in the other direction also.

This means I've now got the world's most convoluted serial console hooked up
to my Arduino - using the software serial connected via the voltage divider
to pins 5 and 7 on the Imp (which are hardwired to the Imp's UART) and a
simple serial monitor running on the Imp, I can see the output from my
weather station Arduino sketch on the Imp debug console:

![](https://dl.dropboxusercontent.com/u/18971919/waveduino/impDemo1.png)

Which is pretty neat. Next, decode that data and make it available via a web
service.

(annoyingly, I can't seem to get things to work unless the Arduino has both a
USB *and* 9V battery attached, and the Imp doesn't want to run off a USB power
supply either, so currently it's taking 2 USB ports and a 9V battery to make
it work, and it currently looks like this:

![](https://dl.dropboxusercontent.com/u/18971919/waveduino/IMG_20131031_143723.jpg)

Which is a bit of a mess, but hey ho)

**Thursday late afternoon**

The perennial problem of noise has arisen again - it turns out that connecting
the USB-powered Imp does actually generate a substantial amount of noise in
the 433MHz circuit, meaning that getting clean, useful data from the receiver
becomes very difficult as soon as it is connected. A clean packet does get
through very occasionally, and when it does, the data wends its way through
the cloudyweb and I have a nice little Imp application that allows you to
retrieve the current temperature and humidity from an HTTP request. Sadly,
it only seems to get a useful packet about once every half hour, and the
rest of the time there's just too much noise.

**Thursday afternoon a bit later still...**

It seems if I continually poll the Imp UART (using imp.onidle rather than
imp.wakeup) the noise virtually goes away. This is far from ideal in a low-
power device, but it will do for now.

**Friday morning**

The setup seems to be reasonably stable if not terribly power efficient as
it is. I tried hooking the Imp directly up to the Arduino UART rather than
using the SoftwareSerial on pins 8/9, but it kind of collapsed in a heap when
I did that.

So, the final setup is:

    Arduino  : Both USB and 9V cell power connected

    XD-RF-5V : VCC -> Arduino 5V
               GND -> Arduino GND
               Data -> Arduino 2 (interrupt 0)

               (debug LED connected in parallel to data pin with 560ohm
                resister, connected to GND)

    Imp      : Pin 7 (RX) -> Arduino pin 9 via voltage divider (R1 = 560ohm
               R2 = 1K, grounded to Imp GND)
               Pin 5 (TX) -> Arduino pin 8 (direct connection)
               Power from USB

The Arduino software is in the [weatherduino
folder](https://github.com/cawhitworth/weatherduino/tree/master/weatherduino)
and the Imp scripts are in the [impScripts
folder](https://github.com/cawhitworth/weatherduino/tree/master/impScripts).


(I wonder if this is because I am using quite an old Imp dev board?)

Anyway, I have temperature and humidity data in the cloud, which is nice.

**Friday lunchtime**

I have a web service in Python now: the Imp agent POSTs form data to it:

    /submit
    temperature=<float>
    humidity=<int>

The service stores data in a SQLite database (called, at the moment,
temperature.db). It can be queried on two other GET endpoints:

    /last?<int>    - retrieve the last <int> humidity and temperature records
    /today         - retrieve all the humidity and temperature records for today

Both return data in JSON format.

There is also a /graph endpoint. This returns an HTML document that uses
[D3](http://d3js.org) to draw a graph of humidity and temperature data for
the current day.

![](https://dl.dropboxusercontent.com/u/18971919/waveduino/graph.png)

(the URL the agent posts to is hardcoded. The committed version is not where
my webservice really lives)

