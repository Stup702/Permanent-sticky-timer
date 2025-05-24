#!/usr/bin/env python3

import tkinter as tk
from tkinter import simpledialog
import os
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Subject list
SUBJECTS = ["Electrical Circuits", "Statistics", "Integral Cal", "Physics", "Pulse Techniques"]
LOG_FILE = "study_log.json"

# Initialize logs
study_log = {subject: 0 for subject in SUBJECTS}
monthly_log = {subject: 0 for subject in SUBJECTS}

# Flags
monthly_popup_shown = False

def load_logs():
    global study_log, monthly_log
    try:
        with open(LOG_FILE, 'r') as f:
            data = json.load(f)
            if data['reset_day'] != datetime.now().strftime('%Y-%m-%d'):
                week_day = datetime.now().weekday()
                if week_day == 4:  # Friday
                    data['weekly'] = {subject: 0 for subject in SUBJECTS}
                    data['reset_day'] = datetime.now().strftime('%Y-%m-%d')
            study_log.update(data.get('weekly', {}))
            monthly_log.update(data.get('monthly', {}))
    except FileNotFoundError:
        pass

def save_logs():
    with open(LOG_FILE, 'w') as f:
        json.dump({
            'weekly': study_log,
            'monthly': monthly_log,
            'reset_day': datetime.now().strftime('%Y-%m-%d')
        }, f)

load_logs()

# Main root window
root = tk.Tk()
root.title("Sticky Timer")
root.attributes("-topmost", True)
root.geometry("200x100+1000+50")
root.resizable(False, False)

label = tk.Label(root, font=('Helvetica', 30), fg='white', bg='black')
label.pack(expand=True, fill='both')

# Graph window (not sticky)
graph_root = tk.Toplevel(root)
graph_root.title("Study Stats")
graph_root.geometry("400x300+600+50")
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

def show_monthly_popup():
    global monthly_popup_shown
    if monthly_popup_shown:
        return
    monthly_popup_shown = True
    popup = tk.Toplevel(root)
    popup.title("Monthly Stats")
    popup.geometry("300x300+800+300")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)

    tk.Label(popup, text="Monthly Study Time", font=('Helvetica', 14, 'bold')).pack(pady=10)
    for subject in SUBJECTS:
        mins = monthly_log.get(subject, 0)
        tk.Label(popup, text=f"{subject}: {mins} min", font=('Helvetica', 12)).pack(anchor='w', padx=20)

    tk.Button(popup, text="OK", command=popup.destroy).pack(pady=10)

def update_graph():
    ax.clear()
    ax.set_title("Weekly Study Time Table")
    ax.axis('off')
    table_data = [[subject, f"{study_log.get(subject, 0) // 60}h {study_log.get(subject, 0) % 60}m"] for subject in SUBJECTS]
    table = ax.table(cellText=table_data, colLabels=["Subject", "Minutes"], loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)
    fig.tight_layout()
    canvas.draw()
    graph_root.after(10000, update_graph)  # Update graph every 10 seconds

def countdown(duration):
    def update(count):
        global reminder_after_id, start_time
        mins, secs = divmod(count, 60)
        timer_display = f'{mins:02}:{secs:02}'
        label.config(text=timer_display)
        if count > 0:
            root.after(1000, update, count - 1)
        else:
            label.config(text="Time’s up")
            os.system("paplay /home/stup/Music/timer_done.wav")
            global timer_started
            timer_started = False
            end_time = datetime.now()
            if current_subject and start_time:
                duration_minutes = (end_time - start_time).total_seconds() / 60
                minutes = round(duration_minutes)
                study_log[current_subject] += minutes
                monthly_log[current_subject] += minutes
                save_logs()
            reminder_after_id = root.after(5000, reminder)
    update(duration)

def reminder():
    global reminder_after_id, input_win, reminder_popup
    if not timer_started:
        if reminder_popup and reminder_popup.winfo_exists():
            reminder_popup.destroy()

        os.system("paplay /home/stup/Music/timer_set.wav")
        reminder_popup = tk.Toplevel(root)
        reminder_popup.title("Friendly Reminder \U0001F640")
        reminder_popup.attributes("-topmost", True)
        reminder_popup.geometry("220x70+1000+400")
        tk.Label(reminder_popup, text="You haven’t set a timer yet...", font=('Helvetica', 11)).pack(pady=10)
        tk.Button(reminder_popup, text="OK", command=reminder_popup.destroy).pack()
        reminder_after_id = root.after(5000, reminder)
        show_subject_selection()

def show_subject_selection():
    global input_win
    if input_win and input_win.winfo_exists():
        input_win.destroy()

    input_win = tk.Toplevel(root)
    input_win.title("Choose Subject")
    input_win.attributes("-topmost", True)
    input_win.geometry("300x300+950+200")
    input_win.resizable(False, False)

    tk.Label(input_win, text="What subject are you studying?", font=('Helvetica', 12)).pack(pady=10)

    for subject in SUBJECTS:
        tk.Button(input_win, text=subject, width=20, 
                  command=lambda s=subject: ask_duration(s)).pack(pady=2)

def ask_duration(subject):
    global current_subject, input_win, start_time
    current_subject = subject
    if input_win and input_win.winfo_exists():
        input_win.destroy()

    input_win = tk.Toplevel(root)
    input_win.title("Timer Setup")
    input_win.attributes("-topmost", True)
    input_win.geometry("250x100+950+200")
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
                input_win.destroy()
                root.destroy()
        except ValueError:
            entry.delete(0, tk.END)
            entry.insert(0, "\U0001F644")

    tk.Button(input_win, text="Start", command=submit).pack()
    input_win.bind('<Return>', lambda event: submit())

show_subject_selection()
show_monthly_popup()
update_graph()
root.mainloop()
