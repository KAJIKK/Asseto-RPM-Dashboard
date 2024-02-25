import time
import acsys
import ac
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "dll"))
os.environ['PATH'] = os.environ['PATH'] + ";."

from serial.tools.list_ports import comports
import serial


##########CONFIG###########
MAX_LEDS = 60
IDLE_LEDS = 5
MAX_RPM = 18000
IDLE_RPM = 4000

PORT = "COM19"
###########################

timer = 0
ports = {}

ser = None

def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def openConfig(*args, **kwargs):
    os.system("start notepad ./apps/python/ArduinoRPMDash/ArduinoRPMDash.py")  


def acMain(acVersion):
    # do something with serial library
    global ser, rpmLabel, rpmForArdLabel, connected, arduinoPort, ports
    ac.log("called acMain()")
    for arduinoPort, desc, hwid in sorted(comports()):
        ac.console("Port: {} | Description: {}".format(arduinoPort, desc))


    appWindow = ac.newApp("Arduino RPM Dash")
    ac.setSize(appWindow, 200, 200)

    rpmLabel = ac.addLabel(appWindow, "rpm")
    ac.setPosition(rpmLabel, 10, 40)

    rpmForArdLabel = ac.addLabel(appWindow, "leds")
    ac.setPosition(rpmForArdLabel, 10, 60)

    connected = ac.addLabel(appWindow, "connected")
    ac.setPosition(connected, 10, 100)

    configButton = ac.addButton(appWindow, "Config")
    ac.setPosition(configButton, 10, 140)
    ac.setSize(configButton, 100, 20)
    ac.addOnClickedListener(configButton, openConfig)

    arduinoPort = ac.addTextInput(appWindow, "port")
    ac.setPosition(arduinoPort, 10, 120)
    ac.setSize(arduinoPort, 100, 20)
    ac.setText(arduinoPort, PORT)

    """
    ac.setAllowDeselection(port, 1)
    for p, desc, hwid in sorted(comports()):
        i = ac.addItem(port, p)
        ports[i] = p
    """

    try:
        ser = serial.Serial(port=PORT, baudrate=9600, timeout=0)
    except serial.SerialException:
        ac.log("Serial port {} not found".format(PORT))
        ac.setText(connected, "Disconnected")
    return "Arduino RPM Dash"


def acUpdate(deltaT):
    global ser, ac, acsys, timer

    rpm = ac.getCarState(0, acsys.CS.RPM)
    ac.setText(rpmLabel, "RPM: {}".format(rpm))

    if timer < 0.01:
        timer += deltaT
        return

    rpmForArduino = str(int(map_range(rpm, IDLE_RPM, MAX_RPM, IDLE_LEDS, MAX_LEDS))) + "\n"
    ac.setText(rpmForArdLabel, "LEDs: {}".format(rpmForArduino))

    if ser is None or not ser.isOpen():
        if timer < 1:
            timer += deltaT
            return
        try:
            ac.log("Trying to open serial port: " + ac.getText(arduinoPort))
            ser = serial.Serial(port=ac.getText(arduinoPort), baudrate=9600, timeout=0)
        except serial.SerialException:
            ac.log("Serial port not found")
            return
    try:
        ser.write(rpmForArduino.encode())
    except serial.SerialException:
        ac.log("Serial exception, closing port")
        ac.setText(connected, "Disconnected")
        ser = None
        return
    else:
        ac.setText(connected, "Connected")

    timer = 0


def acShutdown():
    global ser
    ac.log("called acShutdown()")
    ser.write("0".encode())
    ser.close()
