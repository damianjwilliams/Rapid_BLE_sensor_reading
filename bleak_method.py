import time
import csv
import asyncio
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from bleak import BleakScanner
from qasync import QEventLoop
from collections import deque
import platform
import re

# BLE peripheral ID
address = (
    "94:B9:7E:DA:7C:FE"
    if platform.system() != "Darwin"
    else "BF14B585-74C7-75D7-D6F2-3D1968FA7764"
)
length_window = 100

class Window(pg.GraphicsLayoutWidget):
    def __init__(self, loop=None, parent=None):
        super().__init__(parent)
        self._loop = loop
        self.setWindowTitle("pyqtgraph example: Scrolling Plots")
        self.plot1 = self.addPlot()
        self.plot1.setYRange(20, 30, padding=0)
        self.plot1.setLabel(axis='left', text='Temperature (C)')
        self.plot1.setLabel(axis='bottom', text='Point number')
        self.plot1.hideAxis('bottom')
        self._temp_data = deque([0] * length_window)
        self._curve1 = self.plot1.plot(self.temp_data, pen='r')

        self._save_data = []

        self._previous_readings = deque([0] * 25)
        self.current_name = ""
        self.counter = 0
        self._client = BleakScanner(loop=self._loop)

    @property
    def client(self):
        return self._client

    async def start(self):
        await self.client.start()
        self.start_read()

    @property
    def temp_data(self):
        return self._temp_data

    @property
    def previous_readings(self):
        return self._previous_readings

    @property
    def curve1(self):
        return self._curve1

    @property
    def save_data(self):
        return self._save_data

    async def read(self):
        self.client.register_detection_callback(self.detection_callback)

    def detection_callback(self, device, advertisement_data):
        if device.address == address:
            stage1 = advertisement_data.manufacturer_data
            temp_list = list(stage1.values())

            try:
                stringything = temp_list[0]
                data_in_here = stringything.decode('utf-8', 'ignore')
                split_data = re.findall('[0-9]+', data_in_here)
                temperature_reading = float(split_data[0]) / 100
                reading_id = float(split_data[1])
                print(reading_id)
                date_time = time.time_ns() // 1000000
                current_reading_id = reading_id

                if current_reading_id not in self.previous_readings:
                    print(self.previous_readings)
                    self.update_plot1(temperature_reading, current_reading_id)

            except Exception as e:
                print(e)

            self.previous_readings.append(current_reading_id)
            self.previous_readings.popleft()

    def start_read(self):
        asyncio.ensure_future(self.read(), loop=self._loop)

    def update_plot1(self, temperature_reading, current_reading_id):
        self.temp_data.append(temperature_reading)
        self.temp_data.popleft()
        self.curve1.setData(self.temp_data)
        self.plot1.setTitle("Temp: " + str(temperature_reading) + " C")
        date_time = time.time_ns() // 1000000
        self.counter += 1
        print(self.counter)
        self.save_data.append(self.counter)
        self.save_data.append(date_time)
        self.save_data.append(current_reading_id)
        self.log_data()
        self.save_data.clear()

    def log_data(self):
        with open("/Users/damianwilliams/Desktop/bleak_method2.txt", "a") as f:
            # with open("C:/Users/Damian/Desktop/bleak_method2.txt", "a") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(self.save_data)


def main(args):
    app = QtGui.QApplication(args)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = Window()
    window.show()

    with loop:
        asyncio.ensure_future(window.start(), loop=loop)
        loop.run_forever()


if __name__ == "__main__":
    import sys
    main(sys.argv)
