import time
from SnifferAPI import Sniffer, UART
import binascii
import re
import csv
from _collections import deque
import pyqtgraph as pg

nPackets = 0
mySniffer = None
count = 0
previous_readings = deque([0] * 5)

win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle('pyqtgraph example: Scrolling Plots')
p2 = win.addPlot()
p2.setYRange(20, 30, padding=0)
p2.setLabel(axis='left', text='Temperature (C)')
p2.setLabel(axis='bottom', text='Point number')
p2.hideAxis('bottom')
temp_data = deque([0] * 100)
curve2 = p2.plot(temp_data)
ptr1 = 0


def setup():
    global mySniffer
    # Find connected sniffers
    ports = UART.find_sniffer()

    if len(ports) > 0:
        # Initialize the sniffer on the first COM port found with baudrate 1000000.
        # If you are using an old firmware version <= 2.0.0, simply remove the baudrate parameter here.
        mySniffer = Sniffer.Sniffer(portnum='/dev/cu.usbserial-1410')
        #mySniffer = Sniffer.Sniffer(portnum='COM14')
    else:
        print("No sniffers found!")
        return

    # Start the sniffer module. This call is mandatory.
    mySniffer.start()
    # Scan for new advertisers
    mySniffer.scan()
    # Wait to allow the sniffer to discover device mySniffer.
    time.sleep(5)
    # Retrieve list of discovered devicemySniffer.
    d = mySniffer.getDevices()
    # Find device with name "Example".
    dev = d.find('Example')

    if dev is not None:
        # Follow (sniff) device "Example". This call sends a REQ_FOLLOW command over UART.
        mySniffer.follow(dev)
    else:
        print("Could not find device")

def loop():
    # Enter main loop
    while True:
        time.sleep(0.01)
        packets = mySniffer.getPackets()
        processPackets(packets)

# Takes list of packets
def processPackets(packets):
    global ptr1, temp_data,count

    for packet in packets:
        global nPackets

        if packet.OK:
            address = binascii.hexlify(bytearray(packet.blePacket.payload[0:6]))

            if ("fe7c" in str(address)):
                payload_string = str(bytes(packet.blePacket.payload), 'cp437')
                #print(payload_string)
                ESP32_data = re.search(r'x_(.*?)_x', payload_string).group(1)
                #print(ESP32_data)
                ESP32_data_split = ESP32_data.split("-")
                temperature = (float(ESP32_data_split[0])) / 100
                #print(temperature)
                ESP32_time = float(ESP32_data_split[1])
                print(ESP32_time)
                date_time = time.time_ns() // 1000000
                current_reading_id = ESP32_time

                if (current_reading_id not in previous_readings):
                    temp_data.append(temperature)
                    temp_data.popleft()
                    curve2.setData(temp_data)
                    curve2.setPos(ptr1, 0)
                    p2.setTitle("Temp: " + str(temperature) + " C")
                    pg.QtWidgets.QApplication.processEvents()
                    print("************")
                    print(ptr1)
                    ptr1 += 1

                    with open("/Users/damianwilliams/Desktop/bluefruit_method_mac.txt", "a") as f:
                    #with open("C:/Users/Damian/Desktop/fast_advertising/bluefruit_method_PC.txt", "a") as f:
                        writer = csv.writer(f, delimiter="\t")
                        writer.writerow([ptr1, date_time, ESP32_time])

                previous_readings.append(current_reading_id)
                previous_readings.popleft()

setup()

if mySniffer is not None:
    loop()

