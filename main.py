from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from database.db_manager import init_db
from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.add_screen import AddScreen
from screens.history_screen import HistoryScreen
from screens.progress_screen import ProgressScreen # <--- IMPORT NOU

class GymApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        Window.size = (400, 600)
        self.current_user_id = None
        init_db()

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(AddScreen(name="add"))
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(ProgressScreen(name="progress")) # <--- ECRAN NOU
        return sm

if __name__ == "__main__":
    GymApp().run()