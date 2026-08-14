// SPDX-License-Identifier: MIT
#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#include <linux/rp1_gpclk.h>

static int open_provider(void)
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
		fprintf(stderr, "route must be 1 (GPIO4) or 2 (GPIO20)\n");
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
	request.required_capabilities = RP1_GPCLK_CAP_ROUTE_IDENTITY |
		RP1_GPCLK_CAP_COMPAT_IDENTITY |
		RP1_GPCLK_CAP_CLEANUP_FAULT_LATCH;
	return request;
}

static void release_lease(int fd, uint64_t lease_id)
{
	struct rp1_gpclk_release_v1 request = { 0 };

	request.header.size = sizeof(request);
	request.header.version = RP1_GPCLK_UAPI_ABI_V1;
	request.lease_id = lease_id;
	if (ioctl(fd, RP1_GPCLK_IOC_RELEASE, &request) != 0) {
		perror("RP1_GPCLK_IOC_RELEASE");
		exit(EXIT_FAILURE);
	}
}

int main(int argc, char **argv)
{
	struct rp1_gpclk_acquire_v1 acquire;
	uint32_t route;
	int fd;

	if (argc < 3) {
		fprintf(stderr, "usage: %s query|once|expect-busy|expect-mismatch|hold ROUTE [marker]\n", argv[0]);
		return EXIT_FAILURE;
	}
	route = parse_route(argv[2]);
	acquire = acquire_request(route);
	fd = open_provider();
	if (strcmp(argv[1], "query") == 0) {
		struct rp1_gpclk_query_v1 query = { 0 };

		query.header.size = sizeof(query);
		query.header.version = RP1_GPCLK_UAPI_ABI_V1;
		if (ioctl(fd, RP1_GPCLK_IOC_QUERY, &query) != 0) {
			perror("RP1_GPCLK_IOC_QUERY");
			return EXIT_FAILURE;
		}
		if (query.header.size != sizeof(query) ||
		    query.header.version != RP1_GPCLK_UAPI_ABI_V1 ||
		    query.header.flags != 0 ||
		    query.abi_min != RP1_GPCLK_UAPI_ABI_V1 ||
		    query.abi_max != RP1_GPCLK_UAPI_ABI_V1 ||
		    query.route != route ||
		    query.compatibility_state !=
			RP1_GPCLK_COMPAT_COMPATIBLE_UNQUALIFIED ||
		    query.compatibility_reason !=
			RP1_GPCLK_COMPAT_REASON_ADMIN_ENROLLMENT_REQUIRED ||
		    query.capabilities != (RP1_GPCLK_CAP_ROUTE_IDENTITY |
			RP1_GPCLK_CAP_COMPAT_IDENTITY |
			RP1_GPCLK_CAP_CLEANUP_FAULT_LATCH) ||
		    strcmp(query.module_id, "rp1-gpclk-dkms") != 0 ||
		    strcmp(query.build_id, "0.0.0-phase3b") != 0 ||
		    strcmp(query.compatibility_id,
			   "phase3b-clock-disabled") != 0) {
			fprintf(stderr, "query identity mismatch\n");
			return EXIT_FAILURE;
		}
		printf("abi=%u-%u route=%u state=%u reason=%u capabilities=0x%llx module=%s build=%s compat=%s\n",
			query.abi_min, query.abi_max, query.route,
			query.compatibility_state, query.compatibility_reason,
			(unsigned long long)query.capabilities, query.module_id,
			query.build_id, query.compatibility_id);
		return EXIT_SUCCESS;
	}
	if (strcmp(argv[1], "expect-mismatch") == 0) {
		acquire.expected_route = route == RP1_GPCLK_ROUTE_GPIO4 ?
			RP1_GPCLK_ROUTE_GPIO20 : RP1_GPCLK_ROUTE_GPIO4;
		if (ioctl(fd, RP1_GPCLK_IOC_ACQUIRE, &acquire) == 0) {
			fprintf(stderr, "route mismatch unexpectedly acquired a lease\n");
			return EXIT_FAILURE;
		}
		if (errno != EINVAL) {
			perror("route mismatch");
			return EXIT_FAILURE;
		}
		return EXIT_SUCCESS;
	}
	if (ioctl(fd, RP1_GPCLK_IOC_ACQUIRE, &acquire) != 0) {
		if (strcmp(argv[1], "expect-busy") == 0 && errno == EBUSY)
			return EXIT_SUCCESS;
		perror("RP1_GPCLK_IOC_ACQUIRE");
		return EXIT_FAILURE;
	}
	if (strcmp(argv[1], "expect-busy") == 0) {
		fprintf(stderr, "second owner unexpectedly acquired a lease\n");
		return EXIT_FAILURE;
	}
	if (strcmp(argv[1], "once") == 0) {
		release_lease(fd, acquire.lease_id);
		return EXIT_SUCCESS;
	}
	if (strcmp(argv[1], "hold") != 0 || argc != 4) {
		fprintf(stderr, "invalid operation\n");
		return EXIT_FAILURE;
	}
	{
		FILE *marker = fopen(argv[3], "w");

		if (!marker) {
			perror("fopen marker");
			return EXIT_FAILURE;
		}
		fprintf(marker, "%ld %llu\n", (long)getpid(),
			(unsigned long long)acquire.lease_id);
		if (fclose(marker) != 0) {
			perror("fclose marker");
			return EXIT_FAILURE;
		}
	}
	for (;;)
		pause();
}
