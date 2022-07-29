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
        connect_timeout = 15
    )
    except Error:
        mydb = mysql.connector.connect(
        host = "10.0.0.147",
        port = 3306,
        user = "HoneyDoo",
        passwd = "NOTREALPASS",
        database = 'honeydoo',
        connect_timeout = 3
    )
    except:
        mydb = mysql.connector.connect(
        host = "localhost",
        user = "HoneyDoo",
        passwd = "NOTREALPASS",
        database = 'honeydoo',
        connect_timeout = 3
    )
    return mydb


def signIn(mydb, email, psswd):
    mydb.commit()
    print(email.upper())
    psswd2 = encryptPassword(psswd)
    print(psswd2)
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
    c.reset()
    return str(user[0]['UID'])


def readTasks(mydb):

    mydb.commit()
    c = mydb.cursor(dictionary=True)

    c.execute("""
        SELECT * FROM TASKS
        WHERE STATUS = 1
        ORDER BY DATE_CREATED ASC, PRIORITY DESC
    """) # 1 is open, 0 is closed

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
        task.append({'TASK_ID': 0, 'TASK_NAME' : 'NO TASK', 'DESCRIPTION': 'NO TASK', 'PRIORITY': 0, 'DATE_CREATED': datetime.date.today()})
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
            SET STATUS = 0
            WHERE TASK_ID = %s;
        """, (taskID,)) # close tasks by setting STATUS = 0
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