// Language selection is shared by Arduino IDE and PlatformIO builds.
#include "wordclock_config.h"
#if WORDCLOCK_LANGUAGE == WORDCLOCK_ENGLISH
#include "wordclockfunctions.ino_english"
#elif WORDCLOCK_LANGUAGE == WORDCLOCK_GERMAN
#include "wordclockfunctions.ino_german"
#elif WORDCLOCK_LANGUAGE == WORDCLOCK_ITALIAN
#include "wordclockfunctions.ino_italian"
#else
#error Unsupported WORDCLOCK_LANGUAGE
#endif
