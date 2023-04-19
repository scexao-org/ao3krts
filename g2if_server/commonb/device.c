/*
 * device.c -- Functions for interface with server and device handler
 *
 * 2008/12/08 Makoto WATANABE -- Initial version
 */

#include <string.h>				/* for strcmp() */
#include "log.h"				/* for error(), info(), debug() */
#include "server.h"				/* for client_t */
#include "device.h"				/* for struct device */

/*
 * Initialize structures of all devices
 */
int device_init(struct device *devs, int n)
{
	int i, j, ret = 0;
	struct device *dev;
	int (*dev_init)(void *, const char *);
	int (*dev_free)(void *);

	/* Call init routines of devices sequentially */
	for (i = 0; i < n; i++) {
		dev = &(devs[i]);
		dev_init = dev->ops->init;
		if (dev_init != NULL) {
			if ((ret = (*dev_init)(dev->data, dev->name)) < 0) {
				break;
			}
		}
	}

	/* Call free routines of devices sequentially */
	if (ret < 0) {
		for (j = 0; j < i; j++) {
			dev = &(devs[j]);
			dev_free = dev->ops->free;
			if (dev_free != NULL) {
				(*dev_free)(dev->data);
			}
		}
	}
	
	return ret;
}

/*
 * Free memory for data of all devices
 */
int device_free(struct device *devs, int n)
{
	int i;
	struct device *dev;
	int (*dev_free)(void *);

	for (i = 0; i < n; i++) {
		dev = &(devs[i]);
		dev_free = dev->ops->free;
		if (dev_free != NULL) {
			(*dev_free)(dev->data);
		}
	}

	return 0;
}

/*
 * Open all devices
 */
int device_open(struct device *devs, int n)
{
	int i, ret;
	struct device *dev;
	int (*dev_open)(void *);

	for (i = 0; i < n; i++) {
		dev = &(devs[i]);
		dev_open = dev->ops->open;
		if (dev_open != NULL) {
/*			debug("%s: open", dev->name); */
			if ((ret = (*dev_open)(dev->data)) < 0) {
				return ret;
			}
		}
	}

	return 0;
}

/*
 * Close all devices
 */
int device_close(struct device *devs, int n)
{
	int i;
	struct device *dev;
	int (*dev_close)(void *);

	for (i = 0; i < n; i++) {
		dev = &(devs[i]);
		dev_close = dev->ops->close;
		if (dev_close != NULL) {
/*			debug("%s: close", dev->name); */
			(*dev_close)(dev->data);
		}
	}

	return 0;
}

/*
 * Find device by name
 */
struct device *device_getdev(struct device *devs, int n, const char *name)
{
	int i;
	struct device *dev, *dev_find = NULL;

	for (i = 0; i < n; i++) {
		dev = &(devs[i]);
		if (dev->name != NULL && strcmp(name, dev->name) == 0) {
			dev_find = dev;
			break;
		}
	}

	return dev_find;
}

/*
 * Process a configuration parameter of device
 */
int device_procconf(struct device *dev, const char *sect, int argc,
	const char **argv)
{
	int (*dev_procconf)(void *, const char *, int, const char **);

	dev_procconf = dev->ops->procconf;
	if (dev_procconf == NULL) {
		return 0;
	}

	return (*dev_procconf)(dev->data, sect, argc, argv);
}

/*
 * Open all devices
 */
int device_postconf(struct device *devs, int n)
{
	int i, ret;
	struct device *dev;
	int (*dev_postconf)(void *);

	for (i = 0; i < n; i++) {
		dev = &(devs[i]);
		dev_postconf = dev->ops->postconf;
		if (dev_postconf != NULL) {
			if ((ret = (*dev_postconf)(dev->data)) < 0) {
				return ret;
			}
		}
	}

	return 0;
}

/*
 * Process an operation command of device
 */
void *device_proccmd(struct device_workreq *req)
{
	struct device *dev = req->dev;
	client_t *client = req->client;
	int (*dev_proccmd)(client_t *, void *);

	dev_proccmd = dev->ops->proccmd;
	if (dev_proccmd == NULL) {
		return 0;
	}

	(*dev_proccmd)(client, dev->data);

	return NULL;
}
