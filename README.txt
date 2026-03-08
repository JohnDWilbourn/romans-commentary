ROMANS ROAD COMMENTARY — LOCAL SERVER SETUP
===========================================

REQUIREMENTS
------------
- Python 3 (already installed on Ubuntu)
- Both devices (laptop + phone) on the same WiFi network


FIRST TIME SETUP
----------------
1. Unzip the romans-commentary.zip file
2. Place the romans-commentary folder wherever you want it
   (Desktop, Documents, your project folder, etc.)


STARTING THE SERVER
-------------------
Open a terminal and run:

    cd /path/to/romans-commentary
    bash serve.sh

Example if it's on your Desktop:

    cd ~/Desktop/romans-commentary
    bash serve.sh

The terminal will print two URLs:

    Laptop:  http://localhost:8000
    Phone:   http://192.168.x.x:8000


OPENING ON YOUR LAPTOP
-----------------------
Open any browser and go to:

    http://localhost:8000


OPENING ON YOUR PHONE (Galaxy S25 Ultra)
-----------------------------------------
1. Make sure your phone is on the same WiFi as your laptop
2. Open Chrome on your phone
3. Type the Phone URL printed by serve.sh into the address bar
   Example: http://192.168.1.105:8000
4. The site will load just like on the laptop


INSTALLING AS AN APP ON ANDROID
---------------------------------
1. Open the site in Chrome on your phone
2. Tap the three-dot menu (top right)
3. Tap "Add to Home Screen" or "Install App"
4. It will appear on your home screen like a native app
5. Once installed, it works OFFLINE — no server needed


STOPPING THE SERVER
--------------------
In the terminal where serve.sh is running, press:

    Ctrl + C


TROUBLESHOOTING
---------------
Phone can't connect?
  - Make sure laptop and phone are on the same WiFi network
  - Mobile data on the phone must be OFF (or it won't reach local network)
  - Check that your laptop firewall isn't blocking port 8000

    To temporarily allow port 8000 on Ubuntu:
    sudo ufw allow 8000

IP address changed?
  - Your laptop's local IP can change when you reconnect to WiFi
  - Just run serve.sh again and use the new IP it prints

Server already running on port 8000?
  - Either stop the other process, or edit serve.sh and change
    PORT=8000 to PORT=8001 (then use :8001 in the browser)


NOTES
-----
- The server only needs to run when you're reading locally
- Once the site is deployed to GitHub Pages, no server is needed
- The search index (search-index.json) loads automatically
- All content works offline after the PWA is installed
