from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from kivy.clock import Clock
import tools.checkSave as checkSave
import tools.HoneyDooSQL as HoneyDooSQL
from tools.screens import MainWindow, TaskList, Register, NewTask
import tools.config as config
from time import sleep
from kivy.utils import platform

kv = Builder.load_file('honeydoo.kv')

def remove_splash_custom():
    if(platform == 'android'):
        from android import loadingscreen
        loadingscreen.hide_loading_screen()
    return

#### Copy everything between here

#Phone Layout
from kivy.core.window import Window
#Window.size = (360, 740)
Window.clearcolor = (.4, 1, .7, 1)

#Window Definitions
#App Logo/Start Screen

class LoadWindow(Screen):
    def load(self):
        Clock.schedule_once(lambda dt: remove_splash_custom())
        def windowAfterLoad():

            config.mydb = dbLoad()
            if config.mydb == None:
                self.ids.connect_status.text = 'Unable to Connect'
                Clock.schedule_once(lambda dt: app.stop(), 7)#7 
                return
            else:
                screens = [Register(), MainWindow(), TaskList(), NewTask()]
                for screen in screens:
                    wm.add_widget(screen)
                self.ids.connect_status.text = 'Connected'
                
                Clock.schedule_once(lambda dt: next(self), 2)

        def dbLoad():
            try:
                config.mydb = HoneyDooSQL.dbSetup()
            except:
                config.mydb = None #Cannot Connect to Database, close app
            return config.mydb

        def connected(self):
            next(self)

        def next(self):
            wm.current = checkSave.startWindow()
            wm.transition = SlideTransition()
            return
        Clock.schedule_once(lambda dt: windowAfterLoad(), -1)

    def on_pre_enter(self):
        self.ids.connect_status.text = 'Connecting...'

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.load(), 4)#4
        



#Baseclass window
class WindowManager(ScreenManager):
    pass

#Assign return value for App.Build()
wm = WindowManager(transition=FadeTransition())
wm.switch_to(LoadWindow())


#### and here

class HoneyDoo(App):
    def build(self):
        return wm

if __name__ == '__main__':
    app = HoneyDoo()
    app.run()