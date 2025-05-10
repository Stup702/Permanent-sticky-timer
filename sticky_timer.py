#!/usr/bin/env python3

import tkinter as tk
from tkinter import simpledialog
import os

def countdown(duration):
    def update(count):
        mins, secs = divmod(count, 60)
        timer_display = f'{mins:02}:{secs:02}'
        label.config(text=timer_display)
        if count > 0:
            root.after(1000, update, count - 1)
        else:
            label.config(text="Time’s up 🫠")
            # Optional sound
            os.system("paplay /home/YOUR_USERNAME/Sounds/timer_done.wav")  # ← change or comment out
            # Or use this instead:
            # os.system("espeak 'Time is up. Put the book down.'")
            root.after(3000, ask_again)

    update(duration)

def ask_again():
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
        try:
            minutes = int(entry.get())
            if minutes > 0:
                input_win.destroy()
                countdown(minutes * 60)
            else:
                input_win.destroy()
                root.destroy()
        except ValueError:
            entry.delete(0, tk.END)
            entry.insert(0, "🙄")

    tk.Button(input_win, text="Start", command=submit).pack()
    input_win.bind('<Return>', lambda event: submit())

# Set up the window
root = tk.Tk()
root.title("Sticky Timer")
root.attributes("-topmost", True)
root.geometry("200x100+1000+50")
root.resizable(False, False)

label = tk.Label(root, font=('Helvetica', 30), fg='white', bg='black')
label.pack(expand=True, fill='both')

ask_again()
root.mainloop()
