import io
import os
import time
import pynmea2
import serial
from flask import Flask, send_file, jsonify
#from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from apscheduler.schedulers.background import BackgroundScheduler
from picamera import PiCamera
from gpiozero import LED
 
app = Flask(__name__)
#api = Api(app)
camera = PiCamera()
ser = serial.Serial('/dev/ttyS0', 9600, timeout=5.0)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
lat = 0;
lng = 0;
led = LED(23)

def gps_job():
    global lat;
    global lng;
    try:
        line = sio.readline()
        print(line)
        if line:
            msg = pynmea2.parse(line)
            if msg:
                if msg.latitude and msg.longitude:
                    lat=msg.latitude
                    lng=msg.longitude
                    gps = "Latitude=" + str(lat) + "and Longitude=" + str(lng)
                    print(gps)
    except Exception as e:
        print('error: {}'.format(e))

scheduler = BackgroundScheduler()
job = scheduler.add_job(gps_job, 'interval', seconds=3)
scheduler.start()


@app.route('/gps')
def gps():
    result = {"lat":lat, "lng":lng}
    return jsonify(result), 200
 
@app.route('/picture')
def picture():
    camera.capture('/run/user/1000/image.jpg')
    return send_file('/run/user/1000/image.jpg')

@app.route('/buzzer')
def buzzer():
    led.on()
    time.sleep(2)
    led.off()
    return 'success', 200

           
app.run(host='0.0.0.0', port=12345)