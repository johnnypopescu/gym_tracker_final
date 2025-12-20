# Gym Tracker

Aplicatie desktop pentru evidenta antrenamentelor de sala. Python + Kivy + SQLite.

## Ce face

- Autentificare cu cont (inregistrare + login)
- Adaugare exercitii cu greutate si numar de repetari
- Istoric pe luni/saptamani/zile
- Editare si stergere exercitii
- Grafic de progres pe fiecare exercitiu (ultimele 30 inregistrari)
- Date salvate local in SQLite

## Tech

- GUI: Kivy
- DB: SQLite
- Python 3.12+

## Structura

```
gym_tracker/
  main.py               # entry point + ScreenManager
  database/
    db_manager.py       # CRUD pe SQLite
  screens/
    login_screen.py
    register_screen.py
    add_screen.py
    history_screen.py
    progress_screen.py
```

## Rulare

```
pip install -r requirements.txt
python main.py
```

## Schema DB

- **users** - id, username, password
- **exercises** - id, user_id, workout_name, name, weight, reps, date

## Screenshots

![Overview](screenshots/overview.png)

De la stanga: login, adaugare antrenament, lista exercitii, grafic progres.
