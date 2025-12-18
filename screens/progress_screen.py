from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.metrics import dp
from database.db_manager import get_unique_exercise_names, get_exercise_history

class ProgressScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Layout principal
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 1. Titlu
        layout.add_widget(Label(
            text="📈 Grafic Progres", 
            font_size=24, bold=True, 
            size_hint_y=None, height=50,
            color=(0.2, 0.6, 0.8, 1),
            font_name='seguiemj.ttf'
        ))

        # 2. Selector Exercițiu (DropDown)
        self.btn_select = Button(
            text="👇 Alege un exercițiu",
            size_hint_y=None, height=50,
            background_normal='',
            background_color=(0.25, 0.25, 0.25, 1),
            font_name='seguiemj.ttf'
        )
        self.btn_select.bind(on_release=self.open_dropdown)
        
        self.dropdown = DropDown()
        layout.add_widget(self.btn_select)

        # 3. Zona Graficului (Scroll Orizontal)
        # Graficul va fi într-un ScrollView ca să putem da swipe dacă avem multe date
        chart_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=True, do_scroll_y=False)
        
        # Containerul pentru bare (se lățește cât e nevoie)
        self.chart_container = BoxLayout(
            orientation='horizontal', 
            size_hint_x=None, 
            padding=[10, 50, 10, 10], # Padding sus mai mare pentru text
            spacing=15
        )
        self.chart_container.bind(minimum_width=self.chart_container.setter('width'))
        
        chart_scroll.add_widget(self.chart_container)
        layout.add_widget(chart_scroll)

        # 4. Buton Înapoi
        btn_back = Button(
            text="⬅️ Înapoi",
            size_hint_y=None, height=50,
            background_normal='',
            background_color=(0.5, 0.5, 0.5, 1),
            font_name='seguiemj.ttf'
        )
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def open_dropdown(self, instance):
        self.dropdown.clear_widgets()
        user_id = App.get_running_app().current_user_id
        names = get_unique_exercise_names(user_id)
        
        if not names:
            btn = Button(text="Nu ai exerciții salvate", size_hint_y=None, height=44)
            self.dropdown.add_widget(btn)
        
        for name in names:
            btn = Button(text=name, size_hint_y=None, height=44, background_color=(0.3, 0.3, 0.3, 1))
            btn.bind(on_release=lambda btn: self.select_exercise(btn.text))
            self.dropdown.add_widget(btn)
            
        self.dropdown.open(instance)

    def select_exercise(self, exercise_name):
        self.dropdown.dismiss()
        self.btn_select.text = f"📊 {exercise_name}"
        self.draw_chart(exercise_name)

    def draw_chart(self, exercise_name):
        self.chart_container.clear_widgets()
        user_id = App.get_running_app().current_user_id
        
        # Luăm datele: [(date, weight, reps), ...]
        history = get_exercise_history(user_id, exercise_name)
        
        if not history:
            return

        # Găsim greutatea maximă pentru a scala barele (cea mai înaltă bară = 100%)
        max_val = max([row[1] for row in history])
        
        # Desenăm fiecare bară
        for row in history:
            date_str = row[0]   # "2025-12-11"
            weight = row[1]     # 100.0
            reps = row[2]       # 10
            
            # Formatăm data să fie mai scurtă (zi/lună)
            short_date = date_str[5:] # Luăm de la caracterul 5 încolo (MM-DD)
            
            # Creăm o coloană verticală pentru o zi
            bar_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(60))
            
            # 1. Spațiu gol sus (invers proporțional cu greutatea)
            # Dacă greutatea e mică, spațiul gol e mare.
            fill_ratio = weight / max_val
            empty_ratio = 1.0 - fill_ratio
            
            if empty_ratio > 0:
                bar_layout.add_widget(Label(size_hint_y=empty_ratio))
            
            # 2. Eticheta cu Greutatea (deasupra barei)
            weight_label = Label(
                text=f"{int(weight)}kg", 
                size_hint_y=None, height=20, 
                font_size=12, bold=True,
                color=(0, 1, 0, 1) # Verde
            )
            bar_layout.add_widget(weight_label)

            # 3. BARA EFECTIVĂ (Buton colorat)
            # Facem bara mai verde dacă e greutate mare, mai albastră dacă e mică
            color = (0.2, fill_ratio, 0.8, 1) 
            
            bar = Button(
                text="", # Fără text pe bară
                background_normal='',
                background_color=color,
                size_hint_y=fill_ratio if fill_ratio > 0.1 else 0.1 # Minim 10% înălțime
            )
            bar_layout.add_widget(bar)
            
            # 4. Data jos
            date_lbl = Label(text=short_date, size_hint_y=None, height=20, font_size=10, color=(0.7,0.7,0.7,1))
            bar_layout.add_widget(date_lbl)
            
            self.chart_container.add_widget(bar_layout)

    def go_back(self, instance):
        self.manager.current = 'add'