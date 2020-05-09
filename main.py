#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase
from time import sleep
from threading import Thread
import os
import socket

client_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected = False
SERVER_IP = '192.168.86.35'
SERVER_PORT = 50001
_speed = 255

# define motors
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)

# defing sensors
ultrasonic_sensor = UltrasonicSensor(Port.S1)

brick.light(Color.BLACK)
print('running')
j = 0

def GoForwards():
    global _speed
    left_motor.run(_speed)
    right_motor.run(_speed)
    #brick.sound.file(SoundFile.FORWARDS)

def GoBackwards():
    global _speed
    left_motor.run(-1*_speed)
    right_motor.run(-1*_speed)
    #brick.sound.file(SoundFile.BACKWARDS)

def TurnLeft():
    global _speed
    left_motor.run(-1*_speed)
    right_motor.run(_speed)
    #brick.sound.file(SoundFile.LEFT)

def TurnRight():
    global _speed
    left_motor.run(_speed)
    right_motor.run(-1*_speed)
    #brick.sound.file(SoundFile.RIGHT)

def Stop():
    left_motor.stop()
    right_motor.stop()
    #brick.sound.file(SoundFile.STOP)

def BackUp():
    Stop()
    brick.sound.beep()
    GoBackwards()
    sleep(0.2)
    Stop()

    #left_motor.run_time(-255, 1000, False)
    #right_motor.run_time(-255, 1000, False)


def connect():
    global client_skt
    client_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        con_result = client_skt.connect((SERVER_IP, SERVER_PORT))
    except:
        print('connect exception')


def tick():
    global j
    global client_skt
    
    while True:
        j+=1
        #print('tick ' + str(j))
        print(str(ultrasonic_sensor.distance()))
        send_result = 0
        try:
            send_result = client_skt.send(bytes('*', 'utf-8'))
        except:
            print('send exception')
        finally:
            sleep(1)
            if (send_result == 0):
                connected = False
                brick.light(Color.RED)
                client_skt.close()
                connect()
            else:
                connection = True
                brick.light(Color.GREEN)
            #print('send_result:' + str(send_result))

def receive():

    global connected

    #if (connected):
    global client_skt
    global _speed
    while True:
        try:
            data = client_skt.recv(256).decode()
            if (data):
                print("received message:" + str(data))

                if (data[:9] == ":FORWARDS"):
                    GoForwards()

                if (data[:4] == ":FWD"):
                    GoForwards()

                if (data[:10] == ":BACKWARDS"):
                    GoBackwards()

                if (data[:4] == ":REV"):
                    GoBackwards()
                
                if (data[:9] == ":TURNLEFT"):
                    TurnLeft()

                if (data[:5] == ":LEFT"):
                    TurnLeft()

                if (data[:10] == ":TURNRIGHT"):
                    TurnRight()

                if (data[:6] == ":RIGHT"):
                    TurnRight()

                if (data[:5] == ":STOP"):
                    Stop()

                if (data[:5] == ":FAST"):
                    _speed = 255

                if (data[:7] == ":MEDIUM"):
                    _speed = 127

                if (data[:5] == ":SLOW"):
                    _speed = 50

        except:
            print('receive exception')
    sleep(0.1)
            
        
connect()

# start heartbeat thread
t1 = Thread(target=tick)
t1.start()

# start receive thread
t2 = Thread(target=receive)
t2.start()

#left_motor.run(255)
#right_motor.run(255)

while True:
    front_dist = ultrasonic_sensor.distance()
    if (front_dist < 50):
        BackUp()
        
    sleep(0.2)



