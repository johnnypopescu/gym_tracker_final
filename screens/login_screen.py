from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.app import App
from database.db_manager import validate_login

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        layout.add_widget(Label(text="🔐 LOGIN", font_size=32, bold=True, font_name='seguiemj.ttf', color=(0.2, 0.6, 0.8, 1)))
        
        self.username = TextInput(hint_text="Username", multiline=False, size_hint_y=None, height=50)
        self.password = TextInput(hint_text="Parola", password=True, multiline=False, size_hint_y=None, height=50)
        self.status = Label(text="", color=(1, 0, 0, 1))

        btn_login = Button(text="Intră în cont", size_hint_y=None, height=50, background_normal='', background_color=(0, 0.8, 0.4, 1), bold=True)
        btn_login.bind(on_press=self.do_login)
        
        btn_register = Button(text="Nu ai cont? Înregistrează-te", size_hint_y=None, height=50, background_normal='', background_color=(0.2, 0.2, 0.2, 1))
        btn_register.bind(on_press=self.go_to_register)

        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(btn_login)
        layout.add_widget(btn_register)
        layout.add_widget(self.status)
        
        self.add_widget(layout)

    def do_login(self, instance):
        user = self.username.text.strip()
        pwd = self.password.text.strip()
        
        user_id = validate_login(user, pwd)
        
        if user_id:
            # Salvăm ID-ul utilizatorului în aplicație ca să știm cine e logat
            App.get_running_app().current_user_id = user_id
            self.manager.current = 'add'
            self.status.text = ""
            self.password.text = "" # Curățăm parola
        else:
            self.status.text = "Username sau parolă incorectă!"

    def go_to_register(self, instance):
        self.manager.current = 'register'