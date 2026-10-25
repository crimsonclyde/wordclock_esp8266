"""Regression checks for scheduling and the real NTP client with mocked UDP."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ARDUINO = r'''
#pragma once
#include <cstdint>
#include <string>
#include <type_traits>
using byte = uint8_t;
#define HIGH 1
#define LOW 0
extern unsigned long fakeMillis;
inline unsigned long millis() { return fakeMillis; }
inline void delay(unsigned long ms) { fakeMillis += ms; }
inline uint16_t word(byte a, byte b) { return (uint16_t(a) << 8) | b; }
class String : public std::string {
public:
 using std::string::string;
 String(const std::string& s) : std::string(s) {}
 template<class T, typename std::enable_if<std::is_integral<T>::value, int>::type = 0>
 String(T n) : std::string(std::to_string(n)) {}
};
class IPAddress {};
'''
UDP = r'''
#pragma once
#include "Arduino.h"
class UDP {
public:
 unsigned long timestamp = 3990000000UL;
 int packetSize = 48;
 bool reply = true, pending = false;
 void begin(int) {}
 void stop() {}
 int parsePacket() { return pending ? packetSize : 0; }
 void flush() { pending = false; }
 int beginPacket(const char*, int) { return 1; }
 int beginPacket(IPAddress, int) { return 1; }
 void write(byte*, int) {}
 void endPacket() { pending = reply; }
 int read(byte* packet, int length) {
  for (int i = 0; i < length; ++i) packet[i] = 0;
  for (int i = 0; i < 4; ++i) packet[40 + i] = (timestamp >> (24 - 8*i)) & 255;
  pending = false;
  return length;
 }
};
'''
RUNNER = r'''
#include <cassert>
#include "ntp_client_plus.h"
#include "clock_schedule.h"
unsigned long fakeMillis = 10000;
int main() {
 // Every minute in an overnight schedule, a daytime schedule, and disabled.
 for (int minute = 0; minute < 1440; ++minute) {
  assert(isNightTime(minute, 1380, 420) == (minute < 420 || minute >= 1380));
  assert(isNightTime(minute, 600, 900) == (minute >= 600 && minute < 900));
  assert(!isNightTime(minute, 600, 600));
 }
 UDP udp;
 NTPClientPlus clock(udp, "test", 1, false);
 assert(!clock.hasValidTime());
 udp.reply = false;
 clock.setupNTPClient();
 assert(!clock.hasValidTime());
 udp.reply = true;
 assert(clock.updateNTP() == 0);
 assert(clock.hasValidTime());
 auto before = clock.getEpochTime();
 // Loss of internet must not invalidate or freeze the synchronized clock.
 udp.reply = false;
 fakeMillis += 600000;
 assert(clock.updateNTP() == -1);
 assert(clock.hasValidTime());
 assert(clock.getEpochTime() >= before + 600);
 // Ignore incomplete replies rather than reading stale bytes as a timestamp.
 udp.reply = true;
 udp.packetSize = 12;
 assert(clock.updateNTP() == 2);
 assert(clock.hasValidTime());
 udp.packetSize = 48;
 udp.timestamp += 602;
 assert(clock.updateNTP() == 0);
 assert(clock.hasValidTime());
 assert(clock.getEpochTime() >= before + 602);
}
'''


class RuntimeTest(unittest.TestCase):
    def test_schedule_and_ntp_outage_recovery(self):
        with tempfile.TemporaryDirectory(prefix="wordclock-runtime-") as directory:
            path = Path(directory)
            (path / "Arduino.h").write_text(ARDUINO)
            (path / "WiFiUdp.h").write_text(UDP)
            (path / "check.cpp").write_text(RUNNER)
            subprocess.run([
                "g++", "-std=c++11", "-I", str(path), "-I", str(ROOT),
                str(path / "check.cpp"), str(ROOT / "ntp_client_plus.cpp"),
                "-o", str(path / "check"),
            ], check=True)
            subprocess.run([str(path / "check")], check=True)


if __name__ == "__main__":
    unittest.main()
