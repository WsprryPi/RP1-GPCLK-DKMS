// SPDX-License-Identifier: MIT
#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <time.h>
#include <unistd.h>

#include <linux/rp1_gpclk.h>

/* Frozen from the failed uncorrected sentinel: -58.41 ppm versus RSP1B. */
#define PARENT_HZ 49997248.0L
#define PERIOD 66792U
#define REQUIRED_CAPS (RP1_GPCLK_CAP_SUBMIT_EVENTS | \
	RP1_GPCLK_CAP_STOP_DRAIN | RP1_GPCLK_CAP_STABLE_STATE | \
	RP1_GPCLK_CAP_ROUTE_IDENTITY | RP1_GPCLK_CAP_COMPAT_IDENTITY | \
	RP1_GPCLK_CAP_CLEANUP_FAULT_LATCH | RP1_GPCLK_CAP_LIVE_ELIGIBLE)

static void header(struct rp1_gpclk_uapi_header *value, size_t size)
{
	value->size = (uint16_t)size;
	value->version = RP1_GPCLK_UAPI_ABI_V1;
}

static void tone(struct rp1_gpclk_tone_v1 *out, long double frequency)
{
	long double ideal = PARENT_HZ * 65536.0L / frequency;
	long double lower_frequency;
	long double upper_frequency;
	long double ratio;
	uint64_t lower = (uint64_t)floorl(ideal);
	uint64_t upper = lower + 1;

	lower_frequency = PARENT_HZ * 65536.0L / (long double)lower;
	upper_frequency = PARENT_HZ * 65536.0L / (long double)upper;
	ratio = (frequency - upper_frequency) /
		(lower_frequency - upper_frequency);
	out->lower_divider_q16 = lower;
	out->upper_divider_q16 = upper;
	out->lower_count = (uint32_t)llroundl(ratio * PERIOD);
	out->upper_count = PERIOD - out->lower_count;
}

static void release_lease(int fd, uint64_t lease)
{
	struct rp1_gpclk_release_v1 request = { 0 };

	header(&request.header, sizeof(request));
	request.lease_id = lease;
	if (ioctl(fd, RP1_GPCLK_IOC_RELEASE, &request)) {
		perror("RELEASE");
		exit(EXIT_FAILURE);
	}
}

