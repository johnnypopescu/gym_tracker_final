from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.app import App
from database.db_manager import get_user_exercises, delete_last_exercise, delete_exercise_by_id, update_exercise
from datetime import datetime

# --- CLASĂ POPUP REPARATĂ (ACUM ARE EMOJI) ---
class EditPopup(Popup):
    def __init__(self, exercise_data, refresh_callback, **kwargs):
        super().__init__(**kwargs)
        # 1. Folosim fontul special și text fără diacritice pentru titlu
        self.title = "✏️ Modificare" 
        self.title_font = 'seguiemj.ttf' # <--- REPARAT
        self.size_hint = (0.8, 0.5)
        self.exercise_id = exercise_data[0]
        self.refresh_callback = refresh_callback

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Câmpuri de editare
        self.name_input = TextInput(text=exercise_data[2], multiline=False, hint_text="Nume")
        self.weight_input = TextInput(text=str(exercise_data[3]), multiline=False, input_filter='float', hint_text="Greutate")
        self.reps_input = TextInput(text=str(exercise_data[4]), multiline=False, input_filter='int', hint_text="Reps")

        # Butoane
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        # 2. Folosim fontul special și text fără diacritice pentru buton
        btn_save = Button(
            text="💾 Salvare", 
            background_color=(0, 0.8, 0.4, 1),
            font_name='seguiemj.ttf' # <--- REPARAT
        )
        btn_save.bind(on_press=self.save_changes)
        
        btn_cancel = Button(text="Anulare", background_color=(0.8, 0.2, 0.2, 1))
        btn_cancel.bind(on_press=self.dismiss)

        btn_layout.add_widget(btn_save)
        btn_layout.add_widget(btn_cancel)

        layout.add_widget(Label(text="Modifică detaliile:", size_hint_y=None, height=30))
        layout.add_widget(self.name_input)
        layout.add_widget(self.weight_input)
        layout.add_widget(self.reps_input)
        layout.add_widget(btn_layout)

        self.content = layout

    def save_changes(self, instance):
        new_name = self.name_input.text.strip()
        new_weight = self.weight_input.text.strip()
        new_reps = self.reps_input.text.strip()

        if new_name and new_weight and new_reps:
            try:
                update_exercise(self.exercise_id, new_name, float(new_weight), int(new_reps))
                self.dismiss()
                self.refresh_callback()
            except Exception as e:
                print(f"Eroare update: {e}")

