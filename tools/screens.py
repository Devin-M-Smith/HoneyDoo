from email.message import EmailMessage
from random import randint
import kivy
from kivy.uix.screenmanager import Screen
import tools.config as config
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
import tools.HoneyDooSQL as HoneyDooSQL
from kivy.animation import Animation
from configparser import ConfigParser
import re
import smtplib

con = ConfigParser()

def checkPriority(priorityNumber):
    priorityLabel = ['LOW', 'NORMAL', 'HIGH', 'MAJOR']
    return priorityLabel[priorityNumber]

def checkStatus(statusNumber):
    statusLabel = ['CLOSED', 'OPEN']
    return statusLabel[statusNumber]
    
def setPriorityColor(priorityNumber):
    priorityColor = ['#00ff84', '#ffffff', 'bfff00', '#ff9933']
    return priorityColor[priorityNumber]

def setStatusColor(statusNumber):
    statusColor = ['#9cc9b3', '#00ff84']
    return statusColor[statusNumber]


class Refresh(Screen):
    pass

class RegisterContent(Label):
    pass

class MainWindow(Screen):
    def on_pre_enter(self):
        self.ids.tasks.clear_widgets()
        try:
            c = config.mydb.cursor(buffered=True)
            c.reset()
        except:
            config.mydb = HoneyDooSQL.dbSetup()

        config.task = HoneyDooSQL.readTasks(config.mydb)

    def completeTask(self):
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

    def on_enter(self):

        i = 0
        for task in config.task:
            btn = TaskItem(size_hint_y=None, height='100sp')
            priorityText = '[color=66ffb3][u]PRIORITY[/u][/color]\n' + '[b]'+checkPriority(task['PRIORITY'])+'[/b]'
            statusText = '[color=66ffb3][u]STATUS[/u][/color]\n' + '[b]'+checkStatus(task['STATUS'])+'[/b]'
            priorityColor = setPriorityColor(task['PRIORITY'])
            statusColor = setStatusColor(task['STATUS'])
            dateStatus = 'DATE CREATED: ' + str(task['DATE_CREATED'])

            descriptionText = (
                '[u]DESCRIPTION[/u]\n' + task['DESCRIPTION'] +
                '\n\n' + 'ASSIGNED TO: ' + HoneyDooSQL.getUser(config.mydb, task['UID']) +
                '\n' + dateStatus)

            self.ids[str(task['TASK_ID'])] = btn 
            btn.ids.task_id.text = str(task['TASK_ID'])
            btn.ids.task_name.text = str(task['TASK_NAME'])
            btn.ids.priority.color = priorityColor
            btn.ids.priority.text = priorityText
            btn.ids.status.color = statusColor
            btn.ids.status.text = statusText
            btn.ids.dropdown.text = descriptionText
            btn.ids.dropdown.opacity = 0
            self.ids.tasks.add_widget(btn)
            i += 1
        if i==0 :
            startLabel = RegisterContent(size_hint_y=None, height='100sp', font_size='20sp', text="Click + to create a New Task")
            self.ids.tasks.add_widget(startLabel)
    pass

class TaskPopUp(Popup):

    def updateCompleteTask(self):
        result = HoneyDooSQL.completeTask(config.mydb, config.displayTask)
        if result == '':
            config.displayTask = 0
            pass
        else:
            global dataError
            dataError = DataError()
            errorPopUp(result)


class TaskItem(GridLayout):
    def shrink(self, instance):
        animation = Animation(height=(kivy.metrics.sp(100)), duration = .5)
        animation.start(instance)

    def grow(self, instance):
        animation = Animation(height=(kivy.metrics.sp(300)), duration = .5)
        config.displayTask = self.ids.task_id.text
        animation.start(instance)
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.height < kivy.metrics.sp(201):
                self.grow(self)
                self.ids.dropdown.grow(self.ids.dropdown)
            else:
                self.ids.dropdown.shrink(self.ids.dropdown)
                self.shrink(self)
        else:
            self.shrink(self)
            self.ids.dropdown.shrink(self.ids.dropdown)
    pass
    
class TaskDropdown(Label):
    def grow(self, instance):
        animation = Animation(size_hint_y=2, height=(kivy.metrics.sp(200)), duration = .3) + Animation(opacity = 1, duration = .2)
        animation.start(instance)

    def shrink(self, instance):
        animation = Animation(opacity = 0, duration = .2) + Animation(size_hint_y=0, height=(kivy.metrics.sp(0)), duration = .3)
        animation.start(instance)
    pass

class PairSetting(GridLayout):
    pass

class UIDSetting(GridLayout):
    pass

class RefreshSettings(Screen):
    pass

class SettingsWindow(Screen):
    def on_pre_enter(self):
        self.ids.settingFields.clear_widgets()
        uidField = UIDSetting(size_hint_y=None, height='60sp')
        uidField.ids.uid.text = config.uid
        pairedField = PairSetting(size_hint_y=None, height='50sp')
        if(config.paireduid.isdigit()):
            pairedField.ids.paired.text = config.pairedName
        self.ids.settingFields.add_widget(uidField)
        self.ids.settingFields.add_widget(pairedField)

    def updatePaired(self):
        pairedPopUp()
    pass