int main(int argc, char **argv)
{
	struct rp1_gpclk_query_v1 query = { 0 };
	struct rp1_gpclk_acquire_v1 acquire = { 0 };
	struct rp1_gpclk_submit_events_v1 submit = { 0 };
	struct rp1_gpclk_tone_v1 tones[2] = { 0 };
	struct rp1_gpclk_event_v1 events[16] = { 0 };
	struct rp1_gpclk_state_v1 state = { 0 };
	uint32_t mode;
	uint32_t count;
	uint32_t i;
	int cancel = 0;
	int fd;

	if (argc != 2 || (strcmp(argv[1], "query") &&
	    strcmp(argv[1], "qrss") && strcmp(argv[1], "fskcw") &&
	    strcmp(argv[1], "dfcw") && strcmp(argv[1], "cancel"))) {
		fprintf(stderr, "usage: %s query|qrss|fskcw|dfcw|cancel\n", argv[0]);
		return EXIT_FAILURE;
	}
	fd = open("/dev/rp1-gpclk", O_RDONLY | O_CLOEXEC);
	if (fd < 0) { perror("open"); return EXIT_FAILURE; }
	header(&query.header, sizeof(query));
	if (ioctl(fd, RP1_GPCLK_IOC_QUERY, &query)) {
		perror("QUERY"); return EXIT_FAILURE;
	}
	printf("query route=%u state=%u reason=%u caps=0x%llx build=%s compat=%s\n",
	       query.route, query.compatibility_state, query.compatibility_reason,
	       (unsigned long long)query.capabilities, query.build_id,
	       query.compatibility_id);
	if (query.route != RP1_GPCLK_ROUTE_GPIO4 ||
	    query.compatibility_state != RP1_GPCLK_COMPAT_EXPERIMENTAL ||
	    (query.capabilities & REQUIRED_CAPS) != REQUIRED_CAPS ||
	    strcmp(query.build_id, "0.0.0-phase4b-gpio4") ||
	    strcmp(query.compatibility_id, "phase4b-wspr5-gpio4-6.18.34"))
		return EXIT_FAILURE;
	if (!strcmp(argv[1], "query")) return EXIT_SUCCESS;

	header(&acquire.header, sizeof(acquire));
	acquire.expected_route = RP1_GPCLK_ROUTE_GPIO4;
	acquire.required_capabilities = REQUIRED_CAPS;
	if (ioctl(fd, RP1_GPCLK_IOC_ACQUIRE, &acquire)) {
		perror("ACQUIRE"); return EXIT_FAILURE;
	}
	tone(&tones[0], 10140200.0L);
	tone(&tones[1], 10140220.0L);
	if (!strcmp(argv[1], "qrss")) {
		mode = RP1_GPCLK_MODE_QRSS; count = 1;
		events[0].duration_ns = 1000000000ULL;
		events[0].flags = RP1_GPCLK_EVENT_F_OUTPUT_ENABLED;
	} else if (!strcmp(argv[1], "fskcw")) {
		mode = RP1_GPCLK_MODE_FSKCW; count = 6;
		for (i = 0; i < count; i++) {
			events[i].duration_ns = 1000000000ULL;
			events[i].tone_index = i & 1;
			events[i].flags = RP1_GPCLK_EVENT_F_OUTPUT_ENABLED;
		}
	} else if (!strcmp(argv[1], "dfcw")) {
		mode = RP1_GPCLK_MODE_DFCW; count = 8;
		for (i = 0; i < count; i++) {
			events[i].duration_ns = (i & 1) ? 500000000ULL : 1000000000ULL;
			events[i].tone_index = (i / 2) & 1;
			if (!(i & 1)) events[i].flags = RP1_GPCLK_EVENT_F_OUTPUT_ENABLED;
		}
	} else {
		mode = RP1_GPCLK_MODE_QRSS; count = 8; cancel = 1;
		for (i = 0; i < count; i++) {
			events[i].duration_ns = 1000000000ULL;
			events[i].flags = RP1_GPCLK_EVENT_F_OUTPUT_ENABLED;
		}
	}
	header(&submit.header, sizeof(submit));
	submit.lease_id = acquire.lease_id;
	submit.tones_ptr = (uintptr_t)tones;
	submit.events_ptr = (uintptr_t)events;
	submit.mode = mode;
	submit.fractional_bits = RP1_GPCLK_FRACTIONAL_BITS;
	submit.tick_divider = RP1_GPCLK_TICK_DIVIDER;
	submit.tone_count = 2;
	submit.event_count = count;
	submit.drive_ma = RP1_GPCLK_DRIVE_MA_2;
	for (i = 0; i < count; i++) submit.total_duration_ns += events[i].duration_ns;
	if (ioctl(fd, RP1_GPCLK_IOC_SUBMIT_EVENTS, &submit)) {
		perror("SUBMIT_EVENTS"); release_lease(fd, acquire.lease_id);
		return EXIT_FAILURE;
	}
	if (cancel) {
		struct rp1_gpclk_stop_v1 stop = { 0 };
		struct timespec delay = { .tv_sec = 0, .tv_nsec = 500000000L };
		nanosleep(&delay, NULL);
		header(&stop.header, sizeof(stop));
		stop.lease_id = acquire.lease_id;
		stop.generation = submit.generation;
		if (ioctl(fd, RP1_GPCLK_IOC_STOP, &stop)) {
			perror("STOP"); return EXIT_FAILURE;
		}
	}
	for (;;) {
		struct timespec delay = { .tv_sec = 0, .tv_nsec = 10000000L };
		memset(&state, 0, sizeof(state));
		header(&state.header, sizeof(state));
		state.lease_id = acquire.lease_id;
		state.generation = submit.generation;
		if (ioctl(fd, RP1_GPCLK_IOC_GET_STATE, &state)) {
			perror("GET_STATE"); return EXIT_FAILURE;
		}
		if (state.state == RP1_GPCLK_STATE_COMPLETE ||
		    state.state == RP1_GPCLK_STATE_FAILED) break;
		nanosleep(&delay, NULL);
	}
	printf("terminal generation=%llu state=%u reason=%u event=%u cleanup=%u elapsed_ns=%llu remaining_ns=%llu\n",
	       (unsigned long long)state.generation, state.state,
	       state.terminal_reason, state.current_event, state.cleanup_fault,
	       (unsigned long long)state.elapsed_ns,
	       (unsigned long long)state.remaining_ns);
	if (state.state != RP1_GPCLK_STATE_COMPLETE || state.cleanup_fault ||
	    state.terminal_reason != (cancel ? RP1_GPCLK_REASON_STOPPED :
		RP1_GPCLK_REASON_COMPLETE)) return EXIT_FAILURE;
	release_lease(fd, acquire.lease_id);
	return EXIT_SUCCESS;
}
