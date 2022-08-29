# Rapid_BLE_sensor_reading
The aim of this project is to see if it is possible to use BLE advertising data alone to monitor sensor data at high speed. This method does not require pairing between the sensor and the computer and only requires the name of the BLE sensor to be known. In this case, the temperature sensor data in advertisements broadcast from an ESP32 and data were read using Python.

## ESP32 setup
An ESP32 dev board is used to transmit data from a [TMP102](https://www.sparkfun.com/products/13314) sensor. The maximum rate at which the sensor rate can be read is ~8 Hz, below the maximum rate at which the advertisements are transmitted. I didn't have a sensor which could update faster, unfortunately.  The arduino code (BLE_temp_sensor.ino) is based on [BLEcast](https://github.com/ericbarch/BLECast) by Eric Barch. 

The sensor data is embedded in the advertising packet, specifically the manufacturer data, and in surrounded by `X_` so can be parsed more easily. The advertisments are broadcast at 20 Hz (every 50 ms). The maximum speed at which an [ESP32 can broadcast advertisements is 50 Hz](https://www.lucadentella.it/en/2018/03/26/esp32-33-ble-advertising/). It may be able to use a faster rate than the 20 Hz I used, the ESP32 kept crashing/resetting if it was increased. It might be possible by reducing the size of the advertisement packet. 

## Using the BLE transceiver integrated in the computer
The most simple approach is using the BLE hardware integrated in the PC or MacBook Pro. One potential limitation is that the [maximum rate at which advertisements is ~200 ms](https://stackoverflow.com/questions/37307301/ble-scan-interval-windows-10/37328965) in Windows (I can't find MacOS info). 

I used the excellent [Bleak package](https://github.com/hbldh/bleak). FYI, it didn't seem to work on on MacOS 10.4 but worked fine on 10.5. For this method it was necessary to determine the ESP32 address. This can be determined using the `detection_callback.py` script which is found in the Bleak example folder. For PCs the address is the MAC address of the ESP32 which can also be [found directly](https://randomnerdtutorials.com/get-change-esp32-esp8266-mac-address-arduino/) from the ESP32. For the Mac, the address is dynamic so needs to be read from the `detection_callback.py`. The address needs to be changed on line 13:
```
address = (
    "94:B9:7E:DA:7C:FE"
    if platform.system() != "Darwin"
    else "BF14B585-74C7-75D7-D6F2-3D1968FA7764"
)
```

In addition the save location needs to be updated on line 110.

The Bleak package identifies the manufacturer data, which is then decoded and the numbers parsed.
```
stringything = temp_list[0]
data_in_here = stringything.decode('utf-8', 'ignore')
split_data = re.findall('[0-9]+', data_in_here)
```

There are often large numbers of duplicate ardvertisements read so there needs to be a way to ensure duplicates are no counted. I created a deque to which the timestamp from the advertisement data is added, if the timestamp does not match any of the others in the deque, the sensor data is used.



## Adafruit Bluefruit LE Sniffer
This [Bluetooth sniffer dongle](https://www.adafruit.com/product/2269) captures BLE advertisements and cost about $25. This dongle is often used in conjuction with Wireshark to analyse the BLE network traffic. Unfortunately using Wireshark (or tshark or pyshark, the associated command line program and python package,respectively) is not possible for real-time measurements. This is because the driver software includes a memory buffer that prevents realtime output of decoded advertisement data. 

An alternative method is to use the [nRF Sniffer for Bluetooth LE](https://www.nordicsemi.com/Products/Development-tools/nRF-Sniffer-for-Bluetooth-LE) developed by Nordic Semiconductors. This is available via their [downloads page](https://www.nordicsemi.com/Products/Development-tools/nRF-Sniffer-for-Bluetooth-LE/Download?lang=en#infotabs). It includes a python sniffer API which can be used to monitor BLE packets in realtime, and was used for the basis of the `bluetooth_method.py` script. To use this script the USB port to which the Sniffer is attached can be identified using 'My Devices' in Windows or via the terminal in MacOS and running `ls /dev/tty*` command. The correct port can be added to the script on line 34
```
mySniffer = Sniffer.Sniffer(portnum='/dev/cu.usbserial-1410')
```
 ## Texas Instruments CC2540EMK-USB
 This alternative [Sniffer dongle](https://www.ti.com/tool/CC2540EMK-USB) also captures BLE advertisements and cost about $50. There is no ready-to-use software available suitable for real-time analysis packet analysis. There is a [python script](TICCSniffer) from which CC2540_method.py was adapted.
 
 For this dongle to work a USB library had to be installed. For Windows, download and run libusb-win32-devel-filter-1.2.6.0.exe from 
