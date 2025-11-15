from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from database.db_manager import create_user

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        layout.add_widget(Label(text="📝 ÎNREGISTRARE", font_size=32, bold=True, font_name='seguiemj.ttf', color=(0.8, 0.4, 0.8, 1)))
        
        self.username = TextInput(hint_text="Alege Username", multiline=False, size_hint_y=None, height=50)
        self.password = TextInput(hint_text="Alege Parola", password=True, multiline=False, size_hint_y=None, height=50)
        self.status = Label(text="", color=(1, 1, 0, 1))

        btn_save = Button(text="Creează Cont", size_hint_y=None, height=50, background_normal='', background_color=(0, 0.8, 0.4, 1), bold=True)
        btn_save.bind(on_press=self.do_register)
        
        btn_back = Button(text="Înapoi la Login", size_hint_y=None, height=50, background_normal='', background_color=(0.5, 0.5, 0.5, 1))
        btn_back.bind(on_press=self.go_back)

        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(btn_save)
        layout.add_widget(btn_back)
        layout.add_widget(self.status)
        
        self.add_widget(layout)

    def do_register(self, instance):
        user = self.username.text.strip()
        pwd = self.password.text.strip()
        
        if not user or not pwd:
            self.status.text = "Completează toate câmpurile!"
            return

        success = create_user(user, pwd)
        if success:
            self.status.text = "Cont creat! Te poți loga."
            self.status.color = (0, 1, 0, 1)
        else:
            self.status.text = "Username-ul există deja."
            self.status.color = (1, 0, 0, 1)

    def go_back(self, instance):
        self.manager.current = 'login'