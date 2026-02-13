#!/usr/bin/env python3

import tkinter as tk
from tkinter import simpledialog
from tkinter import font
from tkinter import messagebox 

import random
import csv
import os
import json
import subprocess
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from setproctitle import setproctitle

setproctitle("Sticky Timer") 

# --- YENNEFER THEME CONFIGURATION ---
THEME = {
    "bg": "#101010",            # Raven Black
    "fg": "#E0E0E0",            # Silver/Pearl
    "button_bg": "#1F1F1F",     # Dark Leather
    "button_fg": "#6F2CAD",     # Light violet previously Thistle/Lilac
    "accent": "#4B0082",        # Indigo
    "highlight": "#9932CC",     # Dark Orchid
    "entry_bg": "#262626",      # Charcoal
    "entry_fg": "#FFFFFF",      # White
    "graph_bg": "#101010",      
    "graph_text": "#D8BFD8"     
}

# --- Configuration & Path Setup ---
SUBJECTS = ["CS50",
            "Personal Coding",
            "CP",
            "COA",
            "Matrix and Lin. Alg.",
            "Accounting",
            "Class",
            "Procrastination",
            "Entertainment",
            "Break",
            "Meditation"]

NON_STUDY_SUBS = ["Class",
                  "Procrastination",
                  "Entertainment",
                  "Break", 
                  "Meditation"]

BREAK_SUBS = ["Procrastination","Break", "Entertainment"]

# Subjects restricted from consecutive repetition
RESTRICTED_SUBJECTS = ["Break", "Entertainment"]

# Subjects NOT allowed in Concentration Mode
NO_CONCENTRATION_SUBS = ["Break", "Entertainment"]

FOLDER_NAME = "Study Stats"
if not os.path.exists(FOLDER_NAME):
    try:
        os.makedirs(FOLDER_NAME)
    except OSError as e:
        print(f"Error creating directory: {e}")

LOG_FILE = os.path.join(FOLDER_NAME, "logs.json")
CSV_FILE = os.path.join(FOLDER_NAME, "study_status.csv") 

# ----------------------------------

sub_cnt = 0
for subject in SUBJECTS:
    sub_cnt += 1

daily_log = {subject: 0 for subject in SUBJECTS}
study_log = {subject: 0 for subject in SUBJECTS}
monthly_log = {subject: 0 for subject in SUBJECTS}
last_weekly_reset = datetime.now().date()
last_monthly_reset = datetime.now().strftime('%Y-%m')
monthly_popup_shown = False
concentration_mode_active = False
last_logged_session = None

last_session_subject = None
last_break_end_time = None

goal = ""
goal_not_set = True 

root = tk.Tk()
root.title("Sticky Timer")
root.attributes("-topmost", False)
root.configure(bg=THEME["bg"]) 

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
main_width = int(screen_width * 0.12)
main_height = int(screen_height * 0.08)
root.geometry(f"{main_width}x{main_height}+{int(screen_width * 0.5 - main_width * 0.5)}+{int(screen_height * 0.1)}")
root.resizable(True, True)

label = tk.Label(root, font=('Helvetica', 30), fg=THEME["fg"], bg=THEME["bg"])
label.pack(expand=True, fill='both')

graph_root = tk.Toplevel(root)
graph_root.title("Study Stats")
graph_root.configure(bg=THEME["bg"]) 
graph_width = int(screen_width * 0.30)
graph_height = int(screen_height * (0.03*sub_cnt))
graph_root.geometry(f"{graph_width}x{graph_height}+{0}+{0}")
graph_root.resizable(False, False)

fig, ax = plt.subplots(figsize=(4, 3))
fig.patch.set_facecolor(THEME["graph_bg"])
ax.set_facecolor(THEME["graph_bg"])

canvas = FigureCanvasTkAgg(fig, master=graph_root)
canvas.get_tk_widget().pack(fill="both", expand=True)
canvas.get_tk_widget().configure(bg=THEME["bg"])

timer_started = False
reminder_after_id = None
scold_after_id = None
input_win = None
reminder_popup = None
goal_popup = None
goal_after_id = None
current_subject = None
start_time = None
stopwatch_running = False
stopwatch_stop_button = None
log_update_after_id = None

