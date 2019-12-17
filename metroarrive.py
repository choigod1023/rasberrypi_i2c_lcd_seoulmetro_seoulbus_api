#-*-coding utf-8-*-
from bs4 import BeautifulSoup
import requests
import json
from datetime import date, timedelta, datetime

#!/usr/bin/python
#--------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#  lcd_i2c.py
#  LCD test script using I2C backpack.
#  Supports 16x2 and 20x4 screens.
#
# Author : Matt Hawkins
# Date   : 20/09/2015
#
# http://www.raspberrypi-spy.co.uk/
#
# Copyright 2015 Matt Hawkins
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#--------------------------------------
import smbus
import time

# Define some device parameters
I2C_ADDR = 0x27  # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1  # Mode - Sending data
LCD_CMD = 0  # Mode - Sending command

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94  # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4  # LCD RAM address for the 4th line

LCD_BACKLIGHT = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100  # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1


def split(a):
    if a[0:6].find("]") != -1:
        a = a.split("]")[1]
    if a.find("후") != -1:
        a = a.split("후")[0]
        a = a.replace("분", "m")
        a = a.replace("초", "s")
    if a.find("곧 도착") != -1:
        a = "arrived"
    if a.find("운행종료") != -1:
        a = "end"
    if a.find("출발대기") != -1:
        a = "no out"
    return a


def downbus():
    res = requests.get(
        'http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid?serviceKey=vXvsHQHWzrazD2IdIoKz45y%2BKC7zNIIvleqiGB%2Ba%2FxdmpIOu8MQT35lFTuk6tE%2BFLbk%2F3PuX5DODucPWridzxA%3D%3D&arsId=09152').text
    soup = BeautifulSoup(res, "html.parser")
    for data in soup.find('arrmsg1'):
        a = data.string
    a = split(a)

    for data in soup.find_all('arrmsg1'):
        b = data.string
    b = split(b)
    lcd_string("BUS INFO", LCD_LINE_1)
    lcd_string("to BukbuMarket", LCD_LINE_2)
    time.sleep(3)

    lcd_string('102 ' + a, LCD_LINE_1)
    lcd_string('1133 '+b, LCD_LINE_2)
    time.sleep(3)


def metro():
    d = date.today()
    month = d.month
    year = d.year
    if month < 10:
        month = '0'+str(month)
    else:
        month = str(month)

    res = requests.get('http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo?serviceKey=vXvsHQHWzrazD2IdIoKz45y%2BKC7zNIIvleqiGB%2Ba%2FxdmpIOu8MQT35lFTuk6tE%2BFLbk%2F3PuX5DODucPWridzxA%3D%3D&solYear='+str(year)+'&solMonth='+month)
    soup = BeautifulSoup(res.text, "html.parser")
    holyday = []
    for data in soup.findAll('locdate'):
        holyday.append(data.string)
    j = 0
    check = 1
    for i in holyday:
        if((datetime(int(holyday[j][0:4]), int(holyday[j][4:6]), int(holyday[j][6:8]))-datetime(datetime.today().year, datetime.today().month, datetime.today().day)).days) == 0:
            check = 3
            break
        j += 1
    dt = datetime.now()
    if dt.weekday() == 5:
        check = 2
    elif dt.weekday() == 6:
        check = 3

    res = requests.get(
        'http://openapi.seoul.go.kr:8088/70445a6269636869353963764e4764/json/SearchArrivalTimeOfLine2SubwayByIDService/1/1/0414/2/'+str(check)+'/').text
    dict = json.loads(res)
    arrive = (dict['SearchArrivalTimeOfLine2SubwayByIDService']
              ['row'][0]['ARRIVETIME'])
    destination = (dict['SearchArrivalTimeOfLine2SubwayByIDService']
                   ['row'][0]['DESTSTATION_NAME'])
    lcd_string("METRO INFO", LCD_LINE_1)
    if len(destination) == 3:
        lcd_string("to Oido", LCD_LINE_2)
    else:
        lcd_string("to Sadang", LCD_LINE_2)
    time.sleep(3)
    lcd_string("arrive at Suyu", LCD_LINE_1)
    lcd_string(arrive, LCD_LINE_2)
    time.sleep(3)
    res = requests.get(
        'http://openapi.seoul.go.kr:8088/70445a6269636869353963764e4764/json/SearchArrivalTimeOfLine2SubwayByIDService/1/1/0414/1/'+str(check)+'/').text
    dict = json.loads(res)
    arrive = (dict['SearchArrivalTimeOfLine2SubwayByIDService']
              ['row'][0]['ARRIVETIME'])
    lcd_string("METRO INFO", LCD_LINE_1)
    lcd_string("to Danggogae",LCD_LINE_2)
    time.sleep(3)
    lcd_string("arrive at Suyu",LCD_LINE_1)
    lcd_string(arrive, LCD_LINE_2)
    time.sleep(3)

def upbus():
    res = requests.get(
            'http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid?serviceKey=vXvsHQHWzrazD2IdIoKz45y%2BKC7zNIIvleqiGB%2Ba%2FxdmpIOu8MQT35lFTuk6tE%2BFLbk%2F3PuX5DODucPWridzxA%3D%3D&arsId=09153').text
    soup = BeautifulSoup(res, "html.parser")
    datas = soup.select("arrmsg1")
    array=[]
    for data in datas:
        array.append(data.text)
    c = array[0]
    d = array[1]
    e = array[2]
    c = split(c)
    d = split(d)
    e = split(e)

    lcd_string("BUS INFO",LCD_LINE_1)
    lcd_string("to CHANGDONG",LCD_LINE_2)
    time.sleep(3)
    lcd_string("102 " + d,LCD_LINE_1)
    lcd_string("1133 " + e,LCD_LINE_2)
    time.sleep(3)
    lcd_string("Nowon14 " + c,LCD_LINE_1)
    lcd_string("",LCD_LINE_2)
    time.sleep(3)
def lcd_init():
  # Initialise display
  lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
  lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
  lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
  lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
  lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
  time.sleep(E_DELAY)


def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)


def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
  time.sleep(E_DELAY)


def lcd_string(message, line):
  # Send string to display

  message = message.ljust(LCD_WIDTH, " ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]), LCD_CHR)


def main():
  # Main program block

  # Initialise display
  lcd_init()

  while True:

    # Send some test
    try:

         metro()
         downbus()
         upbus()

    except:
       lcd_string('NONE', LCD_LINE_1)
       lcd_string('NONE', LCD_LINE_2)
       time.sleep(3)


if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
