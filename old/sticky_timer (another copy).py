#!/usr/bin/env python3

import tkinter as tk
from tkinter import simpledialog
import os
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

SUBJECTS = ["Electrical Circuits", "Programming", "Statistics", "Integral Cal", "Physics", "Pulse Techniques", "Break"]
LOG_FILE = "logs.json"

daily_log = {subject: 0 for subject in SUBJECTS}
study_log = {subject: 0 for subject in SUBJECTS}
monthly_log = {subject: 0 for subject in SUBJECTS}
last_weekly_reset = datetime.now().date()
last_monthly_reset = datetime.now().strftime('%Y-%m')
monthly_popup_shown = False
concentration_mode_active = False

def get_last_friday(date):
    weekday = date.weekday()
    days_since_friday = (weekday - 4) % 7
    last_friday = date - timedelta(days=days_since_friday)
    return last_friday

def load_logs():
    global daily_log, study_log, monthly_log, last_weekly_reset, last_monthly_reset
    try:
        with open(LOG_FILE, 'r') as f:
            data = json.load(f)
            print(f"Loaded data: {data}") 
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    today = datetime.now().date()
    current_month = today.strftime('%Y-%m')

    last_date_str = data.get('last_date', '')
    if last_date_str:
        try:
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d').date()
            if last_date == today:
                daily_log.update(data.get('daily', {}))
            else:
                daily_log = {subject: 0 for subject in SUBJECTS}
        except ValueError:
            daily_log = {subject: 0 for subject in SUBJECTS}
    else:
        daily_log = {subject: 0 for subject in SUBJECTS}
        print(f"daily_log: {daily_log}")

    last_friday = get_last_friday(today)
    last_weekly_reset_str = data.get('last_weekly_reset', '')
    if last_weekly_reset_str:
        try:
            last_weekly_reset = datetime.strptime(last_weekly_reset_str, '%Y-%m-%d').date()
            if last_weekly_reset < last_friday:
                study_log = {subject: 0 for subject in SUBJECTS}
                last_weekly_reset = last_friday
                print(f"Reset study_log, last_weekly_reset: {last_weekly_reset}")  # Debug
            else:
                study_log.update(data.get('weekly', {}))
                print(f"Loaded study_log: {study_log}")  # Debug
        except ValueError:
            study_log = {subject: 0 for subject in SUBJECTS}
            last_weekly_reset = last_friday
            print(f"Invalid last_weekly_reset, reset study_log, last_weekly_reset: {last_weekly_reset}")  # Debug

    else:
        study_log = {subject: 0 for subject in SUBJECTS}
        last_weekly_reset = last_friday

    last_monthly_reset_local = data.get('last_monthly_reset', current_month)
    if last_monthly_reset_local != current_month:
        monthly_log = {subject: 0 for subject in SUBJECTS}
        last_monthly_reset = current_month
        print(f"Reset monthly_log, last_monthly_reset: {last_monthly_reset}")  # Debug
    else:
        monthly_log.update(data.get('monthly', {}))
        last_monthly_reset = last_monthly_reset_local
        print(f"Loaded monthly_log: {monthly_log}")  # Debug

def save_logs():
    today = datetime.now().date()
    with open(LOG_FILE, 'w') as f:
        json.dump({
            'daily': daily_log,
            'weekly': study_log,
            'monthly': monthly_log,
            'last_date': today.strftime('%Y-%m-%d'),
            'last_weekly_reset': last_weekly_reset.strftime('%Y-%m-%d'),
            'last_monthly_reset': last_monthly_reset
        }, f)

load_logs()

root = tk.Tk()
root.title("Sticky Timer")
root.attributes("-topmost", True)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
main_width = int(screen_width * 0.12)
main_height = int(screen_height * 0.08)
root.geometry(f"{main_width}x{main_height}+{int(screen_width * 0.5 - main_width * 0.5)}+{int(screen_height * 0.1)}")
root.resizable(True, True)

label = tk.Label(root, font=('Helvetica', 30), fg='white', bg='black')
label.pack(expand=True, fill='both')

graph_root = tk.Toplevel(root)
graph_root.title("Study Stats")
graph_width = int(screen_width * 0.30)
graph_height = int(screen_height * 0.25)
graph_root.geometry(f"{graph_width}x{graph_height}+{int(screen_width * 0.35 - graph_width * 0.5)}+{int(screen_height * 0.1)}")
graph_root.resizable(False, False)

