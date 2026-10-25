# Wordclock 2.0

Wordclock 2.0 with ESP8266 and NTP time

More details on my website: https://techniccontroller.com/word-clock-with-wifi-and-neopixel/


**Languages**

The frontplate determines the language: English, German, or Italian. English is
selected by default. No sketch files need to be renamed or replaced.

Build with PlatformIO:

```sh
pio run -e english
# Other frontplates:
pio run -e german
pio run -e italian
```

The NodeMCU ESP8266 environments pin the platform and library versions and use a
4 MB flash layout with 2 MB LittleFS. For Arduino IDE builds, use WiFiManager
2.0.17 and select `WORDCLOCK_LANGUAGE` in `wordclock_config.h`.

The web interface displays the firmware version and selected language. Upload
both the firmware and updated `data/` files to get the new settings UI. With a USB
connection, `pio run -e english -t upload` uploads firmware and
`pio run -e english -t uploadfs` uploads the web files. Uploading the filesystem
replaces its contents; preserve any custom files first. Builds alone do not
upload anything. WiFiManager setup works without creating `secrets.h`; an
existing file is still honored for the AP name.

### Startup and network recovery

The startup LED sweep can be disabled in the web settings. Its setting is saved
across restarts. **The IP display and its two-second duration are unchanged.**

Button actions:

- Short press: change mode, or leave manual night mode.
- Hold for 2 seconds and release: enable manual night mode.
- Hold for 8 seconds: open Wi-Fi setup immediately. Releasing then does not also
  enable night mode. Existing credentials are retained until a new network is saved.

If the saved network is unavailable at startup, WiFiManager opens `WordclockAP`
(or the AP name in `secrets.h`). Connect a phone to it and open
`http://192.168.4.1/` to choose the new 2.4 GHz network. Setup runs without blocking
the clock loop. The portal closes after three minutes; hold the button for eight
seconds to reopen it. When the portal is closed, disconnected clocks retry the
saved network every 30 seconds. While the setup portal is open, the normal clock
web UI is paused because both use port 80.

For the move to Italy, no reflash or timezone adjustment is required: the existing
UTC+1 and summer-time configuration applies. The router may assign a different IP.

After the first successful time sync, temporary Wi-Fi or NTP outages leave the
clock ticking from its last synchronized time, with periodic sync retries and no
forced restarts. Time can drift offline. After a power loss, it needs a successful
sync again because there is no battery-backed real-time clock. Until then, clock
modes show blue minute indicators instead of an invalid time.

Automatic night mode evaluates the entire configured interval, including across
midnight, and applies after initial sync and after settings changes. Start is
inclusive and end is exclusive. Equal start and end disables the automatic
schedule. Manual changes last until the next scheduled boundary.

Run host regression checks with Python 3 and g++:

```sh
python3 -B -m unittest discover -s tests -v
```



## Features
- 6 modes (Clock, Digital Clock, SPIRAL animation, TETRIS, SNAKE, PONG)
- time update via NTP server
- automatic summer/wintertime change
- easy WIFI setup with WifiManager
- configurable color
- configurable night mode (start and end time)
- configurable brightness
- automatic mode change
- webserver interface for configuration and control
- physical button to change mode or enable night mode without webserver
- automatic current limiting of LEDs

