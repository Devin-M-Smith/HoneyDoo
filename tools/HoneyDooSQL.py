import datetime
import mysql.connector
from mysql.connector import Error
from configparser import  ConfigParser

config = ConfigParser()

def dbSetup():
    #if config.read('config.ini'):
    #    pass
    #else:
    try:
        mydb = mysql.connector.connect(
        host = "devin-m-smith.com",
        port = 3306, #change to devin-m-smith.com for production
        user = "HoneyDoo",
        passwd = "honeydoo",
        database = 'honeydoo',
        connect_timeout = 8
    )
    except Error:
        mydb = mysql.connector.connect(
        host = "10.0.0.147",
        port = 3306,
        user = "HoneyDoo",
        passwd = "honeydoo",
        database = 'honeydoo',
        connect_timeout = 3
    )
    except:
        mydb = mysql.connector.connect(
        host = "localhost",
        user = "HoneyDoo",
        passwd = "honeydoo",
        database = 'honeydoo',
        connect_timeout = 3
    )
    return mydb
    
def readTasks(mydb):
    c = mydb.cursor(dictionary=True)
    c.execute("""
        SELECT * FROM TASKS
        ORDER BY PRIORITY DESC, TASK_NAME
    """)
    records = c.fetchall()
    print(records)
    task = []
    recordCount = 0
    for record in records:
        recordCount += 1
    taskCount = 0
    while taskCount < recordCount:
        task.append(records[taskCount])
        taskCount += 1
    while taskCount < 10:
        task.append({'TASK_NAME' : 'No Task', 'DESCRIPTION': 'No Task', 'PRIORITY': 0})
        taskCount += 1
    return task

def writeTask(mydb, user, taskName, taskDetail, taskPriority):
    c = mydb.cursor(dictionary=True)
    try:
        c.execute("""
            INSERT INTO TASKS
            (TASK_NAME, DESCRIPTION, PRIORITY, DATE_CREATED)
            VALUES
            (%s, %s, %s, %s)
        """, (taskName, taskDetail, taskPriority, datetime.date.today()))
        mydb.commit()
        return ''
    except Error as E:
        return E
    except:
        return 'Unknown Error'
    