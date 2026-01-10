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


### A watchdog that restarts the app every 30 mins if its off ( If you want)

If you are a master procrastinator like me and turn off your timer sometimes and then forget to turn it back up, it's not going to do that much judging anyway, right?
Well, have no fear, every 30 minutes, the systemd service will check your timer state, if off, it's gonna come back to life.

TO enable this feature, simply go to the systemd setup file and run the setup_systemd.sh file

make is executable,
    
    chmod +x setup_systemd.sh

then run,

    ./setup_systemd.sh

And done. 

To exorcise this recurring ghost, 
run the remove_systemd.sh file

Go to the systemd removal folder and then run the remove_systemd.sh file

make is executable,
    
    chmod +x remove_systemd.sh

then run,

    ./remove_systemd.sh


## A safety word to kill the app for some time,

    systemctl --user stop watchdog.service

## Another bigger safety word for closure till restart,

    systemctl --user stop watchdog.service
    systemctl --user start watchdog_timer.service
This will paralyze the system until restart

    


### Also a GNOME EXTENSION
If you want dont want timer window to be a pain in the a$$, you can configure it to have a gnome extension which will create a timer in the top bar. Like this,

<img width="371" height="94" alt="image" src="https://github.com/user-attachments/assets/78f7fe14-e0a0-46a4-8f58-00fe4dd67ebb" />


Then use the install_extension.sh file

    chmod +x install_extension.sh

and then 
    
    ./install_extension.sh

This will install the GNOME EXTENSION for this app.

##MUST BE A GNOME DESKTOP



