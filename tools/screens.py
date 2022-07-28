from email.message import EmailMessage
from random import randint
from kivy.uix.screenmanager import Screen
import tools.config as config
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
import tools.checkSave as checkSave
import tools.HoneyDooSQL as HoneyDooSQL
from kivy.app import App
from configparser import ConfigParser
import re
import smtplib

con = ConfigParser()

app = App.get_running_app()

class Refresh(Screen):
    pass

class MainWindow(Screen):

    def on_pre_enter(self):
        self.ids.task_header.text = 'LOADING...'
        self.ids.task_description.text = ''
        self.ids.priority.text = ''

    def checkPriority(self, priorityNumber):
        priorityLabel = ['LOW', 'NORMAL', 'HIGH', 'MAJOR']
        return priorityLabel[priorityNumber]

    def update(self):
        try:
            c = config.mydb.cursor(buffered=True)
            c.reset()
        except:
            config.mydb = HoneyDooSQL.dbSetup()

        self.plus = checkSave.plus()
        config.task = HoneyDooSQL.readTasks(config.mydb)
        i = 0

        while i < 10:
            self.ids[list(self.ids)[i]].text = str(config.task[i]['TASK_NAME']).upper()
            i+=1
    
        id = 'task1'
        MainWindow.update_display(self, id)

    def update_display(self, id):
        config.displayTask = list(self.ids).index(str(id))
        self.ids.task_header.text = str(config.task[config.displayTask]['TASK_NAME'])
        self.ids.task_description.text = str(config.task[config.displayTask]['DESCRIPTION'])
        self.ids.priority.text = '[color=006633][size=10sp]' + str(config.task[config.displayTask]['DATE_CREATED']) + '[/size][/color]' + '\n[u]PRIORITY[/u]\n' + self.checkPriority(config.task[config.displayTask]['PRIORITY'])
    
    def completeTaskButton(self):

        try:
            c = config.mydb.cursor(buffered=True)
            c.reset()
        except:
            config.mydb = HoneyDooSQL.dbSetup()

        window = TaskPopUp(
            title = "Mark Task as Complete?",
            title_color = (.4, 1, .7, 1),
            title_size = '28sp', 
            separator_color = (0, .4, .2, 1),
            auto_dismiss = False, 
            background_color = (0, .4, .2, .5),
            size_hint = (None, None), 
            size = ('300sp', '150sp'))
        window.open()
    pass

class TaskPopUp(Popup):

    def updateCompleteTask(self):
        result = HoneyDooSQL.completeTask(config.mydb, config.task[config.displayTask]['TASK_ID'])
        if result == '':
            pass
        else:
            global dataError
            dataError = DataError()
            errorPopUp(result)

class TaskList(Screen):
    pass

class RegisterRequest(FloatLayout):
    pass

def RegisterPopUp():
    show = RegisterRequest()
    window = Popup(
        title = "New User",
        title_color = (.4, 1, .7, 1),
        title_size = '28sp',
        separator_color = (0, .4, .2, 1),
        content = show,
        background_color = (0, .4, .2, .5),
        size_hint = (None, None), 
        size = ('300sp', '150sp'))
    window.open()


def sendConfirmEmail():
    config.code = randint(111111, 999999)
    sender = 'HoneyDooApp@gmail.com'
    receiver = config.email

    body = "Your confirmation code is: " + str(config.code) + "\nThank You,\nHoneyDoo"

    msg = EmailMessage()
    msg['Subject'] = 'HoneyDoo Confirmation Code'
    msg['From'] = sender
    msg['To'] = receiver
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtpObj:
            smtpObj.login(sender, 'NOTREALPASS')
            smtpObj.send_message(msg)
            EmailPopUp()
    except:
        global dataError
        dataError = DataError()
        errorPopUp('Failed to Send Confirmation Email\nTry again later')
    

