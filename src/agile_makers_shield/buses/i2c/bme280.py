
############################################################################
# Copyright (c) 2016, 2017 Libelium Comunicaciones Distribuidas S.L.       #
#                                                                          #
# All rights reserved. This program and the accompanying materials         #
# are made available under the terms of the Eclipse Public License v1.0    #
# and Eclipse Distribution License v1.0 which accompany this distribution. #
#                                                                          #
# The Eclipse Public License is available at                               #
#    http://www.eclipse.org/legal/epl-v10.html                             #
# and the Eclipse Distribution License is available at                     #
#   http://www.eclipse.org/org/documents/edl-v10.php.                      #
#                                                                          #
# Contributors:                                                            #
#    David Palomares - Initial API and implementation                      #
############################################################################

#########################################################
#                  AGILE I2C BME280                     #
#                                                       #
#    Description: Class to communicate with the BME280  #
#       in the AGILE Maker's Shield. This allows to     #
#       read the temperature, humidity and pressure     #
#       from the sensor.                                #
#    Author: David Palomares <d.palomares@libelium.com> #
#    Version: 0.1                                       #
#    Date: March 2017                                   #
#########################################################

# --- Imports -----------
from agile_makers_shield.buses.i2c import i2c_bus
import time
# -----------------------


# --- Variables ---------
# BME280
BME280_ADDRESS = 0x77
BME280_CHECK_BYTE = 0x60
DUMMY_DATA = [0x00]
# Oversampling constants
BME280_OVERSAMP_SKIPPED = 0x00
BME280_OVERSAMP_1X = 0x01
BME280_OVERSAMP_2X = 0x02
BME280_OVERSAMP_4X = 0x03
BME280_OVERSAMP_8X = 0x04
BME280_OVERSAMP_16X = 0x05
# I2C Addresses
BME280_REG_DIG_T1 = 0x88 # 2 bytes LE
BME280_REG_DIG_T2 = 0x8A # 2 bytes LE signed
BME280_REG_DIG_T3 = 0x8C # 2 bytes LE signed
BME280_REG_DIG_P1 = 0x8E # 2 bytes LE
BME280_REG_DIG_P2 = 0x90 # 2 bytes LE signed
BME280_REG_DIG_P3 = 0x92 # 2 bytes LE signed
BME280_REG_DIG_P4 = 0x94 # 2 bytes LE signed
BME280_REG_DIG_P5 = 0x96 # 2 bytes LE signed
BME280_REG_DIG_P6 = 0x98 # 2 bytes LE signed
BME280_REG_DIG_P7 = 0x9A # 2 bytes LE signed
BME280_REG_DIG_P8 = 0x9C # 2 bytes LE signed
BME280_REG_DIG_P9 = 0x9E # 2 bytes LE signed
BME280_REG_DIG_H1 = 0xA1
BME280_REG_DIG_H2 = 0xE1 # 2 bytes LE signed
BME280_REG_DIG_H3 = 0xE3
BME280_REG_DIG_H4 = 0xE4 # 2 bytes BE
BME280_REG_DIG_H5 = 0xE5 # 2 bytes LE
BME280_REG_DIG_H6 = 0xE7 # 1 byte signed
BME280_REG_CHIP_ID = 0xD0 # Chip ID
BME280_REG_VER = 0xD1 # Version
BME280_REG_RST = 0xE0 # Softreset
BME280_REG_CTRL_HUMIDITY = 0xF2 # Control Humidity
BME280_REG_STAT = 0xF3 # Status
BME280_REG_CTRL_MEAS = 0xF4 # Control Measure
BME280_REG_CONFIG = 0xF5 # Configuration
BME280_REG_PRESSURE = 0xF7 # 2 bytes
BME280_REG_TEMPERATURE = 0xFA # 2 bytes
BME280_REG_HUMIDITY = 0xFD # 2 bytes
# -----------------------


