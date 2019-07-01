#!/usr/bin/python3

import socket

import smbus
import time

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

channel = 1

address = 0x40

class TempHumSensor(object):
    SI7021_RESET_CMD = 0xFE
    SI7021_ID1_CMD = 0xFA0F
    SI7021_MEASTEMP_NOHOLD_CMD = 0xF3
    SI7021_READPREVTEMP_CMD = 0xE0
    SI7021_MEASRH_NOHOLD_CMD = 0xF5
    TIMEOUT = 0.5

    def __init__(self, channel = 1, address = 0x40):
        self.channel = channel
        self.address = address
        self.bus = smbus.SMBus(self.channel)
        self.reset()

    def reset(self):
        self.bus.write_byte(self.address, self.SI7021_RESET_CMD)
        time.sleep(0.005)

    def _readTemp(self):
        self.bus.write_byte(self.address, self.SI7021_MEASTEMP_NOHOLD_CMD)

    def getTemp(self, fahrenheit = False):
        self._readTemp()
        endtime = time.time() + self.TIMEOUT
        while(time.time() < endtime):
            try:
                result = self.bus.read_i2c_block_data(self.address, self.SI7021_READPREVTEMP_CMD, 3)
                temp = (result[0] << 8) + result[1]
                temperature = ((temp * 175.72)/65536) - 46.85
                if fahrenheit:
                    temperature = (temperature * (9/5)) + 32

                return temperature
            except OSError:
                # Not ready?
                time.sleep(0.05)

    def _readHumid(self):
        self.bus.write_byte(self.address, self.SI7021_MEASRH_NOHOLD_CMD)

    def getHumid(self):
        self._readHumid()
        endtime = time.time() + self.TIMEOUT
        while(time.time() < endtime):
            try:
                result = self.bus.read_i2c_block_data(self.address, self.SI7021_READPREVTEMP_CMD, 3)
                rh = (result[0] << 8) + result[1]
                humidity = ((125 * rh)/65536) - 6
                return humidity
            except OSError:
                # Not ready?
                time.sleep(0.05)


class TempHumidExporter(object):
    def __init__(self):
        self.sensor = TempHumSensor()
        self.hostname = socket.gethostname()

    def collect(self):
        temp_c = self.sensor.getTemp(False)
        rel_humid = self.sensor.getHumid()
        temp_guage = GaugeMetricFamily('temperature', 'Current temperature in celsius', labels=['host',])
        temp_guage.add_metric([self.hostname,], round(temp_c, 2))
        yield temp_guage
        humidity_guage = GaugeMetricFamily('humidity', 'Current realtive humidity', labels=['host',])
        humidity_guage.add_metric([self.hostname,], round(rel_humid, 2))
        yield humidity_guage


if __name__ == "__main__":
    REGISTRY.register(TempHumidExporter())
    start_http_server(8000)
    running = True
    while running:
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            running = False
