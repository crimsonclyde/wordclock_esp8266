#pragma once

#define WORDCLOCK_ENGLISH 1
#define WORDCLOCK_GERMAN 2
#define WORDCLOCK_ITALIAN 3

// Override with a build flag, or edit here when using the Arduino IDE.
#ifndef WORDCLOCK_LANGUAGE
#define WORDCLOCK_LANGUAGE WORDCLOCK_ENGLISH
#endif

#define WORDCLOCK_VERSION "2.1.0"

#if WORDCLOCK_LANGUAGE == WORDCLOCK_ENGLISH
#define WORDCLOCK_LANGUAGE_NAME "English"
#elif WORDCLOCK_LANGUAGE == WORDCLOCK_GERMAN
#define WORDCLOCK_LANGUAGE_NAME "German"
#elif WORDCLOCK_LANGUAGE == WORDCLOCK_ITALIAN
#define WORDCLOCK_LANGUAGE_NAME "Italian"
#else
#error Unsupported WORDCLOCK_LANGUAGE
#endif

// Functions in the selected language include are not discovered by Arduino's
// automatic prototype generator.
String timeToString(uint8_t hours, uint8_t minutes);
int showStringOnClock(String message, uint32_t color);
void drawMinuteIndicator(uint8_t minutes, uint32_t color);
String split(String s, char parser, int index);
void applyNightSchedule(bool force = false);
