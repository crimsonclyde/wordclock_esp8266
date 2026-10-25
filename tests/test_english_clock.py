"""Host regression check: python3 -m unittest discover -s tests -v (requires g++)."""

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]

# Replace hardware and Arduino String operations, while executing the sketch's
# actual time conversion, word lookup, and split functions.
STUBS = r"""
#include <cstdint>
#include <iostream>
#include <string>
class String : public std::string {
public:
  using std::string::string;
  String(const std::string& value) : std::string(value) {}
  int indexOf(const String& word, int start = 0) const {
    auto pos = find(word, start);
    return pos == npos ? -1 : static_cast<int>(pos);
  }
  int indexOf(char letter, int start = 0) const {
    auto pos = find(letter, start);
    return pos == npos ? -1 : static_cast<int>(pos);
  }
  String substring(int start, int end) const {
    return substr(start, end - start);
  }
};
struct { template<class T> void println(T) {} } Serial;
struct { void logString(String) {} } logger;
#define WIDTH 11
struct {
  bool grid[11][11]{};
  void gridFlush() {
    for (auto& row : grid) for (auto& pixel : row) pixel = false;
  }
  void gridAddPixel(int x, int y, uint32_t) {
    if (x < 0 || x >= 11 || y < 0 || y >= 11) std::abort();
    grid[y][x] = true;
  }
  void setMinIndicator(uint8_t, uint32_t) {}
} ledmatrix;
String split(String, char, int);
"""

RUNNER = r"""
int main() {
  for (int h = 0; h < 24; ++h) for (int m = 0; m < 60; ++m) {
    String message = timeToString(h, m);
    int result = showStringOnClock(message, 0xffffff);
    std::cout << h << '|' << m << '|' << result << '|' << message << '|';
    for (auto& row : ledmatrix.grid)
      for (bool pixel : row) std::cout << (pixel ? '1' : '0');
    std::cout << '\n';
  }
}
"""


class EnglishClockTest(unittest.TestCase):
    def test_all_times_and_led_positions(self):
        source = (ROOT / "wordclockfunctions.ino_english").read_text()
        main = (ROOT / "wordclock_esp8266.ino").read_text()
        start = main.index("String split(String s,")
        split = main[start:main.index("\n/**", start)]
        with tempfile.TemporaryDirectory(prefix="wordclock-test-") as directory:
            path = Path(directory)
            (path / "check.cpp").write_text(STUBS + source + split + RUNNER)
            subprocess.run(
                ["g++", "-std=c++11", str(path / "check.cpp"),
                 "-o", str(path / "check")], check=True,
            )
            output = subprocess.check_output([str(path / "check")], text=True)

        # Expected phrases in each five-minute interval, and whether they name
        # the following hour. These include the half-past and noon boundaries.
        intervals = [
            ("", 0), ("FIVE MINUTES PAST ", 0),
            ("TEN MINUTES PAST ", 0), ("QUARTER PAST ", 0),
            ("TWENTY MINUTES PAST ", 0), ("TWENTY FIVE MINUTES PAST ", 0),
            ("HALF PAST ", 0), ("TWENTY FIVE MINUTES TO ", 1),
            ("TWENTY MINUTES TO ", 1), ("QUARTER TO ", 1),
            ("TEN MINUTES TO ", 1), ("FIVE MINUTES TO ", 1),
        ]
        hours = ["TWELVE", "ONE", "TWO", "THREE", "FOUR", "FIVE",
                 "SIX", "SEVEN", "EIGHT", "NINE", "TEN", "ELEVEN"]
        # Zero-based positions from the English frontplate, independent of the
        # sketch's search string. Distinguish minute FIVE/TEN from hour FIVE/TEN.
        positions = {
            "IT": 0, "IS": 3, "QUARTER": 11, "HALF": 18,
            "TWENTY": 22, "FIVE": 29, "TEN": 6, "MINUTES": 33,
            "TO": 42, "PAST": 44, "OCLOCK": 115,
        }
        hour_positions = [104, 51, 55, 59, 66, 73, 78, 83, 88, 100, 110, 93]
        lines = output.splitlines()
        self.assertEqual(len(lines), 1440)
        for line in lines:
            hour, minute, result, message, pixels = line.split("|")
            hour, minute = int(hour), int(minute)
            with self.subTest(hour=hour, minute=minute):
                phrase, advance = intervals[minute // 5]
                named_hour = (hour + advance) % 12
                expected = "IT IS " + phrase + hours[named_hour] + " "
                if minute < 5:
                    expected += "OCLOCK "
                self.assertEqual(message, expected)
                self.assertEqual(result, "0")
                expected_pixels = set()
                for word in ("IT IS " + phrase).split():
                    pos = positions[word]
                    expected_pixels.update(range(pos, pos + len(word)))
                pos = hour_positions[named_hour]
                expected_pixels.update(range(pos, pos + len(hours[named_hour])))
                if minute < 5:
                    expected_pixels.update(range(115, 121))
                self.assertEqual(
                    {i for i, pixel in enumerate(pixels) if pixel == "1"},
                    expected_pixels,
                )


if __name__ == "__main__":
    unittest.main()
