import tkinter as tk
import time

DURATION = 5 * 60  # 5 minutes

def countdown(count):
    mins, secs = divmod(count, 60)
    timer_display = f'{mins:02}:{secs:02}'
    label.config(text=timer_display)
    if count > 0:
        root.after(1000, countdown, count - 1)
    else:
        label.config(text="Time’s up 🫠")

root = tk.Tk()
root.title("Sticky Timer")
root.attributes("-topmost", True)
root.geometry("200x100+1000+50")
root.resizable(False, False)

label = tk.Label(root, font=('Helvetica', 30), fg='white', bg='black')
label.pack(expand=True, fill='both')

countdown(DURATION)
root.mainloop()
