# SI7021 Prometheus Exporter

This is a simple Python script that reads the temperature and realitive humidity from an Adafruit SI7021 breakout board and exposes it on port 8000 as Prometheus metrics.

This was my first I2C project, and is a pretty basic port of the Arduino sample code grafted onto the sample code for an exporter in the Prometheus client documentation.

