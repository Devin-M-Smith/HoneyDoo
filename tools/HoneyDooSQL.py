import datetime
import mysql.connector
from mysql.connector import Error
from tools.passwordHandler import encryptPassword
import tools.config as config

def dbSetup():
    try:
        mydb = mysql.connector.connect(
        host = "devin-m-smith.com",
        port = 3306,
        user = "HoneyDoo",
        passwd = "NOTREALPASS",
        database = 'honeydoo',
        connect_timeout = 15,
        auth_plugin='mysql_native_password'
    )
    except Error:
        mydb = mysql.connector.connect(
        host = "10.0.0.147",
        port = 3306,
        user = "HoneyDoo",
        passwd = "NOTREALPASS",
        database = 'honeydoo',
        connect_timeout = 3,
        auth_plugin='mysql_native_password'
    )
    except:
        mydb = mysql.connector.connect(
        host = "localhost",
        user = "HoneyDoo",
        passwd = "NOTREALPASS",
        database = 'honeydoo',
        connect_timeout = 3,
        auth_plugin='mysql_native_password'
    )
    return mydb


def signIn(mydb, email, psswd):
    mydb.commit()
    psswd2 = encryptPassword(psswd)
    c = mydb.cursor(dictionary=True)
    c.execute("""
        SELECT * FROM USERS
        WHERE EMAIL = %s
        AND PASSWORD = %s;
    """, (email.upper(), psswd2))
    userMatch = c.fetchall()
    user = []
    user.append(userMatch[0])
    config.email = str(user[0]['EMAIL'])
    config.name = str(user[0]['NAME'])
    config.uid = str(user[0]['UID'])
    c.reset()
    return str(user[0]['UID'])


def getUser(mydb, UID):
    mydb.commit()
    c = mydb.cursor(dictionary=True)

    c.execute("""
        SELECT NAME FROM USERS
        WHERE UID = %s;
    """, (UID, ))
    user = c.fetchall()
    return user[0]['NAME']

def readAllTasks(mydb):

    mydb.commit()
    c = mydb.cursor(dictionary=True)

    c.execute("""
        SELECT * FROM TASKS
        WHERE UID = %s
        OR UID = %s
        ORDER BY DATE_CREATED DESC, PRIORITY DESC;
    """, (config.uid, config.uid)) # 1 is open, 0 is closed

    records = c.fetchall()
    task = []

    i = 0
    for record in records:
        task.append(records[i])
        i += 1

    return task

def readTasks(mydb):
    mydb.commit()
    c = mydb.cursor(dictionary=True)

    c.execute("""
        SELECT * FROM TASKS
        WHERE STATUS = 1
        AND UID = %s
        ORDER BY DATE_CREATED ASC, PRIORITY DESC
    """, (config.uid, )) # 1 is open, 0 is closed

    records = c.fetchall()
    task = []

    for record in records:
        task.append(record)
    return task

def readTasksOld(mydb):

    mydb.commit()
    c = mydb.cursor(dictionary=True)

    c.execute("""
        SELECT * FROM TASKS
        WHERE STATUS = 1
        AND UID = %s
        ORDER BY DATE_CREATED ASC, PRIORITY DESC
    """, (config.uid, )) # 1 is open, 0 is closed

    records = c.fetchall()
    task = []

    recordCount = 0
    for record in records:
        recordCount += 1

    taskCount = 0
    while taskCount < recordCount:
        task.append(records[taskCount])
        taskCount += 1

    while taskCount < 10:
        task.append({'UID': config.uid, 'NAME': '', 'TASK_ID': 0, 'TASK_NAME' : 'NO TASK', 'DESCRIPTION': 'NO TASK', 'STATUS': 0, 'PRIORITY': 0, 'DATE_CREATED': datetime.date.today()})
        taskCount += 1
    return task

def writeTask(mydb, user, taskName, taskDetail, taskPriority):

    c = mydb.cursor(dictionary=True)

    try:
        c.execute("""
            INSERT INTO TASKS
            (UID, TASK_NAME, DESCRIPTION, PRIORITY, STATUS, DATE_CREATED)
            VALUES
            (%s, %s, %s, %s, %s, %s)
        """, (user, taskName.upper(), taskDetail.upper(), taskPriority, 1, datetime.date.today()))
        mydb.commit()
        return ''
    except Error as E:
        return E
    except:
        return 'Unknown Error'
    
def completeTask(mydb, taskID):

    c = mydb.cursor(dictionary=True)

    try:
        c.execute("""
            UPDATE TASKS
            SET STATUS = 0,
            DATE_COMPLETED = %s
            WHERE TASK_ID = %s;
        """, (datetime.date.today(), taskID)) # close tasks by setting STATUS = 0
        mydb.commit()
        return ''
    except Error as E:
        return E
    except:
        return 'Unknown Error'

def registerUser(mydb, name, email, psswd):
    c = mydb.cursor(dictionary=True)

    try:
        c.execute("""
            INSERT INTO USERS
            (NAME, EMAIL, PASSWORD, ACTIVE)
            VALUES
            (%s, %s, %s, 1);
        """, (name.upper(), email.upper(), encryptPassword(psswd)))
        mydb.commit()
        c.execute("""
            SELECT UID FROM USERS
            WHERE EMAIL = %s
            AND NAME = %s;
        """, (email.upper(), name.upper()))
        result = c.fetchall()
        return str(result[0]['UID'])
    except Error as E:
        return E
    except:
        return 'Unknown Error'