# --- SCREEN PRINCIPAL ---
class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        
        self.view_mode = 'months' 
        self.selected_month_key = None
        self.selected_week_key = None
        self.selected_day_key = None
        self.grouped_data = {}

        self.title_label = Label(
            text="Istoric", 
            font_size=24, 
            bold=True, 
            size_hint_y=None, 
            height=50, 
            color=(0.2, 0.6, 0.8, 1),
            font_name='seguiemj.ttf'
        )

        self.scroll = ScrollView(size_hint=(1, 1))
        self.content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        
        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.scroll)

        bottom_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=60, spacing=10)
        
        self.btn_back = Button(
            text="⬅️ Înapoi",
            background_normal='',
            background_color=(0.2, 0.6, 0.8, 1),
            font_size=16,
            font_name='seguiemj.ttf'
        )
        self.btn_back.bind(on_press=self.handle_back)
        
        self.btn_delete = Button(
            text="🗑️ Șterge Ultima",
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),
            font_size=16,
            font_name='seguiemj.ttf'
        )
        self.btn_delete.bind(on_press=self.delete_last)

        bottom_layout.add_widget(self.btn_back)
        bottom_layout.add_widget(self.btn_delete)

        self.layout.add_widget(bottom_layout)
        self.add_widget(self.layout)

    def on_pre_enter(self):
        self.load_and_group_data()
        self.show_months()

    def load_and_group_data(self):
        user_id = App.get_running_app().current_user_id
        raw_exercises = get_user_exercises(user_id)
        
        self.grouped_data = {}
        nume_luni = ["", "Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie", 
                     "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"]
        zile_sapt = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"]

        for row in raw_exercises:
            workout_name = row[1]
            date_str = row[5]
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            
            month_key = f"{nume_luni[dt.month]} {dt.year}"
            week_key = f"Săptămâna {dt.isocalendar()[1]}"
            day_key = date_str 
            day_name = zile_sapt[dt.weekday()]
            pretty_day_label = f"{day_name}, {dt.day} {nume_luni[dt.month][:3]} - {workout_name}"

            if month_key not in self.grouped_data:
                self.grouped_data[month_key] = {}
            if week_key not in self.grouped_data[month_key]:
                self.grouped_data[month_key][week_key] = {}
            if day_key not in self.grouped_data[month_key][week_key]:
                self.grouped_data[month_key][week_key][day_key] = {
                    "label": pretty_day_label,
                    "exercises": []
                }
            self.grouped_data[month_key][week_key][day_key]["exercises"].append(row)

    def show_months(self):
        self.view_mode = 'months'
        self.title_label.text = "📅 Alege Luna"
        self.content.clear_widgets()
        
        if not self.grouped_data:
            self.content.add_widget(Label(text="Nu ai antrenamente încă.", color=(0.7,0.7,0.7,1)))
            return

        for month_key in self.grouped_data.keys():
            btn = Button(
                text=month_key, 
                size_hint_y=None, height=60, 
                background_normal='', background_color=(0.15, 0.15, 0.15, 1), 
                font_size=18, bold=True
            )
            btn.bind(on_press=lambda instance, m=month_key: self.show_weeks(m))
            self.content.add_widget(btn)

    def show_weeks(self, month_key):
        self.view_mode = 'weeks'
        self.selected_month_key = month_key
        self.title_label.text = f"📂 {month_key}" 
        self.content.clear_widgets()

        weeks = self.grouped_data[month_key]
        for week_key in sorted(weeks.keys(), reverse=True):
            btn = Button(
                text=week_key, 
                size_hint_y=None, height=60, 
                background_normal='', background_color=(0.2, 0.2, 0.2, 1), 
                font_size=16
            )
            btn.bind(on_press=lambda instance, w=week_key: self.show_days(w))
            self.content.add_widget(btn)

    def show_days(self, week_key):
        self.view_mode = 'days'
        self.selected_week_key = week_key
        self.title_label.text = f"📆 {week_key}"
        self.content.clear_widgets()

        days_dict = self.grouped_data[self.selected_month_key][week_key]
        
        for day_key in sorted(days_dict.keys(), reverse=True):
            day_data = days_dict[day_key]
            label_text = day_data["label"] 
            
            btn = Button(
                text=label_text, 
                size_hint_y=None, height=60, 
                background_normal='', background_color=(0.25, 0.25, 0.25, 1), 
                font_size=16
            )
            btn.bind(on_press=lambda instance, d=day_key: self.show_exercises(d))
            self.content.add_widget(btn)

    def show_exercises(self, day_key):
        self.view_mode = 'exercises'
        self.selected_day_key = day_key
        
        day_data = self.grouped_data[self.selected_month_key][self.selected_week_key][day_key]
        full_label = day_data["label"]
        workout_name = full_label.split("-")[-1].strip()
        self.title_label.text = f"💪 {workout_name}"
        
        self.content.clear_widgets()

        exercises = day_data["exercises"]
        for row in exercises:
            ex_id = row[0]
            name = row[2]
            weight = row[3]
            reps = row[4]
            
            row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=5)
            
            item_text = f"[b][color=#00CC66]{name}[/color][/b]\n{weight}kg x {reps} reps"
            
            lbl = Label(
                text=item_text, markup=True, 
                size_hint_x=0.6, 
                font_size=16, 
                halign='left', valign='middle'
            )
            lbl.bind(size=lbl.setter('text_size'))
            
            # 3. Font emoji pentru butoanele de acțiune
            btn_edit = Button(
                text="✏️", 
                size_hint_x=0.2, 
                background_normal='', 
                background_color=(0.2, 0.6, 0.8, 1), 
                font_name='seguiemj.ttf' # <--- IMPORTANT
            )
            btn_edit.bind(on_press=lambda instance, r=row: self.open_edit_popup(r))

            btn_del = Button(
                text="❌", 
                size_hint_x=0.2, 
                background_normal='', 
                background_color=(0.8, 0.2, 0.2, 1), 
                font_name='seguiemj.ttf' # <--- IMPORTANT
            )
            btn_del.bind(on_press=lambda instance, x=ex_id: self.delete_specific_exercise(x))
            
            row_layout.add_widget(lbl)
            row_layout.add_widget(btn_edit)
            row_layout.add_widget(btn_del)
            
            self.content.add_widget(row_layout)

    def open_edit_popup(self, exercise_data):
        popup = EditPopup(exercise_data, refresh_callback=lambda: self.show_exercises(self.selected_day_key))
        popup.open()

    def delete_specific_exercise(self, ex_id):
        delete_exercise_by_id(ex_id)
        self.load_and_group_data()
        try:
            day_exists = (self.selected_month_key in self.grouped_data and 
                          self.selected_week_key in self.grouped_data[self.selected_month_key] and
                          self.selected_day_key in self.grouped_data[self.selected_month_key][self.selected_week_key])
            if day_exists:
                self.show_exercises(self.selected_day_key)
            else:
                self.show_days(self.selected_week_key)
        except Exception as e:
            self.show_months()

    def handle_back(self, instance):
        if self.view_mode == 'exercises':
            self.show_days(self.selected_week_key)
        elif self.view_mode == 'days':
            self.show_weeks(self.selected_month_key)
        elif self.view_mode == 'weeks':
            self.show_months()
        else:
            self.manager.current = "add"

    def delete_last(self, instance):
        user_id = App.get_running_app().current_user_id
        try:
            delete_last_exercise(user_id)
            self.load_and_group_data()
            if self.view_mode == 'exercises':
                try: self.show_exercises(self.selected_day_key)
                except: self.show_days(self.selected_week_key)
            elif self.view_mode == 'days':
                self.show_days(self.selected_week_key)
            else:
                self.show_months()
        except Exception as e:
            print(f"Eroare: {e}")