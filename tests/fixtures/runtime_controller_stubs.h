/* SPDX-License-Identifier: MIT */
#ifndef RUNTIME_CONTROLLER_STUBS_H
#define RUNTIME_CONTROLLER_STUBS_H
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <limits.h>
#include <assert.h>
#include <stdio.h>
typedef uint32_t __u32;
typedef uint64_t __u64;
typedef int32_t __s32;
typedef uint64_t u64;
#define __user
#define __init
#define __exit
#define __aligned(x) __attribute__((aligned(x)))
#define CONFIG_OF_OVERLAY 1
#define IS_ENABLED(x) (x)
#define U64_MAX UINT64_MAX
#define CAP_SYS_ADMIN 1
#define THIS_MODULE ((void *)1)
#define MISC_DYNAMIC_MINOR 1
#define _IOWR(a,b,c) 0xc040b801U
#define MODULE_LICENSE(x)
#define MODULE_DESCRIPTION(x)
#define MODULE_VERSION(x)
#define EXPORT_SYMBOL_GPL(x)
#define module_init(x)
#define module_exit(x)
#define DEFINE_MUTEX(x) int x
static bool allowed = true, foreign;
static int references, apply_error, apply_id = 9, remove_error, remove_id;
static int apply_calls, remove_calls, copyout_error;
struct file { int unused; };
struct device_node { int unused; };
static struct device_node node_fixture;
#define ARRAY_SIZE(x) (sizeof(x)/sizeof((x)[0]))
static struct device_node *of_find_compatible_node(void *from, const char *type, const char *name) {
 (void)from; (void)type; (void)name; return foreign ? &node_fixture : NULL;
}
static struct device_node *of_find_node_by_name(void *from, const char *name) {
 (void)from; (void)name; return NULL;
}
static int capable(int cap) { (void)cap; return allowed; }
static int mutex_trylock(int *lock) { if (*lock) return 0; *lock = 1; return 1; }
static void mutex_lock(int *lock) { assert(!*lock); *lock = 1; }
static void mutex_unlock(int *lock) { assert(*lock); *lock = 0; }
static void of_node_put(void *node) { (void)node; }
static int of_machine_is_compatible(const char *name) { (void)name; return true; }
static void __module_get(void *module) { (void)module; references++; }
static void module_put(void *module) { (void)module; assert(references > 0); references--; }
static int copy_from_user(void *to, const void *from, unsigned long size) { memcpy(to, from, size); return 0; }
static int copy_to_user(void *to, const void *from, unsigned long size) { if (copyout_error) return 1; memcpy(to, from, size); return 0; }
static int of_overlay_fdt_apply(const void *data, unsigned int size, int *id, void *base) {
 (void)data; (void)size; (void)base; apply_calls++; *id = apply_id; return apply_error;
}
static int of_overlay_remove(int *id) { assert(*id > 0); remove_calls++; *id = remove_id; return remove_error; }
static u64 get_random_u64(void) { return 1234; }
struct utsname_fixture { const char *release; const char *machine; };
static struct utsname_fixture *utsname(void) {
 static struct utsname_fixture value = {"6.18.34+rpt-rpi-2712", "aarch64"}; return &value;
}
struct file_operations { void *owner; long (*unlocked_ioctl)(struct file *, unsigned int, unsigned long); };
struct miscdevice { int minor; const char *name; const struct file_operations *fops; int mode; };
static int misc_register(struct miscdevice *dev) { (void)dev; return 0; }
static void misc_deregister(struct miscdevice *dev) { (void)dev; }
#endif
