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
    minutes = simpledialog.askinteger("Timer Setup", "How many minutes?")
    if minutes and minutes > 0:
        countdown(minutes * 60)
    else:
        root.destroy()  # Escape the loop, and this life

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
