// SPDX-License-Identifier: MIT
#include <stdio.h>
#include <stdlib.h>

#include "rp1_gpclk/execution_policy.h"

#define CHECK(expression)                                                     \
    do {                                                                      \
        if (!(expression)) {                                                  \
            fprintf(stderr, "%s:%d: CHECK failed: %s\n", __FILE__, __LINE__, \
                    #expression);                                             \
            exit(1);                                                          \
        }                                                                     \
    } while (0)

int main(void)
{
    struct rp1_gpclk_tone tones[RP1_GPCLK_MAX_TONES] = { 0 };
    __u32 words[8] = { 0 };
    size_t writes = 0;
    unsigned int index;

    for (index = 0; index < RP1_GPCLK_MAX_TONES; index++) {
        tones[index].lower_divider_q16 = (3ULL << 16) + 10 + index * 2;
        tones[index].upper_divider_q16 =
            tones[index].lower_divider_q16 + 1;
        tones[index].lower_count = 1;
        tones[index].upper_count = 3;
    }
    CHECK(rp1_gpclk_execution_tones_valid(
              tones, RP1_GPCLK_MAX_TONES, RP1_GPCLK_DRIVE_MA_2) == 0);
    CHECK(rp1_gpclk_execution_tones_valid(tones, 0,
              RP1_GPCLK_DRIVE_MA_2) != 0);
    CHECK(rp1_gpclk_execution_tones_valid(tones, RP1_GPCLK_MAX_TONES,
              RP1_GPCLK_DRIVE_MA_4) != 0);
    tones[3].lower_divider_q16 = (4ULL << 16) + 1;
    tones[3].upper_divider_q16 = tones[3].lower_divider_q16 + 1;
    CHECK(rp1_gpclk_execution_tones_valid(
              tones, RP1_GPCLK_MAX_TONES, RP1_GPCLK_DRIVE_MA_2) != 0);
    tones[3] = tones[0];

    tones[0].lower_divider_q16 = (255ULL << 16) + 1;
    tones[0].upper_divider_q16 = tones[0].lower_divider_q16 + 1;
    CHECK(rp1_gpclk_execution_tones_valid(
              tones, 1, RP1_GPCLK_DRIVE_MA_2) == 0);
    tones[0].lower_divider_q16 = (256ULL << 16) + 1;
    tones[0].upper_divider_q16 = tones[0].lower_divider_q16 + 1;
    CHECK(rp1_gpclk_execution_tones_valid(
              tones, 1, RP1_GPCLK_DRIVE_MA_2) == 0);
    tones[0].lower_divider_q16 = (368ULL << 16) + 1;
    tones[0].upper_divider_q16 = tones[0].lower_divider_q16 + 1;
    CHECK(rp1_gpclk_execution_tones_valid(
              tones, 1, RP1_GPCLK_DRIVE_MA_2) == 0);
    tones[0].lower_divider_q16 = (65534ULL << 16) + 1;
    tones[0].upper_divider_q16 = tones[0].lower_divider_q16 + 1;
    CHECK(rp1_gpclk_execution_tones_valid(
              tones, 1, RP1_GPCLK_DRIVE_MA_2) == 0);
    tones[0].lower_divider_q16 = (65535ULL << 16) + 1;
    tones[0].upper_divider_q16 = tones[0].lower_divider_q16 + 1;
    CHECK(rp1_gpclk_execution_tones_valid(
              tones, 1, RP1_GPCLK_DRIVE_MA_2) == 0);
    tones[0].lower_divider_q16 = 0xffffffffULL - 1;
    tones[0].upper_divider_q16 = 0xffffffffULL;
    CHECK(rp1_gpclk_execution_tones_valid(
              tones, 1, RP1_GPCLK_DRIVE_MA_2) == 0);
    tones[0].lower_divider_q16 = 0xffffffffULL;
    tones[0].upper_divider_q16 = 0x100000000ULL;
    CHECK(rp1_gpclk_execution_tones_valid(
              tones, 1, RP1_GPCLK_DRIVE_MA_2) != 0);
    tones[0].lower_divider_q16 = 0x100000000ULL;
    tones[0].upper_divider_q16 = 0x100000001ULL;
    CHECK(rp1_gpclk_execution_tones_valid(
              tones, 1, RP1_GPCLK_DRIVE_MA_2) != 0);
    tones[0].lower_divider_q16 = (368ULL << 16) + 7;
    tones[0].upper_divider_q16 = tones[0].lower_divider_q16 + 2;
    CHECK(rp1_gpclk_execution_tones_valid(
              tones, 1, RP1_GPCLK_DRIVE_MA_2) != 0);
    tones[0].lower_divider_q16 = (368ULL << 16) + 0xffff;
    tones[0].upper_divider_q16 = tones[0].lower_divider_q16 + 1;
    CHECK(rp1_gpclk_execution_tones_valid(
              tones, 1, RP1_GPCLK_DRIVE_MA_2) != 0);
    tones[0].lower_divider_q16 = 1;
    tones[0].upper_divider_q16 = 2;
    CHECK(rp1_gpclk_execution_tones_valid(
              tones, 1, RP1_GPCLK_DRIVE_MA_2) != 0);
    tones[0].lower_divider_q16 = (1ULL << 16) + 1;
    tones[0].upper_divider_q16 = tones[0].lower_divider_q16 + 1;
    CHECK(rp1_gpclk_execution_tones_valid(
              tones, 1, RP1_GPCLK_DRIVE_MA_2) == 0);

    tones[0].lower_divider_q16 = (3ULL << 16) + 10;
    tones[0].upper_divider_q16 = tones[0].lower_divider_q16 + 1;

    CHECK(rp1_gpclk_execution_event_writes(10000000ULL, &writes) == 0);
    CHECK(writes == 978);
    CHECK(rp1_gpclk_execution_event_writes(1, &writes) != 0);
    CHECK(rp1_gpclk_execution_event_writes(0, &writes) != 0);
    CHECK(rp1_gpclk_execution_event_writes(10000000ULL, NULL) != 0);

    CHECK(rp1_gpclk_execution_fill_words(&tones[0], words, 8) == 0);
    CHECK(words[0] == 11U << 16);
    CHECK(words[1] == 11U << 16);
    CHECK(words[2] == 11U << 16);
    CHECK(words[3] == 10U << 16);
    CHECK(words[4] == 11U << 16);
    CHECK(words[7] == 10U << 16);
    CHECK(rp1_gpclk_execution_fill_words(&tones[0], words, 0) != 0);
    CHECK(rp1_gpclk_execution_fill_words(NULL, words, 1) != 0);

    puts("execution policy: PASS (divider envelope, pacing, packing)");
    return 0;
}
