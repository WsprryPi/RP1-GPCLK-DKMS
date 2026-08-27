// SPDX-License-Identifier: MIT
#define _GNU_SOURCE
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

#define PARENT_HZ 49997248.0L
#define PERIOD 66792U

static void header(struct rp1_gpclk_uapi_header *value, size_t size, uint16_t version)
{
	value->size = (uint16_t)size;
	value->version = version;
}

static void tone(struct rp1_gpclk_tone_v1 *out, long double frequency)
{
	long double ideal = PARENT_HZ * 65536.0L / frequency;
	uint64_t lower = (uint64_t)floorl(ideal);
	long double lower_frequency = PARENT_HZ * 65536.0L / (long double)lower;
	long double upper_frequency = PARENT_HZ * 65536.0L / (long double)(lower + 1);
	long double ratio = (frequency - upper_frequency) /
		(lower_frequency - upper_frequency);

	out->lower_divider_q16 = lower;
	out->upper_divider_q16 = lower + 1;
	out->lower_count = (uint32_t)llroundl(ratio * PERIOD);
	out->upper_count = PERIOD - out->lower_count;
}

int main(int argc, char **argv)
{
	struct rp1_gpclk_query_v2 query = { 0 };
	struct rp1_gpclk_acquire_v1 acquire = { 0 };
	struct rp1_gpclk_submit_tone_v2 submit = { 0 };
	struct rp1_gpclk_state_v1 state = { 0 };
	struct rp1_gpclk_release_v2 release = { 0 };
	const char *route_environment = getenv("RP1_GPCLK_TEST_ROUTE");
	const char *compatibility_id;
	uint32_t expected_route = RP1_GPCLK_ROUTE_GPIO20;
	uint32_t operation;
	int fd;

	if (route_environment && !strcmp(route_environment, "4"))
		expected_route = RP1_GPCLK_ROUTE_GPIO4;
	else if (route_environment && strcmp(route_environment, "20")) {
		fprintf(stderr, "RP1_GPCLK_TEST_ROUTE must be 4 or 20\n");
		return 2;
	}
	compatibility_id = expected_route == RP1_GPCLK_ROUTE_GPIO4 ?
		"v1.1.2-pi5-gpio4-6.18.34-development-candidate-r4" :
		"v1.1.2-pi5-gpio20-6.18.34-development-candidate-r4";
	if (argc != 2 || (strcmp(argv[1], "finite") && strcmp(argv[1], "continuous")))
		return 2;
	operation = !strcmp(argv[1], "finite") ?
		RP1_GPCLK_TONE_OPERATION_FINITE : RP1_GPCLK_TONE_OPERATION_CONTINUOUS;
	fd = open("/dev/rp1-gpclk", O_RDONLY | O_CLOEXEC);
	if (fd < 0) { perror("open"); return 1; }
	header(&query.header, sizeof(query), RP1_GPCLK_UAPI_ABI_V2);
	if (ioctl(fd, RP1_GPCLK_IOC_QUERY_V2, &query)) { perror("QUERY_V2"); return 1; }
	if (query.route != expected_route || strcmp(query.build_id, "1.1.2") ||
	    strcmp(query.compatibility_id, compatibility_id) ||
	    !(query.capabilities & RP1_GPCLK_CAP_LIVE_ELIGIBLE))
		return 1;
	header(&acquire.header, sizeof(acquire), RP1_GPCLK_UAPI_ABI_V1);
	acquire.expected_route = expected_route;
	acquire.required_capabilities = RP1_GPCLK_CAP_LIVE_ELIGIBLE |
		RP1_GPCLK_CAP_TONE_CONTINUOUS | RP1_GPCLK_CAP_TONE_FINITE;
	if (ioctl(fd, RP1_GPCLK_IOC_ACQUIRE, &acquire)) { perror("ACQUIRE"); return 1; }
	header(&submit.header, sizeof(submit), RP1_GPCLK_UAPI_ABI_V2);
	submit.lease_id = acquire.lease_id;
	tone(&submit.tone, 10140200.0L);
	submit.duration_ns = operation == RP1_GPCLK_TONE_OPERATION_FINITE ?
		1000000000ULL : 0;
	submit.operation = operation;
	submit.expected_route = expected_route;
	submit.fractional_bits = RP1_GPCLK_FRACTIONAL_BITS;
	submit.tick_divider = RP1_GPCLK_TICK_DIVIDER;
	submit.drive_ma = RP1_GPCLK_DRIVE_MA_2;
	if (ioctl(fd, RP1_GPCLK_IOC_SUBMIT_TONE_V2, &submit)) { perror("TONE_V2"); return 1; }
	if (operation == RP1_GPCLK_TONE_OPERATION_CONTINUOUS) {
		struct rp1_gpclk_stop_v1 stop = { 0 };
		struct timespec delay = { .tv_sec = 1 };
		nanosleep(&delay, NULL);
		header(&stop.header, sizeof(stop), RP1_GPCLK_UAPI_ABI_V1);
		stop.lease_id = acquire.lease_id;
		stop.generation = submit.generation;
		if (ioctl(fd, RP1_GPCLK_IOC_STOP, &stop)) { perror("STOP"); return 1; }
	}
	for (;;) {
		struct timespec delay = { .tv_nsec = 10000000L };
		memset(&state, 0, sizeof(state));
		header(&state.header, sizeof(state), RP1_GPCLK_UAPI_ABI_V1);
		state.lease_id = acquire.lease_id;
		state.generation = submit.generation;
		if (ioctl(fd, RP1_GPCLK_IOC_GET_STATE, &state)) { perror("STATE"); return 1; }
		if (state.state == RP1_GPCLK_STATE_COMPLETE || state.state == RP1_GPCLK_STATE_FAILED)
			break;
		nanosleep(&delay, NULL);
	}
	printf("tone=%s generation=%llu state=%u reason=%u cleanup=%u elapsed_ns=%llu\n",
	       argv[1], (unsigned long long)state.generation, state.state,
	       state.terminal_reason, state.cleanup_fault,
	       (unsigned long long)state.elapsed_ns);
	if (state.state != RP1_GPCLK_STATE_COMPLETE || state.cleanup_fault ||
	    state.terminal_reason != (operation == RP1_GPCLK_TONE_OPERATION_FINITE ?
		RP1_GPCLK_REASON_COMPLETE : RP1_GPCLK_REASON_STOPPED))
		return 1;
	header(&release.header, sizeof(release), RP1_GPCLK_UAPI_ABI_V2);
	release.lease_id = acquire.lease_id;
	release.generation = submit.generation;
	if (ioctl(fd, RP1_GPCLK_IOC_RELEASE_V2, &release)) { perror("RELEASE_V2"); return 1; }
	close(fd);
	return 0;
}
