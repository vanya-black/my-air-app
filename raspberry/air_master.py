import os
import serial
from serial import SerialException
from time import sleep
import logging
from datetime import datetime
import sqlite3

COMMAND = b'\x55\xCD\x47\x00\x00\x00\x00\x00\x00\x01\x69\x0D\x0A'
DB_NAME = '~/my-air-app/air.db'
REQUEST_INTERVAL = 5

logging.basicConfig(filename='~/my-air-app/air_master.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

def get_connection() -> serial.Serial:
    is_connected = False
    while not is_connected:
        try:
            ser = serial.Serial('/dev/ttyUSB0', 19200, timeout=5)
            sleep(30)
            while ser.in_waiting != 0:
                ser.readline()
            is_connected = True
            return ser
        except SerialException as ex:
            logging.warning(f'Cannot estabilish connection to serial port, sleeping 30 sec and retry. Exceptinon:  {ex}')
            sleep(30)


def prepare_db(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE air_storage (
            id INTEGER PRIMARY KEY,
            dt DATETIME,
            pm25 INTEGER,
            pm10 INTEGER,
            hcho REAL,
            tvoc REAL,
            co2 INTEGER,
            temp REAL,
            rh REAL, 
            runnig_hours INTEGER,
            um_03_parts_num INTEGER,
            um_05_parts_num INTEGER,
            um_1_parts_num INTEGER,
            um_25_parts_num INTEGER,
            um_50_parts_num INTEGER,
            um_10_parts_num INTEGER
        );
    """)
    conn.commit()
    conn.close()


def store_data(values: dict, conn):
    cur = conn.cursor()
    cur.execute("""INSERT
                        INTO
                        air_storage (dt,
                                    pm25,
                                    pm10,
                                    hcho,
                                    tvoc,
                                    co2,
                                    temp,
                                    rh,
                                    runnig_hours,
                                    um_03_parts_num,
                                    um_05_parts_num,
                                    um_1_parts_num,
                                    um_25_parts_num,
                                    um_50_parts_num,
                                    um_10_parts_num)
                        VALUES (:dt,
                                :pm25,
                                :pm10,
                                :hcho,
                                :tvoc,
                                :co2,
                                :temp,
                                :rh,
                                :runnig_hours,
                                :um_03_parts_num,
                                :um_05_parts_num,
                                :um_1_parts_num,
                                :um_25_parts_num,
                                :um_50_parts_num,
                                :um_10_parts_num)""", values)
    conn.commit()


ser = get_connection()

if not os.path.isfile(DB_NAME):
    logging.info(f"DB is not exist, creating")
    prepare_db(DB_NAME)
conn = sqlite3.connect(DB_NAME)

values = {}

while True:
    try:
        ser.write(COMMAND)
        data = ser.read_until(b'\r\n')
        logging.info(f'Received {len(data)} bytes: {data}')
        values['dt'] = datetime.utcnow()
        values['pm25'] = int.from_bytes(data[1:3], byteorder='big',  signed=False)
        values['pm10'] = int.from_bytes(data[3:5], byteorder='big',  signed=False)
        values['hcho'] = int.from_bytes(data[5:7], byteorder='big',  signed=False) / 1000
        values['tvoc'] = int.from_bytes(data[7:9], byteorder='big',  signed=False) / 1000
        values['co2'] = int.from_bytes(data[9:11], byteorder='big',  signed=False)
        values['temp'] = int.from_bytes(data[11:13], byteorder='big',  signed=True) / 100
        values['rh'] = int.from_bytes(data[13:15], byteorder='big',  signed=False) / 100
        values['runnig_hours'] = int.from_bytes(data[17:19], byteorder='big',  signed=False)
        values['um_03_parts_num'] = int.from_bytes(data[19:21], byteorder='big',  signed=False)
        values['um_05_parts_num'] = int.from_bytes(data[21:23], byteorder='big',  signed=False)
        values['um_1_parts_num'] = int.from_bytes(data[23:25], byteorder='big',  signed=False)
        values['um_25_parts_num'] = int.from_bytes(data[25:27], byteorder='big',  signed=False)
        values['um_50_parts_num'] = int.from_bytes(data[27:29], byteorder='big',  signed=False)
        values['um_10_parts_num'] = int.from_bytes(data[29:31], byteorder='big',  signed=False)
        store_data(values, conn)
        sleep(REQUEST_INTERVAL)
    except SerialException as ex:
        logging.warning(f'Cannot read data, try to connect. Exceptinon: {ex}')
        ser.close()
        ser = get_connection()
