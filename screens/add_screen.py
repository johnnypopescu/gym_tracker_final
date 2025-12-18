from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.dropdown import DropDown
from kivy.app import App
from database.db_manager import add_exercise, get_unique_exercise_names

class AddScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=40, spacing=15)

        # Header
        header = BoxLayout(size_hint_y=None, height=40)
        
        # Titlu
        header.add_widget(Label(
            text="🏋️ GYM TRACKER", 
            bold=True, 
            color=(0, 0.8, 0.4, 1), 
            font_name='seguiemj.ttf'
        ))
        
        # Buton Logout (Actualizat: BOLD + Emoji nou)
        btn_logout = Button(
            text="🔐 Iesi",  # Am schimbat lacătul
            size_hint_x=None, 
            width=80, 
            bold=True,  # <--- AM ADĂUGAT BOLD
            background_normal='', 
            background_color=(0.3, 0.3, 0.3, 1),
            font_name='seguiemj.ttf' 
        )
        btn_logout.bind(on_press=self.logout)
        header.add_widget(btn_logout)
        
        layout.add_widget(header)

        # 1. Nume Antrenament
        layout.add_widget(Label(text="Ce antrenezi azi?", size_hint_y=None, height=30, color=(0.7, 0.7, 0.7, 1)))
        self.workout_name_input = TextInput(hint_text="Ex: Piept...", multiline=False, size_hint_y=None, height=45, font_size=16)
        layout.add_widget(self.workout_name_input)

        layout.add_widget(Label(size_hint_y=None, height=10))

        # 2. Date + Autocomplete
        self.dropdown = DropDown()
        self.is_suggestion_selected = False
        
        self.exercise = TextInput(hint_text="Nume Exercițiu", multiline=False, size_hint_y=None, height=45, font_size=16)
        self.exercise.bind(text=self.on_text_change)
        
        self.weight = TextInput(hint_text="Greutate (kg)", multiline=False, input_filter='float', size_hint_y=None, height=45, font_size=16)
        self.reps = TextInput(hint_text="Nr. Repetări", multiline=False, input_filter='int', size_hint_y=None, height=45, font_size=16)
        self.status = Label(text="", font_size=14, color=(1, 1, 0, 1), font_name='seguiemj.ttf')

        # --- BUTOANE DE ACȚIUNE ---
        btn_add = Button(text="💾 SALVEAZĂ", size_hint_y=None, height=55, background_normal='', background_color=(0, 0.8, 0.4, 1), font_size=16, bold=True, font_name='seguiemj.ttf')
        btn_add.bind(on_press=self.save_exercise)

        # Layout orizontal pentru butoanele de navigare
        nav_layout = BoxLayout(size_hint_y=None, height=55, spacing=10)
        
        btn_history = Button(text="📋 ISTORIC", background_normal='', background_color=(0.2, 0.6, 0.8, 1), font_size=14, bold=True, font_name='seguiemj.ttf')
        btn_history.bind(on_press=self.go_to_history)
        
        btn_progress = Button(text="📈 PROGRES", background_normal='', background_color=(0.6, 0.2, 0.8, 1), font_size=14, bold=True, font_name='seguiemj.ttf')
        btn_progress.bind(on_press=self.go_to_progress)

        nav_layout.add_widget(btn_history)
        nav_layout.add_widget(btn_progress)

        layout.add_widget(self.exercise)
        layout.add_widget(self.weight)
        layout.add_widget(self.reps)
        layout.add_widget(Label(size_hint_y=0.1))
        layout.add_widget(btn_add)
        layout.add_widget(nav_layout)
        layout.add_widget(self.status)

        self.add_widget(layout)

    def on_text_change(self, instance, text):
        if self.is_suggestion_selected or not text:
            self.dropdown.dismiss()
            return
        
        user_id = App.get_running_app().current_user_id
        if not user_id: return
        all_names = get_unique_exercise_names(user_id)
        matches = [name for name in all_names if text.lower() in name.lower()]
        
        if not matches:
            self.dropdown.dismiss()
            return

        self.dropdown.clear_widgets()
        for name in matches:
            btn = Button(text=name, size_hint_y=None, height=40, background_normal='', background_color=(0.25, 0.25, 0.25, 1))
            btn.bind(on_release=lambda btn: self.select_suggestion(btn.text))
            self.dropdown.add_widget(btn)
        try: self.dropdown.open(self.exercise)
        except: pass

    def select_suggestion(self, text):
        self.is_suggestion_selected = True
        self.exercise.text = text
        self.dropdown.dismiss()
        self.weight.focus = True

    def logout(self, instance):
        App.get_running_app().current_user_id = None
        self.manager.current = 'login'

    def go_to_history(self, instance):
        self.manager.current = "history"

    def go_to_progress(self, instance):
        self.manager.current = "progress"

    def save_exercise(self, instance):
        w_name = self.workout_name_input.text.strip()
        ex = self.exercise.text.strip()
        wt = self.weight.text.strip()
        rp = self.reps.text.strip()
        user_id = App.get_running_app().current_user_id 

        if not ex or not wt:
            self.status.text = "⚠️ Date incomplete!"
            return

        try:
            add_exercise(user_id, w_name, ex, float(wt), int(rp) if rp else 0)
            self.status.text = f"✅ Adăugat!"
            self.exercise.text = ""
            self.weight.text = ""
            self.reps.text = ""
            self.exercise.focus = True 
        except Exception as e:
            self.status.text = f"❌ Eroare: {e}"