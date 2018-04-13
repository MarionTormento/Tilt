#include <CapacitiveSensor.h>

/* Analog Read to PC
   ------------------
*/
int capPinE = 10;
int capPinSL = 8;
int capPinSR = 9;

CapacitiveSensor   cs_Left = CapacitiveSensor(capPinE, capPinSL);     // 10M resistor between pins 8 & 10, pin 8 is sensor pin, add a wire and or foil if desired
CapacitiveSensor   cs_Right = CapacitiveSensor(capPinE, capPinSR);     // 10M resistor between pins 9 & 10, pin 9 is sensor pin, add a wire and or foil

int potPin = 5;    // select the input pin for the potentiometer
int pot_val = 0;       // variable to store the value coming from the sensor
float gear_ratio = 1;
float angle_mean = 1800;
float ohms_per_turn = 1723;
float Vin = 5;
float R = 10000;
float angle = 1;
float correction = 3600/2089.38;
volatile int right_hand = 0;
volatile int left_hand = 0;
int threshR = 50;
int threshL = 50;
long totalLeft;
long totalRight;


void setup()
{
  cs_Left.set_CS_AutocaL_Millis(0xFFFFFFFF);  
  cs_Right.set_CS_AutocaL_Millis(0xFFFFFFFF);
  Serial.begin(9600);
}

void loop()
{
  totalLeft =  cs_Left.capacitiveSensor(30); 
  totalRight =  cs_Right.capacitiveSensor(30);
  angle = readAngle();

  if ((totalLeft > threshR) && (totalRight> threshR))
  {
    right_hand = 1;
    left_hand = 1;
  }
    else if((totalLeft > threshR) && (totalRight <= threshR))
    {
      right_hand = 0;
      left_hand = 1;
    }
    else if((totalLeft <= threshR) && (totalRight > threshR))
    {
      right_hand = 1;
      left_hand = 0;
    }
  else
  {
    right_hand =0;
    left_hand = 0;
  }

  Serial.print(angle);
  Serial.print("<");
 Serial.print(right_hand);
  Serial.print("<");
  Serial.println(left_hand);
  Serial.flush() ;
  delay(20);
}

float readAngle()
{
  pot_val = analogRead(potPin);
  angle = (pot_val * R * 360 * 5) / (1023 * Vin * ohms_per_turn) * correction - angle_mean;
  return angle;
}

