To make it a executable application on ubuntu, just run the following commands

1.First install tkinter:

sudo apt install python3-tk

2.Then put Your Script Somewhere Sensible

mkdir -p ~/Scripts
mv sticky_timer.py ~/Scripts/

3. Make Sure its executable

chmod +x ~/Scripts/sticky_timer.py


4. Make a file called StickyTimer.desktop in your ~/Desktop folder:

nano ~/Desktop/StickyTimer.desktop

5.Put this inside the .desktop file
⚠️ Replace YOUR_USERNAME with your actual username


[Desktop Entry]
Version=1.0
Type=Application
Name=Sticky Timer
Comment=A floating, clingy countdown timer that silently judges you.
Exec=/home/YOUR_USERNAME/Scripts/sticky_timer.py
Icon=alarm
Terminal=false
StartupNotify=false


6. Then save and exit (Ctrl+O, then Enter, then Ctrl+X).

7.  Make It Executable
    chmod +x ~/Desktop/StickyTimer.desktop

8. Make it actually clickable
   Right-click the StickyTimer.desktop file on your Desktop, choose Properties > Permissions, and make sure “Allow executing file as program” is checked.


And voila! click and that timer will haunt your workspace like a ghost.
