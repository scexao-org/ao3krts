/*
 * device.h -- Definitions for functions for interface with server and device
 *             handler
 *
 * 2008/12/08 Makoto WATANABE -- Initial version
 */

#ifndef _DEVICE_H
#define _DEVICE_H

#include "server.h"				/* for client_t */

/* Structure to store pointer of operation functions of device handler */

struct device_operations {
	int (*init)(void *data, const char *header);
	int (*free)(void *data);
	int (*open)(void *data);
	int (*close)(void *data);
	int (*procconf)(void *data, const char *sect, int argc, const char **argv);
	int (*postconf)(void *data);
	int (*proccmd)(client_t *client, void *data);
};

/* Structure to store data to register device into server */

struct device {
	const char *name;			/* id name of device */
	const char *desc;			/* description of device for help */
	void *data;					/* pointer to device data */
	const struct device_operations *ops;	/* device operation functions */
};


/* Structure to pack device and client data */

struct device_workreq {
	struct device *dev;				/* device data */
	client_t *client;				/* client data */
};

#ifdef __cplusplus
extern "C" {
#endif

/* Function prototypes */

int device_init(struct device *devs, int n);
int device_free(struct device *devs, int n);
int device_open(struct device *devs, int n);
int device_close(struct device *devs, int n);
struct device *device_getdev(struct device *devs, int n, const char *name);
int device_procconf(struct device *dev, const char *sect, int argc,
	const char **argv);
int device_postconf(struct device *devs, int n);
void *device_proccmd(struct device_workreq *req);

#ifdef __cplusplus
}
#endif

#endif /* _DEVICE_H */
