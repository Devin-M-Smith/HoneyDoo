from kivy.uix.screenmanager import Screen
import tools.config as config
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
import tools.checkSave as checkSave
import tools.HoneyDooSQL as HoneyDooSQL
from kivy.app import App


app = App.get_running_app()


class Refresh(Screen):
    pass

#Main Display, Task Bar and tasks ----Moved to separate Module
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

#Full Task List
class TaskList(Screen):
    pass

#Registration Form for New User
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
    pass


#New Task Screen
class NewTask(Screen):

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

        if (
            task_name == ''
            or
            description == ''
            or
            priority == -1):
            result = 'Please fill out all fields'
        else:
            result = HoneyDooSQL.writeTask(config.mydb, user, task_name, description, priority)

        if result == '':
            pass
            return 'main'
        else:
            global dataError
            dataError = DataError()
            errorPopUp(result)
            return 'addTask'
    pass
        
class DataError(FloatLayout): #Data entry Error Popup
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
