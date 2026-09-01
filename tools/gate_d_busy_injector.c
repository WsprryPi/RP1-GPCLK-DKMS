// SPDX-License-Identifier: MIT
#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#include <linux/rp1_gpclk.h>

#include "gate_d_busy_injector.h"

#ifdef __linux__
#include <sys/ioctl.h>
#else
extern int ioctl(int fd, unsigned long request, ...);
#endif

static int valid_identity(const struct rp1_gpclk_query *query,
			  const struct gate_d_busy_config *config)
{
	return query->header.size == sizeof(*query) &&
		query->header.reserved == 0 &&
		query->header.flags == 0 &&
		query->route == config->route &&
		(query->capabilities & RP1_GPCLK_CAP_LIVE_ELIGIBLE) == 0 &&
		memchr(query->module_id, '\0', sizeof(query->module_id)) != NULL &&
		memchr(query->build_id, '\0', sizeof(query->build_id)) != NULL &&
		strcmp(query->module_id, "rp1-gpclk-dkms") == 0 &&
		strcmp(query->build_id, config->expected_build) == 0;
}

int gate_d_busy_run(const struct gate_d_busy_config *config,
		    const struct gate_d_busy_ops *ops,
		    struct gate_d_busy_result *result,
		    const volatile sig_atomic_t *stop_requested)
{
	struct rp1_gpclk_query query = { 0 };
	struct rp1_gpclk_acquire acquire = { 0 };
	struct rp1_gpclk_release release = { 0 };
	int fd = -1;
	int rc = -1;

	if (!config || !ops || !result || !stop_requested ||
	    !ops->open_endpoint || !ops->ioctl_endpoint ||
	    !ops->wait_one_second || !ops->notify_ready || !ops->close_endpoint ||
	    !config->expected_build || config->expected_build[0] == '\0' ||
	    (config->route != RP1_GPCLK_ROUTE_GPIO4 &&
	     config->route != RP1_GPCLK_ROUTE_GPIO20) ||
	    (config->mode != GATE_D_BUSY_OPEN_ONLY &&
	     config->mode != GATE_D_BUSY_OWNER) ||
	    config->timeout_seconds == 0 || config->timeout_seconds > 900) {
		errno = EINVAL;
		return -1;
	}
	memset(result, 0, sizeof(*result));
	fd = ops->open_endpoint(ops->context);
	if (fd < 0)
		return -1;
	query.header.size = sizeof(query);
	if (ops->ioctl_endpoint(ops->context, fd, RP1_GPCLK_IOC_QUERY,
				&query) != 0)
		goto out;
	result->live_eligible =
		(query.capabilities & RP1_GPCLK_CAP_LIVE_ELIGIBLE) != 0;
	if (!valid_identity(&query, config)) {
		errno = EPERM;
		goto out;
	}
	if (config->mode == GATE_D_BUSY_OWNER) {
		acquire.header.size = sizeof(acquire);
		acquire.expected_route = config->route;
		acquire.required_capabilities = RP1_GPCLK_CAP_ROUTE_IDENTITY |
			RP1_GPCLK_CAP_COMPAT_IDENTITY |
			RP1_GPCLK_CAP_CLEANUP_FAULT_LATCH;
		if (ops->ioctl_endpoint(ops->context, fd, RP1_GPCLK_IOC_ACQUIRE,
					&acquire) != 0)
			goto out;
		result->acquired = true;
		result->lease_id = acquire.lease_id;
	}
	result->ready = true;
	if (ops->notify_ready(ops->context, config->mode, config->route,
			      result->acquired) != 0)
		goto out;
	for (result->elapsed_seconds = 0;
	     result->elapsed_seconds < config->timeout_seconds && !*stop_requested;
	     result->elapsed_seconds++) {
		if (ops->wait_one_second(ops->context) != 0)
			goto out;
	}
	rc = 0;
out:
	if (result->acquired) {
		release.header.size = sizeof(release);
		release.lease_id = result->lease_id;
		if (ops->ioctl_endpoint(ops->context, fd, RP1_GPCLK_IOC_RELEASE,
					&release) == 0)
			result->released = true;
		else
			rc = -1;
	}
	if (ops->close_endpoint(ops->context, fd) == 0)
		result->closed = true;
	else
		rc = -1;
	return rc;
}

