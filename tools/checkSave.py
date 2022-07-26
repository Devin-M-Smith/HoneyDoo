from configparser import ConfigParser
from time import sleep
con = ConfigParser()

def startWindow():
    sleep(4)
    if con.read('config.ini'):
        window = "main"
    else:
        window = "register"
    return window

def plus():
    if con.read('config.ini'):
        window = "addTask"
    else:
        window = "register"
    return window

def check():
    if con.read('config.ini'):
        checkResult = True
    else:
        checkResult = False
    return checkResult