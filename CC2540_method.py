# https://github.com/andrewdodd/ccsniffpiper/blob/master/ccsniffpiper.py
# https://github.com/christianpanton/ccsniffer/blob/master/ccsniffer.py

import errno
import binascii
import time
import usb.core
import usb.util
import re
import csv
import pyqtgraph as pg
from collections import deque

TIMEOUT = 500
DEFAULT_CHANNEL = 0x0b  # 11
DATA_EP_CC2531 = 0x83
DATA_EP_CC2530 = 0x82
DATA_EP_CC2540 = 0x83
DATA_TIMEOUT = 200
GET_IDENT = 0xC0
SET_POWER = 0xC5
GET_POWER = 0xC6
SET_START = 0xD0
SET_END = 0xD1
SET_CHAN = 0xD2
DIR_OUT = 0x40
DIR_IN = 0xc0
POWER_RETRIES = 10

dev = None
name = ""
ctr = 0

win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle('pyqtgraph example: Scrolling Plots')
p2 = win.addPlot()
p2.setYRange(20, 30, padding=0)
temp_data = deque([0] * 100)
curve2 = p2.plot(temp_data)
p2.setLabel(axis='left', text='Temperature (C)')
p2.setLabel(axis='bottom', text='Point number')
p2.hideAxis('bottom')
ptr1 = 0

def init():
    global dev
    global name

    try:
        print('try CC2531')
        dev = usb.core.find(idVendor=0x0451, idProduct=0x16ae)

        if dev is None:
            print('did not find a CC2531')

    except usb.core.USBError:
        raise OSError("Permission denied, you need to add an udev rule for this device", errno=errno.EACCES)

    if dev is None:
        try:
            print('try CC2530')
            dev = usb.core.find(idVendor=0x11a0, idProduct=0xeb20)

            if dev is None:
                print('did not find a CC2530')

        except usb.core.USBError:
            raise OSError("Permission denied, you need to add an udev rule for this device", errno=errno.EACCES)

    if dev is None:
        try:
            print('try CC2540')
            dev = usb.core.find(idVendor=0x0451, idProduct=0x16b3)

            if dev is None:
                print('did not find a CC2540')

        except usb.core.USBError:
            raise OSError("Permission denied, you need to add an udev rule for this device", errno=errno.EACCES)

    if dev is None:
        print('Device not found')
        return

    dev.set_configuration()  # must call this to establish the USB's "Config"
    # name = usb.util.get_string(dev, 256, 2) # get name from USB descriptor
    # get name from USB descriptor
    name = usb.util.get_string(dev, dev.iProduct)
    print('name')
    print(name)
    # get identity from Firmware command
    ident = dev.ctrl_transfer(DIR_IN, GET_IDENT, 0, 0, 256)  # get identity from Firmware command
    print('ident')
    print(ident)
    # power on radio, wIndex = 4
    dev.ctrl_transfer(DIR_OUT, SET_POWER, wIndex=4)
    print('powering up')

    while True:
        # check if powered up
        power_status = dev.ctrl_transfer(DIR_IN, GET_POWER, 0, 0, 1)

        if power_status[0] == 4: break

        time.sleep(0.1)

    print('powered up')
    channel = 37
    print('set channel')  # bt channel
    # channels 37,38,39 are the advertisement channels for BTLE
    # channels 11-16 are channels for ZigBee 2.4
    set_channel(channel)
    print('post channel')

def set_channel(channel):
    global dev
    print('set channel')
    dev.ctrl_transfer(DIR_OUT, SET_CHAN, 0, 0, [channel])
    dev.ctrl_transfer(DIR_OUT, SET_CHAN, 0, 1, [0x00])
    print('done setting channel')

def read_data():
    global dev
    print('start sniffing')
    dev.ctrl_transfer(DIR_OUT, SET_START)

    while True:
        try:#time.sleep(1)
        #print('get data')
            ret = dev.read(DATA_EP_CC2540, 4096, DATA_TIMEOUT)
            #print('got data')
            #print(ret)

            for x in ret:
                if x >= 0x20 and x <= 0x7D:
                    #print
                    chr(x),
            #print
            if len(ret) > 10:
                parse_cc2531_packet(ret)

        except:
            print("read timeout")

current_name = ""

def parse_cc2531_packet(packet):
    global ctr
    global current_name
    global ptr1
    # from https://github.com/christianpanton/ccsniffer/blob/master/ccsniffer.py
    packetlen = packet[1]

    if len(packet) - 3 != packetlen:
        return None

    # unknown header produced by the radio chip
    header = packet[3:7].tobytes()
    # the data in the payload
    payload = packet[8:-2].tobytes()
    # length of the payload
    payloadlen = packet[7] - 2  # without fcs

    if len(payload) != payloadlen:
        return None

    # current time
    timestamp = time.gmtime()
    # used to derive other values
    fcs1, fcs2 = packet[-2:]
    # rssi is the signed value at fcs1
    rssi = (fcs1 + 2 ** 7) % 2 ** 8 - 2 ** 7 - 73
    # crc ok is the 7th bit in fcs2
    crc_ok = fcs2 & (1 << 7) > 0
    # correlation value is the unsigned 0th-6th bit in fcs2
    corr = fcs2 & 0x7f
    # print("Channel:     %d" % self.channel)
    # print("Timestamp:   %s" % time.strftime("%H:%M:%S", timestamp))
    # print("Header:      %s" % binascii.hexlify(header))
    #
    # bytes_object = bytes.fromhex(str(header))
    # ascii_string = bytes_object.decode("ASCII")
    # print(ascii_string)
    # print("RSSI:        %d" % rssi)
    # print("CRC OK:      %s" % crc_ok)
    # print("Correlation: %d" % corr)
    payload_decode = binascii.hexlify(payload)
    payload_decode_no_b = payload_decode.decode()
    start_time = time.process_time()


    if("fe7c" in payload_decode_no_b):
        new_name = payload_decode_no_b
        print(payload_decode_no_b)

        if (new_name not in current_name):
            date_time = time.time_ns() // 1000000

            try:
                ha = re.search(r'785f(.*?)5f78', payload_decode_no_b).group(1)
                hadecode = bytearray.fromhex(ha).decode()
                hadecode_split = hadecode.split("-")
                measurement = (float(hadecode_split[0]))/100
                ESP32_time = float(hadecode_split[1])
                print(ptr1)
                print(measurement)
                with open("/Users/damianwilliams/Desktop/CC2540_method_mac.txt", "a") as f:
                #with open("C:/Users/Damian/Desktop/fast_advertising/CC2540_method_PC.txt", "a") as f:

                    writer = csv.writer(f, delimiter="\t")
                    writer.writerow([ptr1,date_time, ESP32_time])

                temp_data.append(measurement)
                temp_data.popleft()
                ptr1 += 1
                curve2.setData(temp_data)
                p2.setTitle("Temp: " + str(measurement) + " C")
                curve2.setPos(ptr1, 0)
                pg.QtWidgets.QApplication.processEvents()

            except:
                "Unable to parse"

        current_name = new_name
        ctr = ctr + 1

if __name__ == "__main__":
    init()
    read_data()
    pg.exec()

