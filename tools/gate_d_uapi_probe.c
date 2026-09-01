// SPDX-License-Identifier: MIT
#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <linux/rp1_gpclk.h>

#ifdef __linux__
#include <sys/ioctl.h>
#else
extern int ioctl(int fd, unsigned long request, ...);
#endif

static void fail(const char *message)
{
	perror(message);
	exit(EXIT_FAILURE);
}

int main(int argc, char **argv)
{
	struct rp1_gpclk_query query = { 0 };
	struct rp1_gpclk_acquire acquire = { 0 };
	struct rp1_gpclk_release release = { 0 };
	uint32_t route;
	int fd;

	if (argc != 3 || (strcmp(argv[1], "gpio4") != 0 &&
			  strcmp(argv[1], "gpio20") != 0)) {
		fprintf(stderr, "usage: %s gpio4|gpio20 EXPECTED_BUILD_ID\n", argv[0]);
		return EXIT_FAILURE;
	}
	route = strcmp(argv[1], "gpio4") == 0 ? RP1_GPCLK_ROUTE_GPIO4 :
		RP1_GPCLK_ROUTE_GPIO20;
	fd = open("/dev/rp1-gpclk", O_RDWR | O_CLOEXEC);
	if (fd < 0)
		fail("open");
	query.header.size = sizeof(query);
	if (ioctl(fd, RP1_GPCLK_IOC_QUERY, &query) != 0)
		fail("RP1_GPCLK_IOC_QUERY");
	if (query.header.size != sizeof(query) ||
	    query.header.reserved != 0 || query.header.flags != 0 ||
	    query.route != route ||
	    (query.capabilities & RP1_GPCLK_CAP_LIVE_ELIGIBLE) != 0 ||
	    strcmp(query.module_id, "rp1-gpclk-dkms") != 0 ||
	    strcmp(query.build_id, argv[2]) != 0) {
		fprintf(stderr, "query identity or output gate mismatch\n");
		return EXIT_FAILURE;
	}
	acquire.header.size = sizeof(acquire);
	acquire.expected_route = route;
	acquire.required_capabilities = RP1_GPCLK_CAP_ROUTE_IDENTITY |
		RP1_GPCLK_CAP_COMPAT_IDENTITY | RP1_GPCLK_CAP_CLEANUP_FAULT_LATCH;
	if (ioctl(fd, RP1_GPCLK_IOC_ACQUIRE, &acquire) != 0)
		fail("RP1_GPCLK_IOC_ACQUIRE");
	release.header.size = sizeof(release);
	release.lease_id = acquire.lease_id;
	if (ioctl(fd, RP1_GPCLK_IOC_RELEASE, &release) != 0)
		fail("RP1_GPCLK_IOC_RELEASE");
	if (close(fd) != 0)
		fail("close");
	printf("route=%s build=%s live_eligible=0 released=1\n", argv[1], argv[2]);
	return EXIT_SUCCESS;
}
