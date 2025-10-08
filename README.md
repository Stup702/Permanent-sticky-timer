# Permanent Sticky Timer

A sticky timer appilcation for linux that sticks on top of your workspace. For pretending like you are getting work done and to not have the need to open your timer app again. It will ask for a new timer when one ends. If you do not enter anything in 15 second, tries to guilt trip you.

## Ringtone setup
You need two .wav files for the tone reminders to work.  They are inside the assets folder

Just use mine or download any ringtone you like and convert to .wav. 

Name them timer_done.wav and timer_set.wav.

## Installation
To make it a executable application on ubuntu, just run the following commands

### 1. First install Dependencies:
    sudo apt install python3-tk
    sudo apt install python3-pip
    pip install matplotlib
 
### 2. Clone the repo
    git clone https://github.com/Stup702/Permanent-sticky-timer
    
#### If you do not have git, download git using 
    sudo apt install git
    
### 3. Make Sure its executable

    chmod +x ~/Permanent_sticky_timer/sticky_timer.py

### 4. Make a systemd file named watchdog.service
     nano ~/.config/systemd/user/watchdog.service
     
Then paste this inside
    
    [Unit]
    Description=Sticky Timer
    After=graphical.target
    
    [Service]
    Type=simple
    ExecStart=python3 /home/USERNAME_HERE/Permanent_sticky_timer/sticky_timer.py
    Restart=always
    RestartSec=2
    Environment=DISPLAY=:0
    Environment=WAYLAND_DISPLAY=%t
    Environment=XDG_RUNTIME_DIR=%t
    
    [Install]
    WantedBy=default.target

    
#### Then save and exit (Ctrl+O, then Enter, then Ctrl+X)

### 5.Initialize the systemd file
    systemctl --user daemon-reload
    systemctl --user enable watchdog.service
    systemctl --user start watchdog.service
    
## ⚠️ If you ever need to stop,
    systemctl --user stop watchdog.service

### 6.Make a file called StickyTimer.desktop in your ~/Desktop folder:

    nano ~/Desktop/StickyTimer.desktop

### 7.Put this inside the .desktop file
#### ⚠️ Replace YOUR_USERNAME with your actual username


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

### 8.  Make It Executable
    chmod +x ~/Desktop/StickyTimer.desktop

### 9. Make it actually clickable
   Right-click the StickyTimer.desktop file on your Desktop, choose Properties > Permissions, and make sure “Allow executing file as program” is checked.


And voila! double click and that timer will haunt your workspace like a ghost.
