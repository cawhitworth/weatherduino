
#define MAX_DURATIONS 256

unsigned int i = 0;
unsigned int durations[MAX_DURATIONS];

void setup()
{
  Serial.begin(9600);
  Serial.print("Hello!");
  attachInterrupt(0, handleInterrupt, CHANGE);
}

void handleInterrupt()
{
   static unsigned long lastTime;
   static unsigned int duration;
   long time = micros();
   duration = time - lastTime;
   durations[i] = duration;
   i++;
   if (i == MAX_DURATIONS) i = 0;
   lastTime = time;   
}

int state = LOW;

void printDuration(int d)
{
  Serial.print(d);
  Serial.print("  ");
  Serial.print(durations[d]);
  Serial.print("\n");
}

void loop()
{
  delay(5000);
  Serial.print("\nTick");
  for(int j = 0; j < i; j++)
    printDuration(j);
  i = 0;
}
