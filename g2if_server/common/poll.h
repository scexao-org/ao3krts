/*
 * poll.h -- Definitions for functions to handle polling work
 *
 * 2008/11/19 Makoto WATANABE -- Initial version
 */

#ifndef _POLL_H
#define _POLL_H

#include <pthread.h>			/* for pthread_* */
#include "server.h"				/* for client_t */

/* Structure for handling polling work */

typedef struct poll {
	int usepoll;				/* flag indicating use of polling */
	int interval;				/* polling interval in seconds */
	int stop;					/* flag to stop polling thread */
	int polling;				/* flag indicating polling is running */
	void *(*routine)(void *);	/* pointer to work routine */
	void *arg;					/* argument for work routine */
	pthread_t tid;				/* id of thread polling */
	pthread_cond_t cv;			/* cv for polling */
	pthread_mutex_t lock;		/* lock of polling data */
	char *header;				/* header string for logging message */
} poll_t;

#ifdef __cplusplus
extern "C" {
#endif

/* Function prototypes */

int poll_init(poll_t *poll, void *(*routine)(void *), void *arg,
	const char *header);
int poll_free(poll_t *poll);
int poll_start(poll_t *poll);
int poll_stop(poll_t *poll);
int poll_setusepoll(poll_t *poll, int usepoll);
int poll_getusepoll(poll_t *poll);
int poll_setinterval(poll_t *poll, int interval);
int poll_getinterval(poll_t *poll);
int poll_isrunning(poll_t *poll);

int poll_cmd_poll(client_t *client, poll_t *poll);
int poll_cmd_interval(client_t *client, poll_t *poll);

#ifdef __cplusplus
}
#endif

#endif /* _POLL_H */
