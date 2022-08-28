# Rapid_BLE_sensor_reading
The aim of this project is to see if it is possible to use BLE advertising data alone to monitor sensor data at high speed. This method does not require pairing between the sensor and the computer and only requires the name of the BLE sensor to be known. In this case, the temperature sensor data in advertisements broadcast from an ESP32 and data were read using Python.

## ESP32 setup
An ESP32 dev board is used to transmit data from a [TMP102](https://www.sparkfun.com/products/13314) sensor. The maximum rate at which the sensor rate can be read is ~8 Hz, below the maximum rate at which the advertisements are transmitted. I didn't have a sensor which could update faster, unfortunately.  The arduino code (BLE_temp_sensor.ino) is based on [BLEcast](https://github.com/ericbarch/BLECast) by Eric Barch. 

The sensor data is embedded in the advertising packet, and in surrounded by `X_` so can be parsed more easily. The advertisments are broadcast at 20 Hz (every 50 ms). The maximum speed at which an [ESP32 can broadcast advertisements is 50 Hz](https://www.lucadentella.it/en/2018/03/26/esp32-33-ble-advertising/). It may be able to use a faster rate than the 20 Hz I used, the ESP32 kept crashing/resetting if it was increased. It might be possible by reducing the size of the advertisement packet. 

## Using the BLE transceiver integrated in the computer
The most simple approach is using the BLE hardware integrated in the PC or MacBook Pro. One potential limitation is that the [maximum rate at which advertisements is ~200 ms](https://stackoverflow.com/questions/37307301/ble-scan-interval-windows-10/37328965) in Windows (I can't find MacOS info). 

I used the excellent [Bleak package](https://github.com/hbldh/bleak). FYI, it didn't seem to work on on MacOS 10.4 but worked fine on 10.5. For this method it was necessary to determine the ESP32 address. This can be determined using the `detection_callback.py` script which is found in the Bleak example folder. For PCs the address is the MAC address of the ESP32 which can also be [found directly](https://randomnerdtutorials.com/get-change-esp32-esp8266-mac-address-arduino/) from the ESP32. For the Mac, the address is dynamic so needs to be read from the `detection_callback.py`
