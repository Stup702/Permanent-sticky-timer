#!/usr/bin/env python3

import tkinter as tk
from tkinter import simpledialog
import os
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Subject list
SUBJECTS = ["Electrical Circuits","Programming","Statistics", "Integral Cal", "Physics", "Pulse Techniques", "Break"]
LOG_FILE = "logs.json"

# Initialize logs
daily_log = {subject: 0 for subject in SUBJECTS}
study_log = {subject: 0 for subject in SUBJECTS}  # Weekly log
monthly_log = {subject: 0 for subject in SUBJECTS}
last_weekly_reset = ''  # Tracks the last weekly reset date
last_monthly_reset = ''  # Tracks the last monthly reset month
monthly_popup_shown = False
concentration_mode_active = False  # Flag for Concentration Mode

def load_logs():
    """Load and update logs from the JSON file with reset logic."""
    global daily_log, study_log, monthly_log, last_weekly_reset, last_monthly_reset
    try:
        with open(LOG_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    today = datetime.now().strftime('%Y-%m-%d')
    current_month = datetime.now().strftime('%Y-%m')

    # Daily reset
    last_date = data.get('last_date', '')
    if last_date == today:
        daily_log.update(data.get('daily', {}))
    else:
        daily_log = {subject: 0 for subject in SUBJECTS}

    # Weekly reset (every 7 days)
    last_weekly_reset_local = data.get('last_weekly_reset', '')
    if last_weekly_reset_local:
        try:
            last_reset_date = datetime.strptime(last_weekly_reset_local, '%Y-%m-%d')
            days_since_reset = (datetime.now() - last_reset_date).days
            if days_since_reset >= 7:
                study_log = {subject: 0 for subject in SUBJECTS}
                last_weekly_reset = today
                
            else:
                study_log.update(data.get('weekly', {}))
                last_weekly_reset = last_weekly_reset_local
        except ValueError:
            study_log = {subject: 0 for subject in SUBJECTS}
            last_weekly_reset = today
    else:
        study_log = {subject: 0 for subject in SUBJECTS}
        last_weekly_reset = today

    # Monthly reset (start of each month)
    last_monthly_reset_local = data.get('last_monthly_reset', '')
    if last_monthly_reset_local != current_month:
        monthly_log = {subject: 0 for subject in SUBJECTS}
        last_monthly_reset = current_month
    else:
        monthly_log.update(data.get('monthly', {}))
        last_monthly_reset = last_monthly_reset_local

def save_logs():
    """Save all logs and reset dates to the JSON file."""
    today = datetime.now().strftime('%Y-%m-%d')
    with open(LOG_FILE, 'w') as f:
        json.dump({
            'daily': daily_log,
            'weekly': study_log,
            'monthly': monthly_log,
            'last_date': today,
            'last_weekly_reset': last_weekly_reset,
            'last_monthly_reset': last_monthly_reset
        }, f)

# Load logs at startup
load_logs()

# Main root window
root = tk.Tk()
root.title("Sticky Timer")
root.attributes("-topmost", True)

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set main window size as 10% of screen width and 8% of screen height, centered
main_width = int(screen_width * 0.10)
main_height = int(screen_height * 0.08)
root.geometry(f"{main_width}x{main_height}+{int(screen_width * 0.5 - main_width * 0.5)}+{int(screen_height * 0.1)}")
root.resizable(False, False)

label = tk.Label(root, font=('Helvetica', 30), fg='white', bg='black')
label.pack(expand=True, fill='both')

# Graph window (weekly popup)
graph_root = tk.Toplevel(root)
graph_root.title("Study Stats")

# Set graph window size as 30% of screen width and 25% of screen height, centered
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
stopwatch_running = False  # Flag for stopwatch mode
stopwatch_stop_button = None  # Reference to stop button
log_update_after_id = None  # Track periodic log update

def show_monthly_popup():
    """Display the monthly study time popup."""
    global monthly_popup_shown
    if monthly_popup_shown:
        return
    monthly_popup_shown = True
    popup = tk.Toplevel(root)
    popup.title("Monthly Stats")

    # Set monthly popup size as 25% of screen width and 25% of screen height, centered
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
    """Update the weekly study time graph with daily, weekly, and total timers."""
    ax.clear()
    ax.set_title("Weekly Study Time Table")
    ax.axis('off')
    # Calculate totals
    total_weekly = sum(study_log.get(subject, 0) for subject in SUBJECTS) - study_log.get("Break", 0)
    total_daily = sum(daily_log.get(subject, 0) for subject in SUBJECTS) - daily_log.get("Break", 0)
    # Table data with subject rows plus a total row
    table_data = [
        [subject,
         f"{study_log.get(subject, 0) // 60}:{study_log.get(subject, 0) % 60:02d}",
         f"{daily_log.get(subject, 0) // 60}:{daily_log.get(subject, 0) % 60:02d}"]
        for subject in SUBJECTS
    ]
    # Append total row
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
    graph_root.after(10000, update_graph)  # Update every 10 seconds

def update_logs_periodically():
    """Update logs every minute while a timer or stopwatch is running."""
    global current_subject, timer_started, stopwatch_running, log_update_after_id
    if timer_started or stopwatch_running:
        if current_subject:
            daily_log[current_subject] += 1
            study_log[current_subject] += 1
            monthly_log[current_subject] += 1
            save_logs()
        log_update_after_id = root.after(60000, update_logs_periodically)
    else:
        log_update_after_id = None

def countdown(duration):
    """Run the countdown timer and update logs when finished."""
    def update(count):
        global reminder_after_id, start_time
        mins, secs = divmod(count, 60)
        timer_display = f'{mins:02}:{secs:02}'
        label.config(text=timer_display)
        if count > 0:
            root.after(1000, update, count - 1)
        else:
            label.config(text="Time’s up")
            sound_path = os.path.join(os.path.dirname(__file__), "assets/timer_done.wav")
            if not os.path.exists(sound_path):
                print(f"Sound file not found: {sound_path}")
            else:
                print(f"Attempting to play: {sound_path}")
                result = os.system(f"paplay {sound_path}")
                if result != 0:
                    print(f"Failed to play sound, exit status: {result}")
            global timer_started
            timer_started = False
            end_time = datetime.now()
            if current_subject and start_time:
                duration_minutes = (end_time - start_time).total_seconds() / 60
                minutes = round(duration_minutes)
                daily_log[current_subject] += minutes
                study_log[current_subject] += minutes
                monthly_log[current_subject] += minutes
                save_logs()
            reminder_after_id = root.after(5000, reminder)
    global log_update_after_id
    if log_update_after_id:
        root.after_cancel(log_update_after_id)
        log_update_after_id = None
    log_update_after_id = root.after(60000, update_logs_periodically)
    update(duration)

def stopwatch():
    """Run a stopwatch for the selected subject until stopped."""
    global start_time, timer_started, stopwatch_running, stopwatch_stop_button, log_update_after_id, concentration_mode_active
    def update():
        if stopwatch_running:
            elapsed = datetime.now() - start_time
            total_seconds = int(elapsed.total_seconds())
            mins, secs = divmod(total_seconds, 60)
            label.config(text=f"{mins:02d}:{secs:02d}")
            root.after(1000, update)

    # Start the stopwatch
    timer_started = True
    stopwatch_running = True
    concentration_mode_active = True  # Activate Concentration Mode
    start_time = datetime.now()
    update()

    # Create a stop button
    if stopwatch_stop_button and stopwatch_stop_button.winfo_exists():
        stopwatch_stop_button.destroy()
    stopwatch_stop_button = tk.Button(root, text="Stop", command=stop_stopwatch, font=('Helvetica', 12))
    stopwatch_stop_button.pack()

    # Start periodic log updates
    if log_update_after_id:
        root.after_cancel(log_update_after_id)
        log_update_after_id = None
    log_update_after_id = root.after(60000, update_logs_periodically)

def stop_stopwatch():
    """Stop the stopwatch and save the elapsed time."""
    global timer_started, stopwatch_running, current_subject, start_time, reminder_after_id, stopwatch_stop_button, log_update_after_id, concentration_mode_active
    if stopwatch_running:
        stopwatch_running = False
        concentration_mode_active = False  # Deactivate Concentration Mode
        end_time = datetime.now()
        if current_subject and start_time:
            duration_minutes = (end_time - start_time).total_seconds() / 60
            minutes = round(duration_minutes)
            daily_log[current_subject] += minutes
            study_log[current_subject] += minutes
            monthly_log[current_subject] += minutes
            save_logs()
        sound_path = os.path.join(os.path.dirname(__file__), "assets/timer_done.wav")
        if not os.path.exists(sound_path):
            print(f"Sound file not found: {sound_path}")
        else:
            print(f"Attempting to play: {sound_path}")
            result = os.system(f"paplay {sound_path}")
            if result != 0:
                print(f"Failed to play sound, exit status: {result}")
        label.config(text="Stopped")
        timer_started = False
        if stopwatch_stop_button:
            stopwatch_stop_button.destroy()
            stopwatch_stop_button = None
        if log_update_after_id:
            root.after_cancel(log_update_after_id)
            log_update_after_id = None
        reminder_after_id = root.after(5000, reminder)

def play_sound_if_popup_exists(popup):
    """Play a sound if the reminder popup is still open."""
    if popup and popup.winfo_exists():
        sound_path = os.path.join(os.path.dirname(__file__), "assets/timer_set.wav")
        os.system(f"paplay {sound_path}")

def reminder():
    """Show a reminder popup if no timer is started and not in Concentration Mode."""
    global reminder_after_id, input_win, reminder_popup, concentration_mode_active
    if not timer_started and not concentration_mode_active:
        if reminder_popup and reminder_popup.winfo_exists():
            reminder_popup.destroy()
        
        reminder_popup = tk.Toplevel(root)
        reminder_popup.title("Friendly Reminder \U0001F640")
        reminder_popup.attributes("-topmost", True)

        # Set reminder popup size as 15% of screen width and 5% of screen height, centered
        reminder_width = int(screen_width * 0.15)
        reminder_height = int(screen_height * 0.05)
        reminder_popup.geometry(f"{reminder_width}x{reminder_height}+{int(screen_width * 0.5 - reminder_width * 0.5)}+{int(screen_height * 0.45)}")

        tk.Label(reminder_popup, text="You haven’t set a timer yet...", font=('Helvetica', 11)).pack(pady=10)
        tk.Button(reminder_popup, text="OK", command=reminder_popup.destroy).pack()
        
        root.after(5000, play_sound_if_popup_exists, reminder_popup)
        reminder_after_id = root.after(5000, reminder)
        show_subject_selection()

def show_subject_selection():
    """Show the subject selection window."""
    global input_win
    if input_win and input_win.winfo_exists():
        input_win.destroy()

    input_win = tk.Toplevel(root)
    input_win.title("Choose Subject")
    input_win.attributes("-topmost", True)

    # Set subject selection size as 25% of screen width and 25% of screen height, centered
    input_width = int(screen_width * 0.25)
    input_height = int(screen_height * 0.25)
    input_win.geometry(f"{input_width}x{input_height}+{int(screen_width * 0.375 - input_width * 0.5)}+{int(screen_height * 0.375)}")
    input_win.resizable(False, False)

    tk.Label(input_win, text="What subject are you studying?", font=('Helvetica', 12)).pack(pady=10)
    for subject in SUBJECTS:
        tk.Button(input_win, text=subject, width=20, font=('Helvetica', 14), command=lambda s=subject: ask_duration(s)).pack(pady=2)

def ask_duration(subject):
    """Prompt for timer duration or stopwatch for the selected subject."""
    global current_subject, input_win, start_time
    current_subject = subject
    if input_win and input_win.winfo_exists():
        input_win.destroy()

    input_win = tk.Toplevel(root)
    input_win.title("Timer Setup")
    input_win.attributes("-topmost", True)

    # Set timer setup size as 25% of screen width and 10% of screen height, centered
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

    # Add "Start" button
    tk.Button(input_win, text="Start", command=submit).pack(pady=5)

    # Add "Concentration Mode" button
    tk.Button(input_win, text="Concentration Mode", command=lambda: start_stopwatch(current_subject)).pack(pady=5)

    input_win.bind('<Return>', lambda event: submit())

def start_stopwatch(subject):
    """Start the stopwatch for the selected subject."""
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
    if(timer_started==False and stopwatch_running == False):
        root.destroy()
        return

    """Show a dialog requiring the user to type a specific sentence to quit."""
    quit_win = tk.Toplevel(root)
    quit_win.title("Really Quit?")
    quit_win.attributes("-topmost", True)

    # Set quit dialog size as 25% of screen width and 15% of screen height, centered
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

# Override window close protocol
root.protocol("WM_DELETE_WINDOW", confirm_quit)
graph_root.protocol("WM_DELETE_WINDOW", confirm_quit)

# Start the application
show_subject_selection()
show_monthly_popup()
update_graph()
root.mainloop()
