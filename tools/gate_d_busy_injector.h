/* SPDX-License-Identifier: MIT */
#ifndef GATE_D_BUSY_INJECTOR_H
#define GATE_D_BUSY_INJECTOR_H

#include <stdbool.h>
#include <signal.h>
#include <stdint.h>

enum gate_d_busy_mode {
	GATE_D_BUSY_OPEN_ONLY = 1,
	GATE_D_BUSY_OWNER = 2,
};

struct gate_d_busy_config {
	enum gate_d_busy_mode mode;
	uint32_t route;
	const char *expected_build;
	unsigned int timeout_seconds;
};

struct gate_d_busy_ops {
	int (*open_endpoint)(void *context);
	int (*ioctl_endpoint)(void *context, int fd, unsigned long request,
			      void *argument);
	int (*wait_one_second)(void *context);
	int (*notify_ready)(void *context, enum gate_d_busy_mode mode,
			    uint32_t route, bool acquired);
	int (*close_endpoint)(void *context, int fd);
	void *context;
};

struct gate_d_busy_result {
	bool ready;
	bool acquired;
	bool released;
	bool closed;
	bool live_eligible;
	uint64_t lease_id;
	unsigned int elapsed_seconds;
};

int gate_d_busy_run(const struct gate_d_busy_config *config,
		    const struct gate_d_busy_ops *ops,
		    struct gate_d_busy_result *result,
		    const volatile sig_atomic_t *stop_requested);

#endif