#ifndef GATE_D_BUSY_LIBRARY
static volatile sig_atomic_t stop_requested;

static void stop_handler(int signal_number)
{
	(void)signal_number;
	stop_requested = 1;
}

static int system_open(void *context)
{
	(void)context;
	return open("/dev/rp1-gpclk", O_RDWR | O_CLOEXEC);
}

static int system_ioctl(void *context, int fd, unsigned long request,
			void *argument)
{
	(void)context;
	return ioctl(fd, request, argument);
}

static int system_wait(void *context)
{
	struct timespec interval = { .tv_sec = 1, .tv_nsec = 0 };
	(void)context;
	while (nanosleep(&interval, &interval) != 0) {
		if (errno == EINTR)
			return 0;
		return -1;
	}
	return 0;
}

static int system_notify(void *context, enum gate_d_busy_mode mode,
			 uint32_t route, bool acquired)
{
	(void)context;
	if (printf("{\"event\":\"ready\",\"mode\":\"%s\",\"route\":\"%s\","
		   "\"liveEligible\":false,\"acquired\":%s}\n",
		   mode == GATE_D_BUSY_OPEN_ONLY ? "open" : "owner",
		   route == RP1_GPCLK_ROUTE_GPIO4 ? "gpio4" : "gpio20",
		   acquired ? "true" : "false") < 0)
		return -1;
	return fflush(stdout);
}

static int system_close(void *context, int fd)
{
	(void)context;
	return close(fd);
}

int main(int argc, char **argv)
{
	struct gate_d_busy_config config = { 0 };
	struct gate_d_busy_ops ops = {
		.open_endpoint = system_open,
		.ioctl_endpoint = system_ioctl,
		.wait_one_second = system_wait,
		.notify_ready = system_notify,
		.close_endpoint = system_close,
	};
	struct gate_d_busy_result result;
	struct sigaction action = { 0 };
	char *end = NULL;
	unsigned long timeout;
	int rc;

	if (argc != 5 ||
	    (strcmp(argv[1], "open") != 0 && strcmp(argv[1], "owner") != 0) ||
	    (strcmp(argv[2], "gpio4") != 0 && strcmp(argv[2], "gpio20") != 0)) {
		fprintf(stderr, "usage: %s open|owner gpio4|gpio20 EXPECTED_BUILD_ID TIMEOUT_SECONDS\n",
			argv[0]);
		return EXIT_FAILURE;
	}
	timeout = strtoul(argv[4], &end, 10);
	if (!end || *end != '\0' || timeout == 0 || timeout > 900) {
		fprintf(stderr, "timeout must be 1..900 seconds\n");
		return EXIT_FAILURE;
	}
	config.mode = strcmp(argv[1], "open") == 0 ?
		GATE_D_BUSY_OPEN_ONLY : GATE_D_BUSY_OWNER;
	config.route = strcmp(argv[2], "gpio4") == 0 ?
		RP1_GPCLK_ROUTE_GPIO4 : RP1_GPCLK_ROUTE_GPIO20;
	config.expected_build = argv[3];
	config.timeout_seconds = (unsigned int)timeout;
	action.sa_handler = stop_handler;
	sigemptyset(&action.sa_mask);
	if (sigaction(SIGINT, &action, NULL) != 0 ||
	    sigaction(SIGTERM, &action, NULL) != 0) {
		perror("sigaction");
		return EXIT_FAILURE;
	}
	rc = gate_d_busy_run(&config, &ops, &result, &stop_requested);
	printf("{\"mode\":\"%s\",\"route\":\"%s\",\"ready\":%s,"
	       "\"liveEligible\":%s,\"acquired\":%s,\"released\":%s,"
	       "\"closed\":%s,\"elapsedSeconds\":%u}\n",
	       argv[1], argv[2], result.ready ? "true" : "false",
	       result.live_eligible ? "true" : "false",
	       result.acquired ? "true" : "false",
	       result.released ? "true" : "false",
	       result.closed ? "true" : "false", result.elapsed_seconds);
	return rc == 0 && result.ready && result.closed &&
		(config.mode != GATE_D_BUSY_OWNER || result.released) ?
		EXIT_SUCCESS : EXIT_FAILURE;
}
#endif
