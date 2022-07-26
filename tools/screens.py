from kivy.uix.screenmanager import Screen
import tools.config as config
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
import tools.checkSave as checkSave
import tools.HoneyDooSQL as HoneyDooSQL
from kivy.app import App
from configparser import ConfigParser

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
            result = 'Please fill out all fields'
        else:
            if psswd == psswd2:
                result = HoneyDooSQL.registerUser(config.mydb, name, email, psswd)
            else:
                result = 'Passwords Do Not Match' 

        if (result.isdigit()):
            con['USER'] = {}
            con['USER']['uid'] = result
            con['USER']['email'] = email.upper()
            con['USER']['name'] = name.upper()
            con['USER']['psswd'] = psswd
            with open('config.ini','w') as configfile:
                con.write(configfile)
            return 'main'
        else:
            global dataError
            dataError = DataError()
            errorPopUp(result)
            return 'register' 
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
