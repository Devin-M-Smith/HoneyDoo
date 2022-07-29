from configparser import ConfigParser
from time import sleep
con = ConfigParser()

def startWindow():
    sleep(4)
    if con.read('config.ini'):
        window = "main"
    else:
        window = "nosave"
    return window

def plus():
    if con.read('config.ini'):
        window = "addTask"
    else:
        window = "nosave"
    return window