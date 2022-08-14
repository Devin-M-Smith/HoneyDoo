from configparser import ConfigParser
from time import sleep
import tools.config as config

con = ConfigParser()

def startWindow():
    sleep(4)
    if con.read('config.ini'):
        window = "main"
        config.name = con['USER']['name']
        config.uid = con['USER']['uid']
    else:
        window = "nosave"
    return window

def plus():
    if con.read('config.ini'):
        window = "addTask"
    else:
        window = "nosave"
    return window