# --- CSV Export Logic ---
def format_time_str(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"

def export_to_csv():
    try:
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            
            total_daily_study = 0
            total_weekly_study = 0
            total_daily_break = 0
            total_weekly_break = 0
            
            for subject in SUBJECTS:
                d_time = daily_log.get(subject, 0)
                w_time = study_log.get(subject, 0)
                if subject not in NON_STUDY_SUBS:
                    total_daily_study += d_time
                    total_weekly_study += w_time
                if subject in BREAK_SUBS:
                    total_daily_break += d_time
                    total_weekly_break += w_time

            writer.writerow(["ACTUAL STUDY TIME"])
            writer.writerow(["  Today", format_time_str(total_daily_break)])
            writer.writerow(["  This Week", format_time_str(total_weekly_break)])
            writer.writerow([])
            writer.writerow(["ACTUAL BREAK TIME"])
            writer.writerow(["  Today", format_time_str(total_daily_study)])
            writer.writerow(["  This Week", format_time_str(total_weekly_study)])
            writer.writerow([])
            writer.writerow(["Did/Read what", "Today", "This Week", "This Month"])
            
            for subject in SUBJECTS:
                d_time = daily_log.get(subject, 0)
                w_time = study_log.get(subject, 0)
                m_time = monthly_log.get(subject, 0)
                writer.writerow([subject])
                writer.writerow([
                    " ",
                    format_time_str(d_time), 
                    format_time_str(w_time), 
                    format_time_str(m_time)
                ])
                writer.writerow([])
            
            writer.writerow([])
            writer.writerow(["TODAY'S GOAL:", goal if goal else "Not set yet"])
            writer.writerow([])
            writer.writerow(["Last Updated:", datetime.now().strftime('%H:%M')])

    except Exception as e:
        print(f"Error exporting CSV: {e}")

def add_session_minutes(subject, start_time, minutes):
    global last_logged_session
    # Since we might log split sessions with same start time, we need to be careful with deduplication.
    # We'll append subject to ID to allow logging "Subject A" and "Break" for the same start time.
    session_id = (subject, start_time.strftime('%Y-%m-%d %H:%M:%S'), minutes)

    if last_logged_session == session_id:
        return

    daily_log[subject] = daily_log.get(subject, 0) + minutes
    study_log[subject] = study_log.get(subject, 0) + minutes
    monthly_log[subject] = monthly_log.get(subject, 0) + minutes

    last_logged_session = session_id
    save_logs()

def get_last_friday(date):
    weekday = date.weekday()
    days_since_friday = (weekday - 4) % 7
    last_friday = date - timedelta(days=days_since_friday)
    return last_friday

def daily_goal():
    global goal, goal_popup, goal_not_set, goal_after_id

    # 1. Stop any pending recursive calls (Fixes the "Double Popup" / "Zombie Timer")
    if goal_after_id:
        root.after_cancel(goal_after_id)
        goal_after_id = None

    if goal_popup and goal_popup.winfo_exists():
        goal_popup.destroy()
    
    # Safety check: If goal is already set, don't open this
    if not goal_not_set:
        reminder()
        return

    goal_popup = tk.Toplevel()
    goal_popup.title("Set Goal")
    goal_popup.configure(bg=THEME["bg"]) 
    
    goal_popup_width = int(screen_width * 0.3)
    goal_popup_height = int(screen_height * 0.13)
    goal_popup.geometry(f"{goal_popup_width}x{goal_popup_height}+{int((screen_width  - goal_popup_width)/2 )}+{int(screen_height * 0.21)}")
    goal_popup.resizable(False, False)
    goal_popup.attributes("-topmost", True) 

    tk.Label(goal_popup, text="What is the goal for today?", font=('Helvetica', 12),
             bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)
    
    entry = tk.Entry(goal_popup, font=('Helvetica', 12),
                     bg=THEME["entry_bg"], fg=THEME["entry_fg"], insertbackground=THEME["highlight"])
    entry.pack(pady=5, fill=tk.X, expand=True, padx=10)
    entry.focus()
    
    def submit():
        global goal, goal_not_set, goal_after_id
        
        # Cancel the loop so it doesn't reopen after we destroy it
        if goal_after_id:
            root.after_cancel(goal_after_id)
            goal_after_id = None

        val = entry.get().strip()
        if val:
            goal = val
            goal_not_set = False
            save_logs() 
            goal_popup.destroy()
            reminder() 
        else:
            goal_not_set = True
            
    tk.Button(goal_popup, text="Set Goal", command=submit,
              bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent"]).pack(pady=10)
    
    # 2. Fix Enter Key: Bind to the ENTRY widget, not just the popup
    entry.bind('<Return>', lambda event: submit())

    # Recursive loop to nag if window is ignored
    if goal_not_set:
        root.after(15000, play_sound_if_popup_exists, goal_popup)
        goal_after_id = root.after(15000, daily_goal)

def load_logs():
    global goal, goal_not_set, daily_log, study_log, monthly_log, last_weekly_reset, last_monthly_reset
    try:
        with open(LOG_FILE, 'r') as f:
            data = json.load(f)
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
                goal = data.get('daily_goal_text', "")
                goal_not_set = (goal == "")
            else:
                daily_log = {subject: 0 for subject in SUBJECTS}
                goal = ""
                goal_not_set = True
        except ValueError:
            daily_log = {subject: 0 for subject in SUBJECTS}
            goal = ""
            goal_not_set = True
    else:
        daily_log = {subject: 0 for subject in SUBJECTS}
        goal = ""
        goal_not_set = True

    last_friday = get_last_friday(today)
    last_weekly_reset_str = data.get('last_weekly_reset', '')
    if last_weekly_reset_str:
        try:
            last_weekly_reset = datetime.strptime(last_weekly_reset_str, '%Y-%m-%d').date()
            if last_weekly_reset < last_friday:
                study_log = {subject: 0 for subject in SUBJECTS}
                last_weekly_reset = last_friday
            else:
                study_log.update(data.get('weekly', {}))
        except ValueError:
            study_log = {subject: 0 for subject in SUBJECTS}
            last_weekly_reset = last_friday
    else:
        study_log = {subject: 0 for subject in SUBJECTS}
        last_weekly_reset = last_friday

    last_monthly_reset_local = data.get('last_monthly_reset', current_month)
    if last_monthly_reset_local != current_month:
        monthly_log = {subject: 0 for subject in SUBJECTS}
        last_monthly_reset = current_month
    else:
        monthly_log.update(data.get('monthly', {}))
        last_monthly_reset = last_monthly_reset_local

def save_logs():
    today = datetime.now().date()
    if not os.path.exists(FOLDER_NAME):
        try:
            os.makedirs(FOLDER_NAME)
        except OSError:
            pass

    with open(LOG_FILE, 'w') as f:
        json.dump({
            'daily': daily_log,
            'weekly': study_log,
            'monthly': monthly_log,
            'daily_goal_text': goal, 
            'last_date': today.strftime('%Y-%m-%d'),
            'last_weekly_reset': last_weekly_reset.strftime('%Y-%m-%d'),
            'last_monthly_reset': last_monthly_reset
        }, f)
    export_to_csv()

load_logs()

def show_monthly_popup():
    global monthly_popup_shown
    monthly_popup_shown = True
    popup = tk.Toplevel(root)
    popup.title("Monthly Stats")
    popup.configure(bg=THEME["bg"]) 
    popup.protocol("WM_DELETE_WINDOW", confirm_quit)
    popup_width = int(screen_width * 0.3)
    popup_height = int(screen_height * 0.37)
    popup.geometry(f"{popup_width}x{popup_height}+{int(screen_width  - popup_width )}+{int(0)}")
    popup.resizable(False, False)
    popup.attributes("-topmost", False)

    tk.Label(popup, text="Monthly Study Time", font=('Helvetica', 14, 'bold'),
             bg=THEME["bg"], fg=THEME["button_fg"]).pack(pady=10)
    
    total_mins = 0
    for subject in SUBJECTS:
        mins = monthly_log.get(subject, 0)
        total_mins += mins
        tk.Label(popup, text=f"{subject}:     {mins //60:02d}:{mins%60:02d}", 
                 font=('Helvetica', 14), bg=THEME["bg"], fg=THEME["fg"]).pack(anchor='e', padx=20)
    
    non_study_time_monthly = 0
    for subject in NON_STUDY_SUBS:
        mins = monthly_log.get(subject, 0)
        non_study_time_monthly += mins
    
    total_mins-=non_study_time_monthly
    
    tk.Label(popup, text=f"Total:     {total_mins //60:02d}:{total_mins%60:02d}", 
             font=('Helvetica', 14), bg=THEME["bg"], fg=THEME["highlight"]).pack(anchor='e', padx=20)

def update_graph():
    ax.clear()
    ax.set_title("Weekly Study Time Table", color=THEME["fg"])
    ax.axis('off')
    
    total_weekly = sum(study_log.get(subject, 0) for subject in SUBJECTS)
    non_study_time_weekly=0
    for subject in NON_STUDY_SUBS:
        non_study_time_weekly+=study_log.get(subject,0)
    total_weekly-=non_study_time_weekly

    total_daily = sum(daily_log.get(subject, 0) for subject in SUBJECTS)
    non_study_time_daily=0
    for subject in NON_STUDY_SUBS:
        non_study_time_daily+=daily_log.get(subject,0)
    total_daily -=non_study_time_daily

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
    
    table = ax.table(
        cellText=table_data, 
        colLabels=["Subject", "Weekly", "Today"], 
        loc='center', 
        cellLoc='center',
        bbox=[0, 0, 1, 1] 
    )
    
    for key, cell in table.get_celld().items():
        cell.set_facecolor(THEME["button_bg"])
        cell.set_text_props(color=THEME["fg"])
        cell.set_edgecolor(THEME["bg"]) 
        
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color=THEME["button_fg"])
            cell.set_facecolor(THEME["bg"])

    table.auto_set_font_size(False)
    table.set_fontsize(10)
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
        global current_subject, reminder_after_id, start_time, timer_started, last_session_subject, last_break_end_time
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
            
            last_session_subject = current_subject
            if current_subject in RESTRICTED_SUBJECTS:
                last_break_end_time = datetime.now()

            load_logs()

            if(current_subject in BREAK_SUBS):
                sound_path = os.path.join(os.path.dirname(__file__), "assets/yen_break_over.wav")
            else:
                sound_path = os.path.join(os.path.dirname(__file__), "assets/yen_timer_done.wav")
                
            if not os.path.exists(sound_path):
                print(f"Sound file not found: {sound_path}")
            else:
                os.system(f"paplay {sound_path}")

            end_time = datetime.now()
            if current_subject and start_time:
                duration_minutes = (end_time - start_time).total_seconds() / 60
                minutes = round(duration_minutes)
                add_session_minutes(current_subject, start_time, minutes)
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
            # REMOVED 30 MIN LIMIT
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
    stopwatch_stop_button = tk.Button(root, text="Stop", command=stop_stopwatch, font=('Helvetica', 12),
                                      bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent"])
    stopwatch_stop_button.pack()
    if log_update_after_id:
        root.after_cancel(log_update_after_id)
        log_update_after_id = None
    log_update_after_id = root.after(60000, update_logs_periodically)

def show_custom_message(title, message, msg_type="info"):
    """
    Custom replacement for messagebox to match the Yennefer theme.
    msg_type options: "info", "error", "warning", "yesno"
    Returns: True if Yes/OK is clicked, False if No is clicked.
    """
    # Create the top-level window
    msg_box = tk.Toplevel(root)
    msg_box.title(title)
    msg_box.configure(bg=THEME["bg"])
    msg_box.attributes("-topmost", True)
    
    # Calculate size and position (centered)
    box_width = int(screen_width * 0.25)
    box_height = int(screen_height * 0.15)
    x_pos = int((screen_width - box_width) / 2)
    y_pos = int((screen_height - box_height) / 2)
    msg_box.geometry(f"{box_width}x{box_height}+{x_pos}+{y_pos}")
    msg_box.resizable(False, False)

    # Message Label
    lbl = tk.Label(msg_box, text=message, font=('Helvetica', 12),
                   bg=THEME["bg"], fg=THEME["fg"], wraplength=box_width-20)
    lbl.pack(pady=20, padx=20, expand=True)

    # Container for return value
    result = {"value": False}

    # Button Frame
    btn_frame = tk.Frame(msg_box, bg=THEME["bg"])
    btn_frame.pack(pady=10)

    # Button Commands
    def on_yes_ok():
        result["value"] = True
        msg_box.destroy()

    def on_no():
        result["value"] = False
        msg_box.destroy()

    # Logic to display buttons based on type
    if msg_type == "yesno":
        btn_yes = tk.Button(btn_frame, text="Yes", command=on_yes_ok, width=10,
                            bg=THEME["button_bg"], fg=THEME["button_fg"], 
                            activebackground=THEME["accent"])
        btn_yes.pack(side=tk.LEFT, padx=10)
        
        btn_no = tk.Button(btn_frame, text="No", command=on_no, width=10,
                           bg=THEME["button_bg"], fg=THEME["button_fg"], 
                           activebackground=THEME["accent"])
        btn_no.pack(side=tk.LEFT, padx=10)
        
        # Bind keys for better UX
        msg_box.bind('<Return>', lambda e: on_yes_ok())
        msg_box.bind('<Escape>', lambda e: on_no())

    else: # info, error, warning
        btn_ok = tk.Button(btn_frame, text="OK", command=on_yes_ok, width=10,
                           bg=THEME["button_bg"], fg=THEME["button_fg"], 
                           activebackground=THEME["accent"])
        btn_ok.pack()
        msg_box.bind('<Return>', lambda e: on_yes_ok())
        msg_box.bind('<Escape>', lambda e: on_yes_ok())

    # Make the window modal (disable interaction with main window until closed)
    msg_box.transient(root)
    msg_box.grab_set()
    root.wait_window(msg_box) # This pauses execution of the main script

    return result["value"]

def start_stopwatch(subject):
    global current_subject, input_win, timer_started, reminder_after_id, reminder_popup
    
    # --- RESTRICTION CHECK ---
    if subject in NO_CONCENTRATION_SUBS:
        # messagebox.showerror("Not Allowed", "Concentration Mode is for study subjects only.\nUse a standard timer for breaks.")
        show_custom_message("Not Allowed", "Concentration Mode is for study subjects only.\nUse a standard timer for breaks.", "error")
        return
        return
    
    # # --- CONFIRMATION ---
    # if not messagebox.askyesno("Confirm", "It's better to study on slotted time. Are you sure ?"):
    #     return
    if not show_custom_message("Confirm", "It's better to study on slotted time. Are you sure ?", "yesno"):
        return

    current_subject = subject
    if input_win and input_win.winfo_exists():
        input_win.destroy()
    if reminder_after_id:
        root.after_cancel(reminder_after_id)
        reminder_after_id = None
    if reminder_popup and reminder_popup.winfo_exists():
        reminder_popup.destroy()
    stopwatch()

def stop_stopwatch():
    global timer_started, stopwatch_running, current_subject, start_time, reminder_after_id, stopwatch_stop_button, log_update_after_id, concentration_mode_active, last_session_subject, last_break_end_time
    if stopwatch_running:
        stopwatch_running = False
        concentration_mode_active = False
        
        last_session_subject = current_subject
        if current_subject in RESTRICTED_SUBJECTS:
            last_break_end_time = datetime.now()

        end_time = datetime.now()
        minutes = 0
        if current_subject and start_time:
            duration_minutes = (end_time - start_time).total_seconds() / 60
            minutes = round(duration_minutes)

        label.config(text="Stopped")
        timer_started = False
        if stopwatch_stop_button:
            stopwatch_stop_button.destroy()
            stopwatch_stop_button = None
        if log_update_after_id:
            root.after_cancel(log_update_after_id)
            log_update_after_id = None
        
        # --- NEW LOGIC FOR > 30 MINS ---
        
        if minutes > 30:
            show_allocation_window(minutes, current_subject, start_time)

        else:
            # Standard logic for <= 30 mins
            if minutes >= 25:
                sound_path = os.path.join(os.path.dirname(__file__), "assets/yen_timer_done.wav")
                if os.path.exists(sound_path):
                    os.system(f"paplay {sound_path}")
            
            add_session_minutes(current_subject, start_time, minutes)
            reminder_after_id = root.after(500, reminder)

        try:
            with open('/tmp/sticky_timer.txt', 'w') as f:
                json.dump({'time': '00:00', 'subject': ''}, f)
        except Exception as e:
                print(f"Failed to clear timer state: {e}")

def show_allocation_window(total_minutes, subject, s_time):
    """
    Popup to split time if session was > 30 mins.
    """
    alloc_win = tk.Toplevel(root)
    alloc_win.title("Time Allocation")
    alloc_win.configure(bg=THEME["bg"])
    alloc_win.attributes("-topmost", True)
    
    # Window geometry
    alloc_width = int(screen_width * 0.3)
    alloc_height = int(screen_height * 0.3)
    alloc_win.geometry(f"{alloc_width}x{alloc_height}+{int((screen_width-alloc_width)/2)}+{int((screen_height - alloc_height)/2)}")

    tk.Label(alloc_win, text=f"Total Time: {total_minutes} min", font=('Helvetica', 14, 'bold'),
             bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)
    
    tk.Label(alloc_win, text=f"How much time was actually {subject}?", font=('Helvetica', 12),
             bg=THEME["bg"], fg=THEME["fg"]).pack(pady=5)
    
    entry_real = tk.Entry(alloc_win, font=('Helvetica', 12), bg=THEME["entry_bg"], fg=THEME["entry_fg"], insertbackground=THEME["highlight"])
    entry_real.insert(0, str(30)) # Suggest 30 mins
    entry_real.pack(pady=5)
    
    tk.Label(alloc_win, text="Deposit the rest into:", font=('Helvetica', 12),
             bg=THEME["bg"], fg=THEME["fg"]).pack(pady=5)
    
    deposit_options = list(SUBJECTS) 
    
    # FIX 3: Safe removal check
    if "Meditation" in deposit_options:
        deposit_options.remove("Meditation")
    
    # Added "Discard" option in case I don't want to log the extra time at all
    if "Discard" not in deposit_options:
        deposit_options.append("Discard")
    selected_deposit = tk.StringVar(alloc_win)
    selected_deposit.set("Break")
    
    # Style the OptionMenu to match theme
    opt = tk.OptionMenu(alloc_win, selected_deposit, *deposit_options)
    opt.config(bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent"], highlightthickness=0)
    opt["menu"].config(bg=THEME["button_bg"], fg=THEME["button_fg"])
    opt.pack(pady=5)

    def confirm_allocation():
        global reminder_after_id
        try:
            real_work = int(entry_real.get())
            if real_work < 0: real_work = 0
            if real_work > total_minutes: real_work = total_minutes
            
            remainder = total_minutes - real_work
            deposit_target = selected_deposit.get()
            
            # Log the real work
            if real_work > 0:
                add_session_minutes(subject, s_time, real_work)
            
            # Log the remainder
            if remainder > 0 and deposit_target != "Discard":
                add_session_minutes(deposit_target, s_time, remainder)
            
            alloc_win.destroy()
            reminder_after_id = root.after(5000, reminder)

        except ValueError:
            pass
    def on_window_close():
        # If closed without allocating, log everything to the main subject so data isn't lost
        add_session_minutes(subject, s_time, total_minutes)
        alloc_win.destroy()
        global reminder_after_id
        reminder_after_id = root.after(5000, reminder)
        
    alloc_win.protocol("WM_DELETE_WINDOW", on_window_close)

    tk.Button(alloc_win, text="Confirm", command=confirm_allocation,
              bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent"]).pack(pady=15)

def play_sound_if_popup_exists(popup):
    if popup and popup.winfo_exists():
        audio_file_id = random.randint(1,3)
        audio_file_name = "assets/yen_timer_set_"+str(audio_file_id)+".wav"
        sound_path = os.path.join(os.path.dirname(__file__), audio_file_name)
        os.system(f"paplay {sound_path}")
def scold_user():
    global scold_after_id, reminder_popup, goal, input_win
    
    # 1. Prevent timer stacking (Cancel any previous pending scold)
    if scold_after_id:
        root.after_cancel(scold_after_id)
        scold_after_id = None
    
    # Safety: Don't scold if a timer is actually running
    if timer_started or concentration_mode_active:
        return

    # 2. THE FIX: If the subject window is closed/missing, bring it back!
    if input_win is None or not input_win.winfo_exists():
        show_subject_selection()

    # 3. Show the Scolding Popup
    if reminder_popup and reminder_popup.winfo_exists():
        reminder_popup.destroy()
    
    reminder_popup = tk.Toplevel(root)
    reminder_popup.title("Friendly Reminder \U0001F640")
    reminder_popup.attributes("-topmost", True)
    reminder_popup.configure(bg=THEME["bg"]) 

    my_font = font.Font(family="Helvetica", size=11, weight="normal")
    warning = "Is what you are doing right now, more important?"
    comparison_str = warning if len(warning) > len(goal) else goal
    
    width_in_pixels = my_font.measure(comparison_str)
    multiplier = min(max(width_in_pixels / screen_width + 0.1, 0.2), 0.8)

    reminder_width = int(screen_width * multiplier)
    reminder_height = int(screen_height * 0.12)

    reminder_popup.geometry(f"{reminder_width}x{reminder_height}+{int(screen_width * 0.5 - reminder_width * 0.5)}+{int(screen_height * 0.215)}")
    
    tk.Label(reminder_popup, text=f"Today's Goal: {goal}", font=('Helvetica', 11),
             bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)

    tk.Label(reminder_popup, text=warning, font=('Helvetica', 11),
             bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)
    
    tk.Button(reminder_popup, text="OK", command=reminder_popup.destroy,
              bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent"]).pack()
    
    # 4. Play Sound
    root.after(500, play_sound_if_popup_exists, reminder_popup)

    # 5. Repeat Scolding every 15 seconds if ignored
    scold_after_id = root.after(15000, scold_user)
     
def reminder():
    global goal, goal_not_set, reminder_after_id, timer_started, concentration_mode_active, input_win, scold_after_id
    
    # 1. Check if already selecting (busy)
    if input_win and input_win.winfo_exists():
        # Check back in 5 seconds, but don't force anything
        reminder_after_id = root.after(5000, reminder)
        return
    
    # 2. Check if timer running (busy)
    if timer_started or concentration_mode_active:
        reminder_after_id = root.after(15000, reminder)
        return

    # 3. Check Goal
    if goal_not_set:
        daily_goal()
        return
    
    # 4. Open Selection Window IMMEDIATELY
    show_subject_selection()
    
    # 5. Schedule the Scolding (Nag) for 15 seconds later
    if scold_after_id:
        root.after_cancel(scold_after_id)
    scold_after_id = root.after(15000, scold_user)
    
    # Note: We do NOT schedule 'reminder' loop here. 
    # The 'scold_user' loop takes over until a session is started.

    
def validate_subject_selection(subject):
    global last_session_subject, last_break_end_time

    if subject in RESTRICTED_SUBJECTS:
        if last_session_subject in RESTRICTED_SUBJECTS:
            # messagebox.showwarning("Hold on!", "I cannot take two breaks in a row.\nGo study something first!")
            show_custom_message("Hold on!", "You cannot take two breaks in a row.\nGo study something first!", "warning")
            return

        if last_break_end_time:
            time_since_break = datetime.now() - last_break_end_time
            if time_since_break < timedelta(minutes=5):
                remaining_seconds = 300 - int(time_since_break.total_seconds())
                mins, secs = divmod(remaining_seconds, 60)
                # messagebox.showwarning("Cooldown Active", f"I must wait {mins}m {secs}s before taking another break.")
                show_custom_message("Cooldown Active", f"You must wait {mins}m {secs}s before taking another break.", "warning")
                return

    ask_duration(subject)

def show_subject_selection():
    global input_win
    if input_win and input_win.winfo_exists():
        input_win.destroy()

    input_win = tk.Toplevel(root)
    input_win.title("Choose Subject")
    input_win.attributes("-topmost", True)
    input_win.configure(bg=THEME["bg"]) 
    
    input_width = int(screen_width * 0.25)
    input_height = int(screen_height * (0.0353846 *sub_cnt))
    input_win.geometry(f"{input_width}x{input_height}+{int((screen_width - input_width)/2 )}+{int(screen_height * 0.375)}")
    input_win.resizable(True, True)

    tk.Label(input_win, text="What subject are you studying?", font=('Helvetica', 12),
             bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)
    for subject in SUBJECTS:
        tk.Button(input_win, text=subject, width=20, font=('Helvetica', 14), 
                  command=lambda s=subject: validate_subject_selection(s),
                  bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent"]).pack(pady=2)

def ask_duration(subject):
    global current_subject, input_win, start_time
    current_subject = subject
    if input_win and input_win.winfo_exists():
        input_win.destroy()

    if subject == "Meditation":
        try:
            subprocess.Popen(["gnome-terminal", "--", "/home/stup/Permanent_sticky_timer/quote_shower"])
            print("Motivational quote shower executed in a new terminal")
        except Exception as e:
            print(f"Failed to run quote_shower: {e}")

    input_win = tk.Toplevel(root)
    input_win.title("Timer Setup")
    input_win.attributes("-topmost", True)
    input_win.configure(bg=THEME["bg"]) 
    
    setup_width = int(screen_width * 0.25)
    setup_height = int(screen_height * 0.23)
    input_win.geometry(f"{setup_width}x{setup_height}+{int((screen_width - setup_width) * 0.5)}+{int(screen_height * 0.45)}")
    input_win.resizable(True, True)

    tk.Label(input_win, text=f"How many minutes for {subject}?", font=('Helvetica', 12),
             bg=THEME["bg"], fg=THEME["fg"]).pack(pady=5)
    
    entry = tk.Entry(input_win, font=('Helvetica', 14),
                     bg=THEME["entry_bg"], fg=THEME["entry_fg"], insertbackground=THEME["highlight"])
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
                tk.Label(input_win, text="Please enter a positive number", fg="red", bg=THEME["bg"]).pack()
        except ValueError:
            entry.delete(0, tk.END)
            entry.insert(0, "\U0001F644")

    def set_timer(min):
        global timer_started, reminder_after_id, reminder_popup, start_time
        
        timer_started = True
        start_time = datetime.now()
        input_win.destroy()
        if reminder_after_id:
            root.after_cancel(reminder_after_id)
            reminder_after_id = None
        if reminder_popup and reminder_popup.winfo_exists():
            reminder_popup.destroy()
        countdown(min * 60)

    tk.Button(input_win, text="Start", command=submit,
              bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent"]).pack(pady=5)
    tk.Button(input_win, text="25 min", command=lambda: set_timer(25),
              bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent"]).pack(pady=5)
    tk.Button(input_win, text="5 min", command=lambda: set_timer(5),
              bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent"]).pack(pady=5)
    tk.Button(input_win, text="Concentration Mode", command=lambda: start_stopwatch(current_subject),
              bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent"]).pack(pady=5)
    input_win.bind('<Return>', lambda event: submit())

def confirm_quit():
    quit_win = tk.Toplevel(root)
    quit_win.title("Really Quit?")
    quit_win.attributes("-topmost", True)
    quit_win.configure(bg=THEME["bg"]) 
    
    quit_width = int(screen_width * 0.25)
    quit_height = int(screen_height * 0.15)
    quit_win.geometry(f"{quit_width}x{quit_height}+{int(screen_width * 0.375 - quit_width * 0.5)}+{int(screen_height * 0.375)}")
    quit_win.resizable(False, False)

    required_sentence = "I am giving up on my study goals"
    tk.Label(quit_win, text=f"Type exactly: '{required_sentence}'", font=('Helvetica', 12),
             bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)
    
    entry = tk.Entry(quit_win, font=('Helvetica', 12), width=40,
                     bg=THEME["entry_bg"], fg=THEME["entry_fg"], insertbackground=THEME["highlight"])
    entry.pack(pady=5)
    entry.focus()

    def check_quit():
        if entry.get() == required_sentence:
            root.destroy()
        else:
            tk.Label(quit_win, text="Sentence doesn't match. Try again.", fg="red", bg=THEME["bg"]).pack()
            entry.delete(0, tk.END)

    tk.Button(quit_win, text="Quit", command=check_quit,
              bg=THEME["button_bg"], fg=THEME["button_fg"], activebackground=THEME["accent"]).pack(pady=5)
    quit_win.bind('<Return>', lambda event: check_quit())

root.protocol("WM_DELETE_WINDOW", confirm_quit)
graph_root.protocol("WM_DELETE_WINDOW", confirm_quit)

# show_subject_selection()
show_monthly_popup()
update_graph()

# root.after(500, play_sound_if_popup_exists, reminder_popup)
reminder_after_id = root.after(500, reminder)

root.mainloop()