class EmailConfirm(Popup):
    def confirm(self, code):
        if len(code) > 2:
            if int(code) == config.code:
                config.result = HoneyDooSQL.registerUser(config.mydb, config.name, config.email, config.psswd)
            else:
                config.result = 'Code Does Not Match\nTry Again'
        else:
            config.result = 'Code Does Not Match\nTry Again'

        if (config.result.isdigit()):
            con['USER'] = {}
            con['USER']['uid'] = config.result
            con['USER']['email'] = config.email.upper()
            con['USER']['name'] = config.name.upper()
            with open('config.ini','w') as configfile:
                con.write(configfile)
            return 'main'
        else:
            global dataError
            dataError = DataError()
            errorPopUp(config.result)
            return 'register'

def EmailPopUp():
    window = EmailConfirm(
        title = "Confirmation",
        title_color = (.4, 1, .7, 1),
        title_size = '28sp', 
        separator_color = (0, .4, .2, 1),
        background_color = (0, .4, .2, .5),
        size_hint = (None, None), 
        size = ('350sp', '150sp'))
    window.open()


class NoSave(Screen):
    pass

class SignIn(Screen):

    def signIn(self, email, psswd):
        try:
            config.result = HoneyDooSQL.signIn(config.mydb, email, psswd)
        except:
            config.result = 'User Not Found'

        if (config.result.isdigit()):
            con['USER'] = {}
            con['USER']['uid'] = config.result
            con['USER']['email'] = config.email.upper()
            con['USER']['name'] = config.name.upper()
            with open('config.ini','w') as configfile:
                con.write(configfile)
            return 'main'
        else:
            global dataError
            dataError = DataError()
            errorPopUp(config.result)
            return 'sign'
    pass

class Register(Screen):

    def on_enter(self):
        RegisterPopUp()

    def submitUser(self, email, name, psswd, psswd2):
        if (
            email == ''
            or
            name == ''
            or 
            psswd == ''
            or
            psswd2 == ''):
            config.result = 'Please fill out all fields'
            global dataError
            dataError = DataError()
            errorPopUp(config.result) 
        else:
            if (re.fullmatch(config.regex, email)):
                if psswd == psswd2:
                    config.name = name
                    config.email = email
                    config.psswd = psswd
                    sendConfirmEmail()
                else:
                    config.result = 'Passwords Do Not Match'
                    dataError = DataError()
                    errorPopUp(config.result) 
            else:
                config.result = 'Invalid Email'
                dataError = DataError()
                errorPopUp(config.result) 
            

        
    pass

class NewTask(Screen):
    
    def on_enter(self):
        con.read('config.ini')
        usernames = []
        for f in con.sections():
            usernames.append(con[f]['name'])
        self.ids.assigned.values = usernames

    def submitTask(self, user, task_name, description, priority):

        try:
            c = config.mydb.cursor(buffered=True)
            c.reset()
        except:
            config.mydb = HoneyDooSQL.dbSetup()

        try:
            priority = self.ids.priority.values.index(priority)
        except:
            priority = -1
        try:
            user = self.ids.assigned.values.index(user)
        except:
            user = -1

        if (
            user == -1
            or
            task_name == ''
            or
            description == ''
            or
            priority == -1):
            result = 'Please fill out all fields'
        else:
            if user == 0:
                result = HoneyDooSQL.writeTask(config.mydb, int(con['USER']['uid']), task_name, description, priority)
            else:
                result = HoneyDooSQL.writeTask(config.mydb, int(con['PARTNER']['uid']), task_name, description, priority)

        if result == '':
            pass
            return 'main'
        else:
            global dataError
            dataError = DataError()
            errorPopUp(result)
            return 'addTask'
    pass
        
class DataError(FloatLayout):
    pass

def errorPopUp(result):

    dataError.ids.error.text = str(result)
    show = dataError

    window = Popup(
        title = "Entry Error",
        title_color = (.4, 1, .7, 1),
        title_size = '28sp', 
        separator_color = (0, .4, .2, 1),
        content = show, 
        background_color = (0, .4, .2, .5),
        size_hint = (None, None), 
        size = ('300sp', '150sp'))
    window.open()
