
#define MAX_DURATIONS 256

unsigned int i = 0;
unsigned int durations[MAX_DURATIONS];

void setup()
{
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

int state = LOW;

void printDuration(int d)
{
  Serial.print("\n");
  Serial.print(d);
  Serial.print("  ");
  Serial.print(durations[d]);
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
  Serial.print("TICK\n");
  if (i != 0)
  {
    if (i == 160)
    {
      int bits[80];
      Serial.print("PCKT\n");
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

      Serial.print("TMP:");
      Serial.print(actualTemp);
      Serial.print("\n");
      Serial.print("HUM:");
      Serial.print(humidity);
      Serial.print("\n");
      
      Serial.print("ENDP\n");
    }
  }
  i = 0;
}