fig, ax = plt.subplots(figsize=(4, 3))
canvas = FigureCanvasTkAgg(fig, master=graph_root)
canvas.get_tk_widget().pack(fill="both", expand=True)

timer_started = False
reminder_after_id = None
input_win = None
reminder_popup = None
current_subject = None
start_time = None
stopwatch_running = False
stopwatch_stop_button = None
log_update_after_id = None

def show_monthly_popup():
    global monthly_popup_shown
    if monthly_popup_shown:
        return
    monthly_popup_shown = True
    popup = tk.Toplevel(root)
    popup.title("Monthly Stats")
    popup_width = int(screen_width * 0.25)
    popup_height = int(screen_height * 0.25)
    popup.geometry(f"{popup_width}x{popup_height}+{int(screen_width * 0.375 - popup_width * 0.5)}+{int(screen_height * 0.375)}")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)

    tk.Label(popup, text="Monthly Study Time", font=('Helvetica', 14, 'bold')).pack(pady=10)
    total_mins = 0
    for subject in SUBJECTS:
        mins = monthly_log.get(subject, 0)
        total_mins += mins
        tk.Label(popup, text=f"{subject}: {mins //60}:{mins%60:02d}", font=('Helvetica', 14)).pack(anchor='w', padx=20)
    break_time = monthly_log.get("Break", 0)
    total_mins -= break_time
    tk.Label(popup, text=f"Total: {total_mins //60}:{total_mins%60:02d}", font=('Helvetica', 14)).pack(anchor='w', padx=20)
    tk.Button(popup, text="OK", command=popup.destroy).pack(pady=10)

def update_graph():
    ax.clear()
    ax.set_title("Weekly Study Time Table")
    ax.axis('off')
    total_weekly = sum(study_log.get(subject, 0) for subject in SUBJECTS) - study_log.get("Break", 0)
    total_daily = sum(daily_log.get(subject, 0) for subject in SUBJECTS) - daily_log.get("Break", 0)
    table_data = [
        [subject,
         f"{study_log.get(subject, 0) // 60}:{study_log.get(subject, 0) % 60:02d}",
         f"{daily_log.get(subject, 0) // 60}:{daily_log.get(subject, 0) % 60:02d}"]
        for subject in SUBJECTS
    ]
    table_data.append([
        "Total",
        f"{total_weekly // 60}:{total_weekly % 60:02d}",
        f"{total_daily // 60}:{total_daily % 60:02d}"
    ])
    table = ax.table(cellText=table_data, colLabels=["Subject", "Weekly", "Today"], loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)
    fig.tight_layout()
    canvas.draw()
    graph_root.after(10000, update_graph)

def update_logs_periodically():
    global log_update_after_id
    if timer_started or stopwatch_running:
        log_update_after_id = root.after(60000, update_logs_periodically)
    else:
        log_update_after_id = None

def countdown(duration):
    def update(count):
        global reminder_after_id, start_time, timer_started
        timer_started = True
        if reminder_after_id is not None:
            root.after_cancel(reminder_after_id)

        mins, secs = divmod(count, 60)
        timer_display = f'{mins:02}:{secs:02}'
        label.config(text=timer_display)

        try:
            with open('/tmp/sticky_timer.txt', 'w') as f:
                json.dump({'time': timer_display, 'subject': current_subject}, f)
        except Exception as e:
            print(f"Failed to write timer state: {e}")

        if count > 0:
            root.after(1000, update, count - 1)
        else:
            label.config(text="Time’s up")
            timer_started = False
            end_time = datetime.now()
            if current_subject and start_time:
                duration_minutes = (end_time - start_time).total_seconds() / 60
                minutes = round(duration_minutes)
                daily_log[current_subject] = daily_log.get(current_subject, 0) + minutes
                study_log[current_subject] = study_log.get(current_subject, 0) + minutes
                monthly_log[current_subject] = monthly_log.get(current_subject, 0) + minutes
                save_logs()
            reminder_after_id = root.after(5000, reminder)
            try:
                with open('/tmp/sticky_timer.txt', 'w') as f:
                    json.dump({'time': '00:00', 'subject': ''}, f)
            except Exception as e:
                print(f"Failed to clear timer state: {e}")

    global log_update_after_id
    if log_update_after_id:
        root.after_cancel(log_update_after_id)
        log_update_after_id = None
    log_update_after_id = root.after(60000, update_logs_periodically)
    update(duration)

