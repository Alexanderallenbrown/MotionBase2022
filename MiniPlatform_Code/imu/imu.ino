#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
  
Adafruit_BNO055 bno = Adafruit_BNO055(55);

void setup(void) 
{
  Serial.begin(115200);
  Serial.println("Orientation Sensor Test"); Serial.println("");
  
  /* Initialise the sensor */
  if(!bno.begin())
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }
  
  delay(1000);
    
  bno.setExtCrystalUse(true);
}

void loop(void) 
{
  
  
  /* Get a new sensor event */ 
// Possible vector values can be:
  // - VECTOR_ACCELEROMETER - m/s^2
  // - VECTOR_MAGNETOMETER  - uT
  // - VECTOR_GYROSCOPE     - rad/s
  // - VECTOR_EULER         - degrees
  // - VECTOR_LINEARACCEL   - m/s^2
  // - VECTOR_GRAVITY       - m/s^2
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
  imu::Vector<3> positionData = bno.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);  
  /* Display the floating point data */
  //Serial.print("X accel: ");
  Serial.print(euler.x());
  Serial.print("\t");
  //Serial.print(" Y accel: ");
  Serial.print(euler.y());
  Serial.print("\t");
  //Serial.print(" Z accel: ");
  Serial.print(euler.z());
  Serial.print("\t");
  //Serial.print("X rad/s: ");
  Serial.print(positionData.x());
  Serial.print("\t");
  //Serial.print(" Y rad/s: ");
  Serial.print(positionData.y());
  Serial.print("\t");
  //Serial.print(" Z rad/s: ");
  Serial.print(positionData.z());
  Serial.print("\t");
  Serial.print(millis()/1000.0);
  Serial.println("");
  delay(10);
}
