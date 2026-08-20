// SPDX-License-Identifier: MIT
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>

static int boot_path(const char *path)
{
	return path && strstr(path, "boot/firmware/");
}

int link(const char *oldpath, const char *newpath)
{
	static int (*real_link)(const char *, const char *);

	if (boot_path(oldpath) || boot_path(newpath)) {
		errno = EPERM;
		return -1;
	}
	if (!real_link)
		real_link = dlsym(RTLD_NEXT, "link");
	return real_link(oldpath, newpath);
}

int linkat(int olddirfd, const char *oldpath, int newdirfd,
	   const char *newpath, int flags)
{
	static int (*real_linkat)(int, const char *, int, const char *, int);

	if (boot_path(oldpath) || boot_path(newpath)) {
		errno = EPERM;
		return -1;
	}
	if (!real_linkat)
		real_linkat = dlsym(RTLD_NEXT, "linkat");
	return real_linkat(olddirfd, oldpath, newdirfd, newpath, flags);
}