class UpdatePaired(Popup):
    def paired(self, code):
        if len(code) > 7:
            try:
                config.result = HoneyDooSQL.getUser(config.mydb, code)
                con.read('config.ini')
                con['PARTNER'] = {}
                con['PARTNER']['name'] = config.result
                con['PARTNER']['uid'] = code
                config.pairedName = config.result
                config.paireduid = code
                HoneyDooSQL.updatePaired(config.mydb, code)
                with open('config.ini','w') as configfile:
                    con.write(configfile)
                config.result = code
                return 'refreshSettings'
            except:
                config.result = 'User Not Found'
        else:
            if code == '0':
                HoneyDooSQL.unPair(config.mydb)
                con.read('config.ini')
                con.remove_section('PARTNER')
                with open('config.ini','w') as configfile:
                    con.write(configfile)
                config.pairedName = ''
                config.paireduid = ''
                return 'refreshSettings'
            else:
                config.result = 'Invalid User Pairing Code'

        if (config.result.isdigit()):
            return 'main'
        else:
            global dataError
            dataError = DataError()
            errorPopUp(config.result)
            return 'customSettings'
    pass

def pairedPopUp():
    window = UpdatePaired(
        title = "Pair New User",
        title_color = (.4, 1, .7, 1),
        title_size = '28sp', 
        separator_color = (0, .4, .2, 1),
        background_color = (0, .4, .2, .5),
        size_hint = (None, None), 
        size = ('350sp', '150sp'))
    window.open()
    pass


class TaskList(Screen):

    def on_pre_enter(self):
        self.ids.tasks.clear_widgets()
        self.ids.topLabel.text = 'Please Wait...'
        try:
            c = config.mydb.cursor(buffered=True)
            c.reset()
        except:
            config.mydb = HoneyDooSQL.dbSetup()

        config.task = HoneyDooSQL.readAllTasks(config.mydb)

    def on_enter(self):

        i = 0
        for task in config.task:
            btn = TaskItem(size_hint_y=None, height='100sp')

            priorityText = '[color=66ffb3][u]PRIORITY[/u][/color]\n' + '[b]'+checkPriority(task['PRIORITY'])+'[/b]'
            statusText = '[color=66ffb3][u]STATUS[/u][/color]\n' + '[b]'+checkStatus(task['STATUS'])+'[/b]'
            priorityColor = setPriorityColor(task['PRIORITY'])
            statusColor = setStatusColor(task['STATUS'])

            if task['STATUS'] == 1:
                dateStatus = 'DATE CREATED: ' + str(task['DATE_CREATED'])
            else:
                dateStatus = 'DATE COMPLETED: ' + str(task['DATE_COMPLETED'])

            descriptionText = (
                '[u]DESCRIPTION[/u]\n' + task['DESCRIPTION'] +
                '\n\n' + 'ASSIGNED TO: ' + HoneyDooSQL.getUser(config.mydb, task['UID']) +
                '\n' + dateStatus)

            self.ids[str(task['TASK_ID'])] = btn 
            btn.ids.task_name.text = str(task['TASK_NAME'])
            btn.ids.priority.color = priorityColor
            btn.ids.priority.text = priorityText
            btn.ids.status.color = statusColor
            btn.ids.status.text = statusText
            btn.ids.dropdown.text = descriptionText
            btn.ids.dropdown.opacity = 0
            self.ids.tasks.add_widget(btn)
            i += 1
        self.ids.topLabel.text = 'Full Task List'
    pass


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
            smtpObj.login(sender, 'NOTREALEMAILPASS')
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
        global dataError
        if (config.result.isdigit()):
            con['USER'] = {}
            con['USER']['uid'] = config.result
            con['USER']['email'] = config.email.upper()
            con['USER']['name'] = config.name.upper()
            if (config.paireduid.isdigit()):
                try:
                    config.pairedName = HoneyDooSQL.getUser(config.mydb, config.paireduid)
                    con['PARTNER'] = {}
                    con['PARTNER']['uid'] = config.paireduid
                    con['PARTNER']['name'] = config.pairedName.upper()
                except:
                    config.result = 'Failed to get Paired User'
                    dataError = DataError()
                    errorPopUp(config.result)

            with open('config.ini','w') as configfile:
                con.write(configfile)
            return 'main'
        else:
            dataError = DataError()
            errorPopUp(config.result)
            return 'sign'
    pass

class Register(Screen):

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

class EditTask(Screen):
    def on_pre_enter(self):
        print(config.displayTask)
        self.ids.header.text = 'PLEASE WAIT...'
        self.ids.assigned.text = 'NO ASSIGNEE'
        self.ids.task_name.text = ''
        self.ids.description.text = ''
        self.ids.priority.text = 'NO PRIORITY'
        if config.displayTask == 0:
            self.ids.header.text = 'UPDATE TASK'
        else:
            try:
                c = config.mydb.cursor(buffered=True)
                c.reset()
            except:
                config.mydb = HoneyDooSQL.dbSetup()
            task = HoneyDooSQL.readOneTask(config.mydb)
            self.ids.assigned.text = HoneyDooSQL.getUser(config.mydb, task[0]['UID'])
            self.ids.task_name.text = task[0]['TASK_NAME']
            self.ids.description.text = task[0]['DESCRIPTION']
            self.ids.priority.text = checkPriority(task[0]['PRIORITY'])
            self.ids.header.text = 'UPDATE TASK'

    def submitTask(self, task_name, description, priority):

        try:
            c = config.mydb.cursor(buffered=True)
            c.reset()
        except:
            config.mydb = HoneyDooSQL.dbSetup()

        try:
            priority = self.ids.priority.values.index(priority)
        except:
            priority = -1

        if (
            task_name == ''
            or
            description == ''
            or
            priority == -1):
            result = 'Please fill out all fields'
        else:
            if config.displayTask == 0:
                result = 'No task selected. Please go back and select a task.'
            else:
                result = HoneyDooSQL.updateTask(config.mydb, task_name, description, priority, config.displayTask)
        if result == '':
            return 'main'
        else:
            global dataError
            dataError = DataError()
            errorPopUp(result)
            return 'editTask'
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
