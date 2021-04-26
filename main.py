import io #input output device
import os #operating system
import time #time module
import pynmea2 #used to parcel nmea data
import serial #access for the serial port
from flask import Flask, send_file, jsonify  #imports Flask, send_file and jsonify from flask
#from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from apscheduler.schedulers.background import BackgroundScheduler  #imports BackgroundScheduler from apscheduler.schedulers.background
from picamera import PiCamera #imports PiCamera from
from gpiozero import LED #imports LED library from gpiozero
 
app = Flask(__name__)
#adds PiCamera() value in camera
camera = PiCamera()

ser = serial.Serial('/dev/ttyS0', 9600, timeout=5.0)#storing name of the serial port, baud rate and time out value in ser

sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser)) #extracts $GPGLL value

#default latitude and longitude value
lat = 0;
lng = 0;
buzz = LED(23)
#defines the job of gps
def gps_job():
    global lat;
    global lng;
    try:
        line = sio.readline() #reads the $GPGLL value and stores it inside 'line'
        print(line)
        if line:
            msg = pynmea2.parse(line) #values from line are parsed and are stored in msg
            if msg:
                if msg.latitude and msg.longitude:
                    lat=msg.latitude #stores latitude value in lat
                    lng=msg.longitude #stores longitude value in lng
                    gps = "Latitude=" + str(lat) + "and Longitude=" + str(lng) #converts the lat and lng value to string
                    print(gps) #prints gps data
    except Exception as e:
        print('error: {}'.format(e)) #throws error when the gps is not functioning

#updates gps data in the interval of 3 seconds
scheduler = BackgroundScheduler()
job = scheduler.add_job(gps_job, 'interval', seconds=3)
scheduler.start()

#gives the o/p of the work done by the gps  in the route /gps
@app.route('/gps')
def gps():
    result = {"lat":lat, "lng":lng} #latitude and longitude values are recived and stored in 'lat' and 'lng' respectively
    return jsonify(result), 200 #returns lat and lng value in a json file
 
 
 #captures the image seen by the picamera and is displayed on the route /picture
@app.route('/picture')
def picture():
    camera.capture('/run/user/1000/image.jpg') #captures the image using PiCamera and is stured in the path "/run/user/1000" with 'image.jpg' as the name of the captured image
    camera.rotation = 90 #rotates the captured image by 90 degrees
    return send_file('/run/user/1000/image.jpg') #sends the recived image to the /picture route where the picture is displayed

#sets off the buzzer when /buzzer route is called
@app.route('/buzzer')
def buzzer():
    buzz.on() #buzzer turns on
    time.sleep(5) #buzzer goes off for 5 sec
    buzz.off() #buzzer turns off
    return 'success', 200 #'success' is displayed in the local host's /buzzer route after the buzzer goes off

#defines the host and the port where the app is to be executed
app.run(host='0.0.0.0', port=12345)

