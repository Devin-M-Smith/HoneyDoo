from configparser import ConfigParser
import mysql.connector as mysql

config = ConfigParser()


def registerUser():
    print("test")


if config.read('config.ini'):
    pass
else:
    mydb = mysql.connector.connect(
            host = "localhost",
            user = "root",
            passwd = "060302",
            database = 'honeydoo'
        )

    c = mydb.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS USERS(
            UID INT NOT NULL AUTO_INCREMENT,
            USERNAME VARCHAR(30) NOT NULL,
            PASSWORD VARCHAR(255) NOT NULL,
            EMAIL VARCHAR(100) NOT NULL,
            PRIMARY KEY (UID)
        )
    """)

    mydb.commit()
    mydb.close()
    registerUser()