def stopwatch():
    global start_time, timer_started, stopwatch_running, stopwatch_stop_button, log_update_after_id, concentration_mode_active
    def update():
        if stopwatch_running:
            elapsed = datetime.now() - start_time
            total_seconds = int(elapsed.total_seconds())
            mins, secs = divmod(total_seconds, 60)
            timer_display = f"{mins:02d}:{secs:02d}"
            label.config(text=timer_display)
            try:
                with open('/tmp/sticky_timer.txt', 'w') as f:
                    json.dump({'time': timer_display, 'subject': current_subject}, f)
            except Exception as e:
                print(f"Failed to write stopwatch state: {e}")
            root.after(1000, update)

    timer_started = True
    stopwatch_running = True
    concentration_mode_active = True
    start_time = datetime.now()
    update()
    if stopwatch_stop_button and stopwatch_stop_button.winfo_exists():
        stopwatch_stop_button.destroy()
    stopwatch_stop_button = tk.Button(root, text="Stop", command=stop_stopwatch, font=('Helvetica', 12))
    stopwatch_stop_button.pack()
    if log_update_after_id:
        root.after_cancel(log_update_after_id)
        log_update_after_id = None
    log_update_after_id = root.after(60000, update_logs_periodically)

def stop_stopwatch():
    global timer_started, stopwatch_running, current_subject, start_time, reminder_after_id, stopwatch_stop_button, log_update_after_id, concentration_mode_active
    if stopwatch_running:
        stopwatch_running = False
        concentration_mode_active = False
        end_time = datetime.now()
        if current_subject and start_time:
            duration_minutes = (end_time - start_time).total_seconds() / 60
            minutes = round(duration_minutes)
            daily_log[current_subject] = daily_log.get(current_subject, 0) + minutes
            study_log[current_subject] = study_log.get(current_subject, 0) + minutes
            monthly_log[current_subject] = monthly_log.get(current_subject, 0) + minutes
            save_logs()
        label.config(text="Stopped")
        timer_started = False
        if stopwatch_stop_button:
            stopwatch_stop_button.destroy()
            stopwatch_stop_button = None
        if log_update_after_id:
            root.after_cancel(log_update_after_id)
            log_update_after_id = None
        reminder_after_id = root.after(5000, reminder)
        try:
            with open('/tmp/sticky_timer.txt', 'w') as f:
                json.dump({'time': '00:00', 'subject': ''}, f)
        except Exception as e:
            print(f"Failed to clear timer state: {e}")

def play_sound_if_popup_exists(popup):
    if popup and popup.winfo_exists():
        sound_path = os.path.join(os.path.dirname(__file__), "assets/timer_set.wav")
        os.system(f"paplay {sound_path}")

def reminder():
    global reminder_after_id, reminder_popup, timer_started, concentration_mode_active
    if not timer_started and not concentration_mode_active:
        if reminder_popup and reminder_popup.winfo_exists():
            reminder_popup.destroy()
        
        reminder_popup = tk.Toplevel(root)
        reminder_popup.title("Friendly Reminder \U0001F640")
        reminder_popup.attributes("-topmost", True)
        reminder_width = int(screen_width * 0.15)
        reminder_height = int(screen_height * 0.05)
        reminder_popup.geometry(f"{reminder_width}x{reminder_height}+{int(screen_width * 0.5 - reminder_width * 0.5)}+{int(screen_height * 0.45)}")

        tk.Label(reminder_popup, text="You haven’t set a timer yet...", font=('Helvetica', 11)).pack(pady=10)
        tk.Button(reminder_popup, text="OK", command=reminder_popup.destroy).pack()
        
        root.after(10000, play_sound_if_popup_exists, reminder_popup)
        reminder_after_id = root.after(10000, reminder)
        show_subject_selection()

