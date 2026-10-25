"""Run actual sketch control functions against simulated button/network state."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from test_runtime import ARDUINO

ROOT = Path(__file__).resolve().parents[1]


def function(source, signature):
    start = source.index(signature)
    opening = source.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end] + "\n"


MOCKS = r'''
#include <cassert>
#include "Arduino.h"
#include "clock_schedule.h"
unsigned long fakeMillis = 0;
const int WL_CONNECTED = 3, BUTTONPIN = 14, LONGPRESS = 2000, SHORTPRESS = 100;
const int WIFI_SETUP_PRESS = 8000, PERIOD_WIFI_RECONNECT = 30000, PERIOD_NTPUPDATE = 30000;
const int NUM_STATES = 6;
const char* AP_SSID = "WordclockAP";
String hostname = "wordclock";
int logMulticastIP = 0, logMulticastPort = 8123;
bool pressed = false;
int digitalRead(int) { return !pressed; }
struct { int starts=0, stops=0; void begin(){starts++;} void stop(){stops++;} } server;
struct {
 bool active=false; int starts=0;
 bool getConfigPortalActive(){return active;}
 void startConfigPortal(const char*){active=true; starts++;}
 void process(){}
} wifiManager;
struct IP { String toString(){return "192.168.1.20";} };
struct {
 int state=0, retries=0;
 int status(){return state;}
 IP localIP(){return IP();}
 void reconnect(){retries++;}
} WiFi;
struct UDPLogger {
 UDPLogger(){} UDPLogger(IP,int,int){}
 void setName(const char*){} void logString(String){}
} logger;
struct {
 bool valid=false; int h=23,m=30;
 bool hasValidTime(){return valid;} int getHours24(){return h;} int getMinutes(){return m;}
} ntp;
bool webServerRunning=true, wasWiFiConnected=false, otaStarted=false;
bool scheduleInitialized=false, scheduledNight=false, nightMode=false;
uint32_t lastNTPUpdate=0, lastWiFiReconnect=0, buttonPressStart=0;
int nightModeStartHour=23, nightModeStartMin=0, nightModeEndHour=7, nightModeEndMin=0;
int currentState=0, nightChanges=0;
void setNightmode(bool value){nightMode=value; nightChanges++;}
void stateChange(int state){currentState=state;}
void setupOTA(String){}
void applyNightSchedule(bool force=false);
void openWiFiSetup();
'''

RUNNER = r'''
int main(){
 applyNightSchedule(); assert(!scheduleInitialized);
 ntp.valid=true;
 applyNightSchedule(); assert(nightMode && scheduleInitialized);
 // A manual override survives periodic checks, until the scheduled boundary.
 setNightmode(false);
 applyNightSchedule(); assert(!nightMode);
 ntp.h=7; ntp.m=0;
 applyNightSchedule(); assert(!nightMode && !scheduledNight);
 // Starting during a daytime night interval also applies immediately.
 nightModeStartHour=10; nightModeEndHour=15; ntp.h=12;
 applyNightSchedule(true); assert(nightMode);
 // Very long hold opens setup once, and releasing does not enable night mode.
 nightMode=false;
 pressed=true; handleButton();
 fakeMillis=8000; handleButton();
 assert(wifiManager.starts==1 && !webServerRunning && server.stops==1);
 fakeMillis=9000; handleButton(); assert(wifiManager.starts==1);
 pressed=false; handleButton(); assert(!nightMode);
 // Portal owns port 80 until it closes. Do not reconnect underneath setup.
 fakeMillis=30000; handleNetwork();
 assert(server.starts==0 && WiFi.retries==0);
 wifiManager.active=false; handleNetwork();
 assert(webServerRunning && server.starts==1 && WiFi.retries==1);
 fakeMillis=31000; handleNetwork(); assert(WiFi.retries==1);
 WiFi.state=WL_CONNECTED; handleNetwork(); assert(otaStarted);
 assert(uint32_t(fakeMillis-lastNTPUpdate)>=PERIOD_NTPUPDATE);
 // Existing long and short button actions still work.
 pressed=true; handleButton(); fakeMillis+=2100;
 pressed=false; handleButton(); assert(nightMode);
 pressed=true; handleButton(); fakeMillis+=200;
 pressed=false; handleButton(); assert(!nightMode);
 pressed=true; handleButton(); fakeMillis+=200;
 pressed=false; handleButton(); assert(currentState==1);
}
'''


class ControlsTest(unittest.TestCase):
    def test_button_wifi_and_night_mode_transitions(self):
        source = (ROOT / "wordclock_esp8266.ino").read_text()
        functions = "".join(function(source, signature) for signature in [
            "void applyNightSchedule(bool force)", "void openWiFiSetup()",
            "void handleNetwork()", "void handleButton()",
        ])
        with tempfile.TemporaryDirectory(prefix="wordclock-controls-") as directory:
            path = Path(directory)
            (path / "Arduino.h").write_text(ARDUINO)
            (path / "check.cpp").write_text(MOCKS + functions + RUNNER)
            subprocess.run([
                "g++", "-std=c++11", "-I", str(path), "-I", str(ROOT),
                str(path / "check.cpp"), "-o", str(path / "check"),
            ], check=True)
            subprocess.run([str(path / "check")], check=True)
