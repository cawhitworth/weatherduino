#include <SoftwareSerial.h>

SoftwareSerial mySerial(8,9);

#define MAX_DURATIONS 256

unsigned int i = 0;
unsigned int durations[MAX_DURATIONS];

void setup()
{
  mySerial.begin(9600);
  mySerial.print("Hello remote!");
  Serial.begin(9600);
  Serial.print("Hello!");
  attachInterrupt(0, handleInterrupt, CHANGE);
}

boolean inInterrupt = false;

void handleInterrupt()
{
   static unsigned long lastTime;
   static unsigned int duration;

   inInterrupt = true;
   long time = micros();
   duration = time - lastTime;
   durations[i] = duration;
   i++;
   if (i == MAX_DURATIONS) i = 0;
   lastTime = time;   
   inInterrupt = false;
}

int lowOrHigh(int width)
{
  int diffLow = abs(1500 - width);
  int diffHigh = abs(500 - width);
  
  if (diffLow < diffHigh) return LOW;
  
  return HIGH;
}

int nibble(int n, int* bits)
{
  return (bits[    (n * 4)] << 3) + 
         (bits[1 + (n * 4)] << 2) + 
         (bits[2 + (n * 4)] << 1) + 
          bits[3 + (n * 4)];
}

void loop()
{
  delay(5000);
  while (inInterrupt) { delay(100); }
  mySerial.print("TICK\n");
  Serial.print("TICK\n");
  if (i != 0)
  {
    if (i == 160)
    {
      int bits[80];
      mySerial.print("PCKT\n");
      // assume first diff is ~1000
      
      for(int pulse = 1; pulse < 160; pulse += 2)
      {
        int highLow = lowOrHigh(durations[pulse]);
        if (highLow == HIGH)
          bits[pulse / 2] = 1;
        else
          bits[pulse / 2] = 0;        
      }
      
      // Temperature is nibbles 5,6,7
      int encodedTemp = (nibble(5, bits) << 8) + (nibble(6, bits) << 4) + nibble(7, bits);
      int actualTemp = (encodedTemp - 400);

      int humidity = (nibble(8, bits) << 4) + nibble(9, bits);

      mySerial.print("TMP:");
      mySerial.print(actualTemp);
      mySerial.print("\n");
      mySerial.print("HUM:");
      mySerial.print(humidity);
      mySerial.print("\n");
      
      Serial.print(actualTemp);
      Serial.print(" ");
      Serial.print(humidity);
      Serial.print("\n");
      
      mySerial.print("ENDP\n");
    }
    else
    {
      Serial.print(i);
      Serial.print("\n");
    }
  }
  i = 0;
}