# --- Classes -----------
class BME280():
   """Class that implements methods to read from
   and write to the BME280 via I2C."""


   def __init__(self):
      self._bus = i2c_bus.I2C_Bus(BME280_ADDRESS)
      if not self._check:
         raise IOError("Could not connect to the I2C Bus")
      self._readCalibration()
      self._t_fine = 0


   def close(self):
      self._bus.close()


   def _check(self):
      """Checks if the I2C bus is working."""
      reg = BME280_REG_CHIP_ID
      try:
         if self._bus.read(reg, 1)[0] == BME280_CHECK_BYTE:
            return True
      except:
         return False
      return False


   def _utosint8(self, uint8):
      """Converts and unsigned 8-bit number to a signed 8-bit number."""
      sint8 = ((uint8 + 128) % 256) - 128
      return sint8


   def _utosint16(self, uint16):
      """Converts and unsigned 16-bit number to a signed 16-bit number."""
      sint16 = ((uint16 + 32768) % 65536) - 32768
      return sint16


   def _readCalibration(self):
      """Reads the calibration values stored in the BME280."""
      # Temperature
      dig_T1 = self._bus.read(BME280_REG_DIG_T1, 2)
      dig_T2 = self._bus.read(BME280_REG_DIG_T2, 2)
      dig_T3 = self._bus.read(BME280_REG_DIG_T3, 2)
      self._dig_T1 = (dig_T1[1] << 8) | dig_T1[0]
      self._dig_T2 = self._utosint16((dig_T2[1] << 8) | dig_T2[0])
      self._dig_T3 = self._utosint16((dig_T3[1] << 8) | dig_T3[0])
      # Pressure
      dig_P1 = self._bus.read(BME280_REG_DIG_P1, 2)
      dig_P2 = self._bus.read(BME280_REG_DIG_P2, 2)
      dig_P3 = self._bus.read(BME280_REG_DIG_P3, 2)
      dig_P4 = self._bus.read(BME280_REG_DIG_P4, 2)
      dig_P5 = self._bus.read(BME280_REG_DIG_P5, 2)
      dig_P6 = self._bus.read(BME280_REG_DIG_P6, 2)
      dig_P7 = self._bus.read(BME280_REG_DIG_P7, 2)
      dig_P8 = self._bus.read(BME280_REG_DIG_P8, 2)
      dig_P9 = self._bus.read(BME280_REG_DIG_P9, 2)
      self._dig_P1 = (dig_P1[1] << 8) | dig_P1[0]
      self._dig_P2 = self._utosint16((dig_P2[1] << 8) | dig_P2[0])
      self._dig_P3 = self._utosint16((dig_P3[1] << 8) | dig_P3[0])
      self._dig_P4 = self._utosint16((dig_P4[1] << 8) | dig_P4[0])
      self._dig_P5 = self._utosint16((dig_P5[1] << 8) | dig_P5[0])
      self._dig_P6 = self._utosint16((dig_P6[1] << 8) | dig_P6[0])
      self._dig_P7 = self._utosint16((dig_P7[1] << 8) | dig_P7[0])
      self._dig_P8 = self._utosint16((dig_P8[1] << 8) | dig_P8[0])
      self._dig_P9 = self._utosint16((dig_P9[1] << 8) | dig_P9[0])
      # Humidity
      dig_H1 = self._bus.read(BME280_REG_DIG_H1, 1)
      dig_H2 = self._bus.read(BME280_REG_DIG_H2, 2)
      dig_H3 = self._bus.read(BME280_REG_DIG_H3, 1)
      dig_H4 = self._bus.read(BME280_REG_DIG_H4, 2)
      dig_H5 = self._bus.read(BME280_REG_DIG_H5, 2)
      dig_H6 = self._bus.read(BME280_REG_DIG_H6, 1)
      self._dig_H1 = dig_H1[0]
      self._dig_H2 = self._utosint16((dig_H2[1] << 8) | dig_H2[0])
      self._dig_H3 = dig_H3[0]
      self._dig_H4 = ((self._utosint8(dig_H4[0]) << 24) >> 20) | (dig_H4[1] & 0x0F)
      self._dig_H5 = ((self._utosint8(dig_H5[1]) << 24) >> 20) | ((dig_H5[0] >> 4) & 0x0F)
      self._dig_H6 = self._utosint8(dig_H6[0])


   def _compensateTemp(self, utemp):
      """Compensates the temperature with the calibration parameters."""
      var1 = (((utemp >> 3) - (self._dig_T1 << 1)) * self._dig_T2) >> 11
      var2 = (((((utemp >> 4) - (self._dig_T1)) * ((utemp >> 4) -
             (self._dig_T1))) >> 12) * self._dig_T3) >> 14
      self._t_fine = var1 + var2
      temp = (((self._t_fine) * 5 + 128) >> 8) / 100
      return temp


   def _compensatePress(self, upress):
      """Compensates the pressure with the calibration parameters."""
      var1 = self._t_fine - 128000
      var2 = var1 * var1 * self._dig_P6
      var2 = var2 + ((var1 * self._dig_P5) << 17)
      var2 = var2 + ((self._dig_P4) << 35)
      var1 = ((var1 * var1 * self._dig_P3) >> 8) + ((var1 * self._dig_P2) << 12)
      var1 = (((1 << 47) + var1) * self._dig_P1) >> 33
      if var1 == 0:
         # Avoid div by 0
         return 0
      press = 1048576 - upress
      press = (((press << 31) - var2) * 3125) / var1
      var1 = (self._dig_P9 * (press / 8192) * (press / 8192)) / 33554432
      var2 = (self._dig_P8 * press) / 524288
      press = ((press + var1 + var2) / 256) + (self._dig_P7 << 4)
      return press


   def _compensateHum(self, uhum):
      """Compensates the humidity with the calibration parameters."""
      hum = self._t_fine - 76800
      hum = (((((uhum << 14) - (self._dig_H4 << 20) - (self._dig_H5 * hum)) +
            16384) >> 15) * (((((((hum * self._dig_H6) >> 10) *
            (((hum * self._dig_H3) >> 11) + 32768)) >> 10) + 2097152) *
            self._dig_H2 + 8192) >> 14))
      hum = hum - (((((hum >> 15) * (hum >> 15)) >> 7) * self._dig_H1) >> 4)
      if hum < 0:
         hum = 0
      elif hum > 419430400:
         hum = 419430400
      hum = hum >> 12
      return hum


   def getTemperature(self, oversample=BME280_OVERSAMP_16X):
      """Reads the temperature from the BME280 with the data compensated."""
      # Set the BME280
      self._bus.write(BME280_REG_CTRL_HUMIDITY, [oversample])
      oversample_control = (oversample << 5) | (oversample << 2) | 1
      self._bus.write(BME280_REG_CTRL_MEAS, [oversample_control])
      # Wait for the meassurement
      meassure_time = (1.25 + (2.3 * (1 << oversample))) / 1000
      time.sleep(meassure_time)
      # Read and compensate the temperature
      tempReg = self._bus.read(BME280_REG_TEMPERATURE, 3)
      utemp = ((tempReg[0] << 16) | (tempReg[1] << 8) | tempReg[2]) >> 4
      temp = self._compensateTemp(utemp)
      return temp


   def getHumidity(self, oversample=BME280_OVERSAMP_16X):
      """Reads the humidity from the BME280 with the data compensated."""
      # Read the temperature to set the t_fine
      temp = self.getTemperature(oversample)
      # Read and compensate the humidity
      humReg = self._bus.read(BME280_REG_HUMIDITY, 2);
      uhum = (humReg[0] << 8) | humReg[1]
      hum = self._compensateHum(uhum)
      # _compensateHum returns humidity in Q22.10 format
      hum = hum / 1024
      return hum


   def getPressure(self, oversample=BME280_OVERSAMP_16X):
      """Reads the pressure from the BME280 with the data compensated."""
      # Read the temperature to set the t_fine
      temp = self.getTemperature(oversample)
      # Read and compensate the pressure
      pressReg = self._bus.read(BME280_REG_PRESSURE, 3);
      upress = ((pressReg[0] << 16) | (pressReg[1] << 8) | pressReg[2]) >> 4
      press = self._compensatePress(upress)
      # _compensatePres returns pressure in Q24.8 format
      press = press / 256
      return press
# -----------------------
