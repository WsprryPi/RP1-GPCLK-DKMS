// SPDX-License-Identifier: MIT
#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#include <linux/rp1_gpclk.h>

#define PHASE4A_CAPABILITIES                                                  \
	(RP1_GPCLK_CAP_SUBMIT_WSPR | RP1_GPCLK_CAP_SUBMIT_EVENTS |             \
	 RP1_GPCLK_CAP_STOP_DRAIN | RP1_GPCLK_CAP_STABLE_STATE |                \
	 RP1_GPCLK_CAP_ROUTE_IDENTITY | RP1_GPCLK_CAP_COMPAT_IDENTITY |         \
	 RP1_GPCLK_CAP_CLEANUP_FAULT_LATCH)

static int provider_open(void)
{
	int fd = open("/dev/rp1-gpclk", O_RDONLY | O_CLOEXEC);

	if (fd < 0) {
		perror("open");
		exit(EXIT_FAILURE);
	}
	return fd;
}

static uint32_t parse_route(const char *value)
{
	char *end = NULL;
	unsigned long route = strtoul(value, &end, 10);

	if (!value[0] || !end || *end ||
	    (route != RP1_GPCLK_ROUTE_GPIO4 &&
	     route != RP1_GPCLK_ROUTE_GPIO20)) {
		fprintf(stderr, "route must be 1 or 2\n");
		exit(EXIT_FAILURE);
	}
	return (uint32_t)route;
}

static struct rp1_gpclk_acquire_v1 acquire_request(uint32_t route)
{
	struct rp1_gpclk_acquire_v1 request = { 0 };

	request.header.size = sizeof(request);
	request.header.version = RP1_GPCLK_UAPI_ABI_V1;
	request.expected_route = route;
	request.required_capabilities = PHASE4A_CAPABILITIES;
	return request;
}

static void release_lease(int fd, uint64_t lease)
{
	struct rp1_gpclk_release_v1 request = { 0 };

	request.header.size = sizeof(request);
	request.header.version = RP1_GPCLK_UAPI_ABI_V1;
	request.lease_id = lease;
	if (ioctl(fd, RP1_GPCLK_IOC_RELEASE, &request)) {
		perror("release");
		exit(EXIT_FAILURE);
	}
}

static int inert_submission(int fd, uint64_t lease)
{
	struct rp1_gpclk_submit_events_v1 request = { 0 };

	request.header.size = sizeof(request);
	request.header.version = RP1_GPCLK_UAPI_ABI_V1;
	request.lease_id = lease;
	request.mode = RP1_GPCLK_MODE_QRSS;
	request.fractional_bits = RP1_GPCLK_FRACTIONAL_BITS;
	request.tick_divider = RP1_GPCLK_TICK_DIVIDER;
	request.tone_count = 1;
	request.event_count = 1;
	request.drive_ma = RP1_GPCLK_DRIVE_MA_2;
	request.total_duration_ns = 10000000ULL;
	errno = 0;
	if (ioctl(fd, RP1_GPCLK_IOC_SUBMIT_EVENTS, &request) == 0 ||
	    errno != EACCES) {
		fprintf(stderr, "output-inhibited submission did not fail EACCES\n");
		return EXIT_FAILURE;
	}
	return EXIT_SUCCESS;
}

int main(int argc, char **argv)
{
	struct rp1_gpclk_acquire_v1 acquire;
	uint32_t route;
	int fd;

	if (argc < 3) {
		fprintf(stderr,
			"usage: %s query|once|inert|expect-busy|expect-mismatch|hold ROUTE [marker]\n",
			argv[0]);
		return EXIT_FAILURE;
	}
	route = parse_route(argv[2]);
	fd = provider_open();
	if (!strcmp(argv[1], "query")) {
		struct rp1_gpclk_query_v1 query = { 0 };

		query.header.size = sizeof(query);
		query.header.version = RP1_GPCLK_UAPI_ABI_V1;
		if (ioctl(fd, RP1_GPCLK_IOC_QUERY, &query)) {
			perror("query");
			return EXIT_FAILURE;
		}
		if (query.route != route ||
		    query.compatibility_state !=
			RP1_GPCLK_COMPAT_COMPATIBLE_UNQUALIFIED ||
		    query.compatibility_reason !=
			RP1_GPCLK_COMPAT_REASON_ADMIN_ENROLLMENT_REQUIRED ||
		    query.capabilities != PHASE4A_CAPABILITIES ||
		    query.supported_drive_ma_mask !=
			RP1_GPCLK_DRIVE_SUPPORT_2_MA ||
		    strcmp(query.module_id, "rp1-gpclk-dkms") ||
		    strcmp(query.build_id, "0.0.0-phase4c-gpio20") ||
		    strcmp(query.compatibility_id,
			   "phase4c-wspr5-gpio20-6.18.34")) {
			fprintf(stderr, "Phase 4A query identity mismatch\n");
			return EXIT_FAILURE;
		}
		printf("route=%u state=%u caps=0x%llx build=%s compat=%s\n",
			query.route, query.compatibility_state,
			(unsigned long long)query.capabilities, query.build_id,
			query.compatibility_id);
		return EXIT_SUCCESS;
	}

	acquire = acquire_request(route);
	if (!strcmp(argv[1], "expect-mismatch")) {
		acquire.expected_route = route == RP1_GPCLK_ROUTE_GPIO4 ?
			RP1_GPCLK_ROUTE_GPIO20 : RP1_GPCLK_ROUTE_GPIO4;
		if (ioctl(fd, RP1_GPCLK_IOC_ACQUIRE, &acquire) == 0 ||
		    errno != EINVAL)
			return EXIT_FAILURE;
		return EXIT_SUCCESS;
	}
	if (ioctl(fd, RP1_GPCLK_IOC_ACQUIRE, &acquire)) {
		if (!strcmp(argv[1], "expect-busy") && errno == EBUSY)
			return EXIT_SUCCESS;
		perror("acquire");
		return EXIT_FAILURE;
	}
	if (!strcmp(argv[1], "expect-busy"))
		return EXIT_FAILURE;
	if (!strcmp(argv[1], "inert")) {
		int result = inert_submission(fd, acquire.lease_id);

		release_lease(fd, acquire.lease_id);
		return result;
	}
	if (!strcmp(argv[1], "once")) {
		release_lease(fd, acquire.lease_id);
		return EXIT_SUCCESS;
	}
	if (strcmp(argv[1], "hold") || argc != 4)
		return EXIT_FAILURE;
	{
		FILE *marker = fopen(argv[3], "w");

		if (!marker)
			return EXIT_FAILURE;
		fprintf(marker, "%ld %llu\n", (long)getpid(),
			(unsigned long long)acquire.lease_id);
		if (fclose(marker))
			return EXIT_FAILURE;
	}
	for (;;)
		pause();
}
