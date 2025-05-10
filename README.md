# Permanent Sticky Timer

A sticky timer appilcation for linux that sticks on top of your workspace. For pretending like you are getting work done and to not have the need to open your timer app again. It will ask for a new timer when one ends. If you do not enter anything in 15 second, tries to guilt trip you.

## Ringtone setup
You need two .wav files for the tone reminders to work. Keep them in /home/USER/Music/
Name them timer_done.wav and timer_set.wav.
Just use mine or download any ringtone you like and convert to .wav. 

## Installation
To make it a executable application on ubuntu, just run the following commands

### 1.First install tkinter:

    sudo apt install python3-tk
 
### 2.Then put Your Script Somewhere Sensible

    mkdir -p ~/Scripts
    mv sticky_timer.py ~/Scripts/

### 3.Make Sure its executable

    chmod +x ~/Scripts/sticky_timer.py


### 4.Make a file called StickyTimer.desktop in your ~/Desktop folder:

    nano ~/Desktop/StickyTimer.desktop

### 5.Put this inside the .desktop file
####⚠️ Replace YOUR_USERNAME with your actual username


    [Desktop Entry]
    Version=1.0
    Type=Application
    Name=Sticky Timer
    Comment=A floating, clingy countdown timer that silently judges you.
    Exec=/home/YOUR_USERNAME/Scripts/sticky_timer.py
    Icon=alarm
    Terminal=false
    StartupNotify=false


#### Then save and exit (Ctrl+O, then Enter, then Ctrl+X).

### 6.  Make It Executable
    chmod +x ~/Desktop/StickyTimer.desktop

### 7. Make it actually clickable
   Right-click the StickyTimer.desktop file on your Desktop, choose Properties > Permissions, and make sure “Allow executing file as program” is checked.


And voila! double click and that timer will haunt your workspace like a ghost.