def show_subject_selection():
    global input_win
    if input_win and input_win.winfo_exists():
        input_win.destroy()

    input_win = tk.Toplevel(root)
    input_win.title("Choose Subject")
    input_win.attributes("-topmost", True)
    input_width = int(screen_width * 0.25)
    input_height = int(screen_height * 0.25)
    input_win.geometry(f"{input_width}x{input_height}+{int(screen_width * 0.375 - input_width * 0.5)}+{int(screen_height * 0.375)}")
    input_win.resizable(False, False)

    tk.Label(input_win, text="What subject are you studying?", font=('Helvetica', 12)).pack(pady=10)
    for subject in SUBJECTS:
        tk.Button(input_win, text=subject, width=20, font=('Helvetica', 14), command=lambda s=subject: ask_duration(s)).pack(pady=2)

def ask_duration(subject):
    global current_subject, input_win, start_time
    current_subject = subject
    if input_win and input_win.winfo_exists():
        input_win.destroy()

    input_win = tk.Toplevel(root)
    input_win.title("Timer Setup")
    input_win.attributes("-topmost", True)
    setup_width = int(screen_width * 0.25)
    setup_height = int(screen_height * 0.15)
    input_win.geometry(f"{setup_width}x{setup_height}+{int(screen_width * 0.375 - setup_width * 0.5)}+{int(screen_height * 0.45)}")
    input_win.resizable(False, False)

    tk.Label(input_win, text=f"How many minutes for {subject}?", font=('Helvetica', 12)).pack(pady=5)
    entry = tk.Entry(input_win, font=('Helvetica', 14))
    entry.pack(pady=5)
    entry.focus()

    def submit():
        global timer_started, reminder_after_id, reminder_popup, start_time
        try:
            minutes = int(entry.get())
            if minutes > 0:
                timer_started = True
                start_time = datetime.now()
                input_win.destroy()
                if reminder_after_id:
                    root.after_cancel(reminder_after_id)
                    reminder_after_id = None
                if reminder_popup and reminder_popup.winfo_exists():
                    reminder_popup.destroy()
                countdown(minutes * 60)
            else:
                tk.Label(input_win, text="Please enter a positive number", fg="red").pack()
        except ValueError:
            entry.delete(0, tk.END)
            entry.insert(0, "\U0001F644")

    tk.Button(input_win, text="Start", command=submit).pack(pady=5)
    tk.Button(input_win, text="Concentration Mode", command=lambda: start_stopwatch(current_subject)).pack(pady=5)
    input_win.bind('<Return>', lambda event: submit())

def start_stopwatch(subject):
    global current_subject, input_win, timer_started, reminder_after_id, reminder_popup
    current_subject = subject
    if input_win and input_win.winfo_exists():
        input_win.destroy()
    if reminder_after_id:
        root.after_cancel(reminder_after_id)
        reminder_after_id = None
    if reminder_popup and reminder_popup.winfo_exists():
        reminder_popup.destroy()
    stopwatch()

def confirm_quit():
    if not timer_started and not stopwatch_running:
        root.destroy()
        return

    quit_win = tk.Toplevel(root)
    quit_win.title("Really Quit?")
    quit_win.attributes("-topmost", True)
    quit_width = int(screen_width * 0.25)
    quit_height = int(screen_height * 0.15)
    quit_win.geometry(f"{quit_width}x{quit_height}+{int(screen_width * 0.375 - quit_width * 0.5)}+{int(screen_height * 0.375)}")
    quit_win.resizable(False, False)

    required_sentence = "I am giving up on my study goals"
    tk.Label(quit_win, text=f"Type exactly: '{required_sentence}'", font=('Helvetica', 12)).pack(pady=10)
    entry = tk.Entry(quit_win, font=('Helvetica', 12), width=40)
    entry.pack(pady=5)
    entry.focus()

    def check_quit():
        if entry.get() == required_sentence:
            root.destroy()
        else:
            tk.Label(quit_win, text="Sentence doesn't match. Try again.", fg="red").pack()
            entry.delete(0, tk.END)

    tk.Button(quit_win, text="Quit", command=check_quit).pack(pady=5)
    quit_win.bind('<Return>', lambda event: check_quit())

root.protocol("WM_DELETE_WINDOW", confirm_quit)
graph_root.protocol("WM_DELETE_WINDOW", confirm_quit)

show_subject_selection()
show_monthly_popup()
update_graph()

root.after(5000, play_sound_if_popup_exists, reminder_popup)
reminder_after_id = root.after(5000, reminder)

root.mainloop()