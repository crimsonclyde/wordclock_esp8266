#pragma once
#include <stdint.h>

// Equal start and end disables the automatic schedule. The end is exclusive.
inline bool isNightTime(uint16_t now, uint16_t start, uint16_t end) {
    if (start == end) return false;
    if (start < end) return now >= start && now < end;
    return now >= start || now < end;
}
