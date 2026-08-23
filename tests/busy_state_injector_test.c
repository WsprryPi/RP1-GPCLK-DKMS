// SPDX-License-Identifier: MIT
#include <assert.h>
#include <errno.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#include <linux/rp1_gpclk.h>

#include "../tools/gate_d_busy_injector.h"

struct fixture {
	bool live;
	bool wrong_build;
	bool wrong_route;
	int opens;
	int queries;
	int acquires;
	int releases;
	int closes;
	int waits;
	int notifications;
};

static int fake_open(void *context)
{
	struct fixture *fixture = context;
	fixture->opens++;
	return 7;
}

static int fake_ioctl(void *context, int fd, unsigned long request, void *argument)
{
	struct fixture *fixture = context;
	assert(fd == 7);
	if (request == RP1_GPCLK_IOC_QUERY) {
		struct rp1_gpclk_query_v1 *query = argument;
		fixture->queries++;
		query->abi_min = query->abi_max = RP1_GPCLK_UAPI_ABI_V1;
		query->route = fixture->wrong_route ? RP1_GPCLK_ROUTE_GPIO20 :
			RP1_GPCLK_ROUTE_GPIO4;
		query->capabilities = RP1_GPCLK_CAP_ROUTE_IDENTITY |
			RP1_GPCLK_CAP_COMPAT_IDENTITY |
			RP1_GPCLK_CAP_CLEANUP_FAULT_LATCH;
		if (fixture->live)
			query->capabilities |= RP1_GPCLK_CAP_LIVE_ELIGIBLE;
		strcpy(query->module_id, "rp1-gpclk-dkms");
		strcpy(query->build_id, fixture->wrong_build ? "wrong" : "test-build");
		return 0;
	}
	if (request == RP1_GPCLK_IOC_ACQUIRE) {
		struct rp1_gpclk_acquire_v1 *acquire = argument;
		fixture->acquires++;
		assert((acquire->required_capabilities &
			(RP1_GPCLK_CAP_SUBMIT_WSPR | RP1_GPCLK_CAP_SUBMIT_EVENTS)) == 0);
		acquire->lease_id = 42;
		return 0;
	}
	if (request == RP1_GPCLK_IOC_RELEASE) {
		struct rp1_gpclk_release_v1 *release = argument;
		fixture->releases++;
		assert(release->lease_id == 42);
		return 0;
	}
	assert(!"unexpected or submitting ioctl");
	return -1;
}

static int fake_wait(void *context)
{
	struct fixture *fixture = context;
	fixture->waits++;
	return 0;
}

static int fake_notify(void *context, enum gate_d_busy_mode mode,
		       uint32_t route, bool acquired)
{
	struct fixture *fixture = context;
	assert(route == RP1_GPCLK_ROUTE_GPIO4);
	assert(acquired == (mode == GATE_D_BUSY_OWNER));
	fixture->notifications++;
	return 0;
}

static int fake_close(void *context, int fd)
{
	struct fixture *fixture = context;
	assert(fd == 7);
	fixture->closes++;
	return 0;
}

static int run(enum gate_d_busy_mode mode, struct fixture *fixture,
	       volatile sig_atomic_t *stop, struct gate_d_busy_result *result)
{
	const struct gate_d_busy_config config = {
		.mode = mode,
		.route = RP1_GPCLK_ROUTE_GPIO4,
		.expected_build = "test-build",
		.timeout_seconds = 2,
	};
	const struct gate_d_busy_ops ops = {
		.open_endpoint = fake_open,
		.ioctl_endpoint = fake_ioctl,
		.wait_one_second = fake_wait,
		.notify_ready = fake_notify,
		.close_endpoint = fake_close,
		.context = fixture,
	};
	return gate_d_busy_run(&config, &ops, result, stop);
}

int main(void)
{
	struct fixture fixture = { 0 };
	struct gate_d_busy_result result;
	volatile sig_atomic_t stop = 0;
	struct gate_d_busy_config invalid = {
		.mode = GATE_D_BUSY_OPEN_ONLY, .route = 17,
		.expected_build = "test-build", .timeout_seconds = 1,
	};
	const struct gate_d_busy_ops ops = {
		.open_endpoint = fake_open, .ioctl_endpoint = fake_ioctl,
		.wait_one_second = fake_wait, .notify_ready = fake_notify,
		.close_endpoint = fake_close,
		.context = &fixture,
	};

	assert(gate_d_busy_run(&invalid, &ops, &result, &stop) == -1);
	assert(fixture.opens == 0);
	assert(run(GATE_D_BUSY_OPEN_ONLY, &fixture, &stop, &result) == 0);
	assert(result.ready && result.closed && !result.acquired && !result.released);
	assert(fixture.acquires == 0 && fixture.releases == 0 && fixture.waits == 2 &&
	       fixture.notifications == 1);

	memset(&fixture, 0, sizeof(fixture));
	assert(run(GATE_D_BUSY_OWNER, &fixture, &stop, &result) == 0);
	assert(result.ready && result.acquired && result.released && result.closed);
	assert(fixture.acquires == 1 && fixture.releases == 1);

	memset(&fixture, 0, sizeof(fixture));
	stop = 1;
	assert(run(GATE_D_BUSY_OWNER, &fixture, &stop, &result) == 0);
	assert(result.released && fixture.waits == 0);
	stop = 0;

	memset(&fixture, 0, sizeof(fixture));
	fixture.live = true;
	assert(run(GATE_D_BUSY_OWNER, &fixture, &stop, &result) == -1);
	assert(result.live_eligible && fixture.acquires == 0 && fixture.closes == 1);

	memset(&fixture, 0, sizeof(fixture));
	fixture.wrong_build = true;
	assert(run(GATE_D_BUSY_OWNER, &fixture, &stop, &result) == -1);
	assert(fixture.acquires == 0 && fixture.closes == 1);

	memset(&fixture, 0, sizeof(fixture));
	fixture.wrong_route = true;
	assert(run(GATE_D_BUSY_OWNER, &fixture, &stop, &result) == -1);
	assert(fixture.acquires == 0 && fixture.closes == 1);

	puts("busy-state injector: PASS");
	return 0;
}
