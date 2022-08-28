#include <BLECast.h>
#include <Wire.h> // Used to establied serial communication on the I2C bus
#include <SparkFunTMP102.h> // Used to send and recieve specific information from our sensor

TMP102 sensor0;

char output[18];
int n;
int m;
float esp32_timer;
float temperature;

// define BTLE name
BLECast bleCast("ESP32BLE");

void setup() {
  Serial.begin(115200);
  Wire.begin(16,17);

  if(!sensor0.begin())
    {
      Serial.println("Cannot connect to TMP102.");
      Serial.println("Is the board connected? Is the device ID correct?");
      while(1);
    }

  // set the Conversion Rate (how quickly the sensor gets a new reading)
  //0-3: 0:0.25Hz, 1:1Hz, 2:4Hz, 3:8Hz
  sensor0.setConversionRate(3);
  sensor0.wakeup();
  bleCast.begin();

} 

void loop() { 
  //Time stamp  
  esp32_timer = millis();
  temperature = sensor0.readTempC();
  int temp_int = int(temperature*100);
  int esp32_timer_int = int(esp32_timer);
  
  Serial.println(esp32_timer_int);
  sprintf(output, "x_%i-%i_x",temp_int,esp32_timer_int);
  
  bleCast.setManufacturerData(output, sizeof(output));

  Serial.println(output);
  delay(50);  
}
