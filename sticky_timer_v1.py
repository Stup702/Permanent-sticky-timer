#!/usr/bin/env python3

import tkinter as tk
from tkinter import simpledialog
import os

root = tk.Tk()
root.title("Sticky Timer")
root.attributes("-topmost", True)
root.geometry("200x100+1000+50")
root.resizable(False, False)

label = tk.Label(root, font=('Helvetica', 30), fg='white', bg='black')
label.pack(expand=True, fill='both')

timer_started = False
reminder_after_id = None

def countdown(duration):
    def update(count):
        global reminder_after_id
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
            # Schedule reminder in 15 seconds if timer not reset
            reminder_after_id = root.after(15000, reminder)
            ask_again()

    update(duration)

def ask_again():
    show_input_window()

def reminder():
    if not timer_started:
        os.system("paplay /home/stup/Music/timer_set.wav")
        popup = tk.Toplevel(root)
        popup.title("Friendly Reminder 🙀")
        popup.attributes("-topmost", True)
        popup.geometry("220x70+1000+400")
        tk.Label(popup, text="You haven’t set a timer yet...", font=('Helvetica', 11)).pack(pady=10)
        tk.Button(popup, text="OK", command=popup.destroy).pack()

def show_input_window():
    input_win = tk.Toplevel(root)
    input_win.title("Timer Setup")
    input_win.attributes("-topmost", True)
    input_win.geometry("250x100+950+200")
    input_win.resizable(False, False)

    tk.Label(input_win, text="How many minutes?", font=('Helvetica', 12)).pack(pady=5)
    entry = tk.Entry(input_win, font=('Helvetica', 14))
    entry.pack(pady=5)
    entry.focus()

    def submit():
        global timer_started, reminder_after_id
        try:
            minutes = int(entry.get())
            if minutes > 0:
                timer_started = True
                input_win.destroy()
                if reminder_after_id:
                    root.after_cancel(reminder_after_id)
                    reminder_after_id = None
                countdown(minutes * 60)
            else:
                input_win.destroy()
                root.destroy()
        except ValueError:
            entry.delete(0, tk.END)
            entry.insert(0, "🙄")

    tk.Button(input_win, text="Start", command=submit).pack()
    input_win.bind('<Return>', lambda event: submit())

# Initial prompt
show_input_window()

root.mainloop()