## Pictures of clock
![modes_images2](https://user-images.githubusercontent.com/36072504/156947689-dd90874d-a887-4254-bede-4947152d85c1.png)

## Screenshots of webserver UI
![screenshots_UI](https://user-images.githubusercontent.com/36072504/158478447-d828e460-d4eb-489e-981e-216e08d4b129.png)

## Quickstart

1. Clone the project into the sketch folder of the Arduino IDE, 
2. Select the language in `wordclock_config.h` (English is the default). WiFiManager does not require router credentials in a source file.
3. Install the additional libraries and upload the program to the ESP8266 as usual (See section [*Upload program to ESP8266*](https://github.com/techniccontroller/wordclock_esp8266/blob/main/README.md#upload-program-to-esp8266-with-arduino-ide) below). 
4. The implemented WiFiManager helps you to set up a WiFi connection with your home WiFi -> on the first startup it will create a WiFi access point named "WordclockAP". Connect your phone to this access point and follow the steps which will be shown to you. 
5. After a successful WiFi setup, open the browser and enter the IP address of your ESP8266 to access the interface of the webserver. 
6. Here you can upload all files located in the folder "data". Please make sure all icons stay in the folder "icons" also on the webserver.


<img src="https://techniccontroller.com/wp-content/uploads/filemanager1-1.png" height="300px" /> <img src="https://techniccontroller.com/wp-content/uploads/filemanager2-1.png" height="300px" /> <img src="https://techniccontroller.com/wp-content/uploads/filemanager3-1.png" height="300px" />

## Install needed Libraries

Please download all these libraries as ZIP from GitHub, and extract them in the *libraries* folder of your Sketchbook location (see **File -> Preferences**):

- https://github.com/adafruit/Adafruit-GFX-Library
- https://github.com/adafruit/Adafruit_NeoMatrix
- https://github.com/adafruit/Adafruit_NeoPixel
- https://github.com/tzapu/WiFiManager
- https://github.com/adafruit/Adafruit_BusIO

folder structure should look like this:

```
MySketchbookLocation 
│
└───libraries
│   └───Adafruit-GFX-Library
│   └───Adafruit_NeoMatrix
│   └───Adafruit_NeoPixel
│   └───WiFiManager
│   └───Adafruit_BusIO
│   
└───wordclock_esp8266
    │   wordclock_esp8266.ino
    │   (...)
    |
    └───data
        │   index.html
        |   (...)
        |
        └───icons 
```


## Upload program to ESP8266 with Arduino IDE

#### STEP1: Installation of Arduino IDE
First, the latest version of the Arduino IDE needs to be downloaded and installed from [here](https://www.arduino.cc/en/software).

#### STEP2: Installation of ESP8266 Arduino Core
To program the ESP8266 with the Arduino IDE, you need to install the board information first in Arduino IDE. To do that follow the following instructions:

- Start Arduino and open the File -> Preferences window.

- Enter http://arduino.esp8266.com/stable/package_esp8266com_index.json into the Additional Board Manager URLs field. You can add multiple URLs, separating them with commas.
![image](https://user-images.githubusercontent.com/36072504/169649790-1b85660e-8c7d-4dfe-a63a-5dfd9862a5de.png)

- Open Boards Manager from Tools > Board menu and search for "esp8266".

- Click the install button.

- Don’t forget to select your ESP8266 board from Tools > Board menu after installation (e.g NodeMCU 1.0)
![image](https://user-images.githubusercontent.com/36072504/169649801-898c4819-9145-45c5-b65b-52f2689ab646.png)

#### STEP3: Upload a program to ESP8266

- Open wordclock_esp8266.ino in Arduino IDE
- Connect ESP8266 board with Computer
- Select right serial Port in Tools -> Port
- Click on the upload button in the Arduino IDE to upload the program to the ESP8266 Module.     
![image](https://user-images.githubusercontent.com/36072504/169649810-1fda75c2-5f4d-4d71-98fe-30985d82f7f5.png)


## Remark about the WiFi setup

WiFiManager is enabled by default. The setup network is `WordclockAP`, and its
portal address is `http://192.168.4.1/`. Hold the physical button for eight seconds
to reopen setup when changing routers. Router credentials are stored by the
ESP8266; they do not need to be compiled into the firmware.

## Resetting the WiFi configuration

You can clear the stored WiFi credentials and restart the WiFi setup described above with these steps:
1. Open the settings panel in the web UI.
2. Enable 'Reset WiFi' slider.
3. Save settings.
4. LED test should be performed.
5. Disconnect and reconnect the power. WiFi credentials were removed. The setup should be restarted.
Resetting the wifi credentials does not delete uploaded files.

## Remark about Logging

The wordclock sends continuous log messages to the serial port and via multicast UDP. If you want to see these messages, you have to 

- open the serial monitor in the Arduino IDE (Tools -> Serial Monitor). The serial monitor must be set to 115200 baud.

OR

- run the following steps for the multicast UDP logging:

1. Starting situation: wordclock is connected to WLAN, a computer with installed Python (https://www.python.org/downloads/) is in the same local area network (WLAN or LAN doesn't matter).
3. Open the file **multicastUDP_receiver.py** in a text editor and in line 81 enter the IP address of the computer (not the wordclock!).
```python	
# ip address of network interface
MCAST_IF_IP = '192.168.0.7'
```
4. Execute the script with following command: 

```bash
python multicastUDP_receiver_analyzer.py
```

5. Now you should see the log messages of the word clock (every 5 seconds a heartbeat message and the currently displayed time). 
If this is not the case, there could be a problem with the network settings of the computer, then recording is unfortunately not possible.

6. If special events (failed NTP update, reboot) occur, a section of the log is saved in a file called *log.txt*. 
In principle, the events are not critical and will occur from time to time, but should not be too frequent.
