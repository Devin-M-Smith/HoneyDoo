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
        if con.has_section('PARTNER'):
            config.paireduid = con['PARTNER']['uid']
            config.pairedName = con['PARTNER']['name']
    else:
        window = "nosave"
    return window

def plus():
    if con.read('config.ini'):
        window = "addTask"
    else:
        window = "nosave"
    return window