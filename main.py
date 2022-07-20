from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from kivy.clock import Clock
import tools.checkSave as checkSave
import tools.HoneyDooSQL as HoneyDooSQL
from tools.screens import MainWindow, TaskList, Register, NewTask, Refresh
import tools.config as config
from time import sleep
from kivy.utils import platform

kv = Builder.load_file('honeydoolayout.kv')

def remove_splash_custom():
    if(platform == 'android'):
        from android import loadingscreen #type: ignore
        loadingscreen.hide_loading_screen()
    return

#Phone Layout
from kivy.core.window import Window
Window.clearcolor = (.4, 1, .7, 1)

#Window Definitions
#App Logo/Start Screen

class LoadWindow(Screen):
    def load(self):

        def windowAfterLoad():
            config.mydb = dbLoad()
            if config.mydb == None:
                Clock.schedule_once(lambda dt: remove_splash_custom())
                self.ids.connect_status.text = 'Unable to Connect'
                Clock.schedule_once(lambda dt: app.stop(), 7)#7 
            else:
                screens = [Register(), MainWindow(), TaskList(), NewTask(), Refresh()]
                for screen in screens:
                    wm.add_widget(screen)
                Clock.schedule_once(lambda dt: remove_splash_custom())
                self.ids.connect_status.text = 'The Honey-Do List App :)'
                Clock.schedule_once(lambda dt: next(self), 2)

        def dbLoad():
            try:
                config.mydb = HoneyDooSQL.dbSetup()
            except:
                config.mydb = None
            return config.mydb

        def next(self):
            wm.current = checkSave.startWindow()
            wm.transition = SlideTransition()
            return
        windowAfterLoad()

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.load(), 4)#4



#Baseclass window
class WindowManager(ScreenManager):
    pass

#Assign return value for App.Build()
wm = WindowManager(transition=FadeTransition())
wm.switch_to(LoadWindow())

class HoneyDoo(App):
    def build(self):
        return wm

if __name__ == '__main__':
    app = HoneyDoo()
    app.run()