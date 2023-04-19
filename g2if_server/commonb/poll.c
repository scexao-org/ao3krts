/*
 * poll.c -- Functions to handle polling work
 *
 * 2008/11/19 Makoto WATANABE -- Initial version
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE			/* for for using GNU version of strerror_r() */
#endif /* _GNU_SOURCE */

#include <stdlib.h>				/* for free() */
#include <string.h>				/* for strdup() */
#include <pthread.h>			/* for pthread_*() */
#include <sys/time.h>			/* for gettimeofday() */
#include <errno.h>				/* for errno */
#include <limits.h>                             /* for USHRT_MAX */
#include "log.h"				/* for error(), info(), debug() */
#include "server.h"				/* for sendres(), sendres_*() */
#include "stringx.h"			/* for strtolower() */
#include "poll.h"				/* for poll_t */

/*
 * Initialize data for polling work
 */
int poll_init(poll_t *poll, void *(*routine)(void *), void *arg,
	const char *header)
{
	if (header != NULL) {
		poll->header = strdup(header);
	} else {
		poll->header = strdup("poll");
	}
	if (poll->header == NULL) {
		error_num(errno, "poll: cannot allocate memory for poll");
		return -1;
	}

	poll->usepoll = 1;
	poll->interval = 0;
	poll->stop = 0;
	poll->polling = 0;
	poll->routine = routine;
	poll->arg = arg;
	pthread_cond_init(&(poll->cv), NULL);
	pthread_mutex_init(&(poll->lock), NULL);

	return 0;
}

/*
 * Free resources in data for polling work
 */
int poll_free(poll_t *poll)
{
	free(poll->header);
	poll->header = NULL;
	pthread_cond_destroy(&(poll->cv));
	pthread_mutex_destroy(&(poll->lock));

	return 0;
}
/*
 *  Polling thread
 */
static void *poll_thread(poll_t *poll)
{
	struct timespec ts;
	void *(*routine)(void *) = poll->routine;
	void *arg = poll->arg;

	pthread_mutex_lock(&(poll->lock));

	info("%s: starting status polling with inverval of %d sec",
		poll->header, poll->interval);

	/* Polling loop */
	while (poll->stop == 0) {

		clock_gettime(CLOCK_REALTIME, &ts);

		/* Get status of all devices */
		pthread_mutex_unlock(&(poll->lock));
		(*routine)(arg);
		pthread_mutex_lock(&(poll->lock));

		if (poll->stop) {
			break;
		}
		ts.tv_sec += poll->interval;
		pthread_cond_timedwait(&(poll->cv), &(poll->lock), &ts);
	}

	pthread_mutex_unlock(&(poll->lock));

	info("%s: stopping status polling", poll->header);

	return NULL;
}

/*
 * Start polling
 */
int poll_start(poll_t *poll)
{
	int ret;
	pthread_t tid;

	/* If polling thread is already running, exit */
	pthread_mutex_lock(&(poll->lock));
	if (poll->polling) {
		pthread_mutex_unlock(&(poll->lock));
		return 0;
	}
	poll->stop = 0;

	/* Create polling thread */
	ret = pthread_create(&tid, NULL, (void *)poll_thread, poll);
	if (ret) {
		pthread_mutex_unlock(&(poll->lock));
		errno = ret;
		error_num(errno, "%s: cannot create polling thread",
			poll->header);
		return -1;
	}
	poll->polling = 1;
	poll->tid = tid;
	pthread_mutex_unlock(&(poll->lock));

	return ret;
}

/*
 * Stop polling
 */
int poll_stop(poll_t *poll)
{
	/* If no polling thread is running, exit */
	pthread_mutex_lock(&(poll->lock));
	if (poll->polling == 0) {
		pthread_mutex_unlock(&(poll->lock));
		return 0;
	}

	/* Signal to polling thread for stopping polling */
	poll->stop = 1;
	pthread_cond_signal(&(poll->cv));
	pthread_mutex_unlock(&(poll->lock));

	/* Wait until thread exits */
	pthread_join(poll->tid, NULL);

	pthread_mutex_lock(&(poll->lock));
	poll->polling = 0;
	pthread_mutex_unlock(&(poll->lock));

	return 0;
}

/*
 * Set value of usepoll flag
 */
int poll_setusepoll(poll_t *poll, int usepoll)
{
	pthread_mutex_lock(&(poll->lock));
	poll->usepoll = usepoll;
	pthread_mutex_unlock(&(poll->lock));

	return 0;
}

/*
 * Get value of usepoll flag
 */
int poll_getusepoll(poll_t *poll)
{
	int usepoll;

	pthread_mutex_lock(&(poll->lock));
	usepoll = poll->usepoll;
	pthread_mutex_unlock(&(poll->lock));

	return usepoll;
}

/*
 * Set polling interval
 */
int poll_setinterval(poll_t *poll, int interval)
{
	pthread_mutex_lock(&(poll->lock));
	poll->interval = interval;
	pthread_cond_signal(&(poll->cv));
	pthread_mutex_unlock(&(poll->lock));

	return 0;
}

/*
 * Get polling interval
 */
int poll_getinterval(poll_t *poll)
{
	int interval;

	pthread_mutex_lock(&(poll->lock));
	interval = poll->interval;
	pthread_mutex_unlock(&(poll->lock));

	return interval;
}

/*
 * Get status of polling
 */
int poll_isrunning(poll_t *poll)
{
	int polling;

	pthread_mutex_lock(&(poll->lock));
	polling = poll->polling;
	pthread_mutex_unlock(&(poll->lock));

	return polling;
}

/*
 * Send error message to client
 */
static int poll_sendres(client_t *client, const char *grp, int ret)
{
	char *errstr, buf[RESSTR_MAX + 1];

	if (ret < 0) {
		errstr = strerror_r(errno, buf, sizeof(buf));
		info("%s: %s\n", grp, errstr);
		sendres(client, "Error: %s: %s\n", grp, errstr);
		return -1;
	}

	return 0;
}

/*
 * Process "poll" command (polling on/off)
 */
int poll_cmd_poll(client_t *client, poll_t *poll)
{
	int ret, usepoll;
	char *grp = getargv(client, 0);
	char *arg = getargv(client, 2);

	/* Check argument */
	if (arg == NULL) {
		sendres_missing_arg(client);
		return -1;
	} else if (strcasecmp(arg, "on") == 0) {
		usepoll = 1;
	} else if (strcasecmp(arg, "off") == 0) {
		usepoll = 0;
	} else {
		sendres_invalid_arg(client, arg);
		return -1;
	}

	/* Start or stop polling */
	poll_setusepoll(poll, usepoll);
	if (usepoll) {
		info("%s: poll start", grp);
		ret = poll_start(poll);
	} else {
		info("%s: poll stop", grp);
		ret = poll_stop(poll);
	}

	return poll_sendres(client, grp, ret);
}

/*
 * Process "interval" command
 */
int poll_cmd_interval(client_t *client, poll_t *poll)
{
	int ret, interval;
	char *grp = getargv(client, 0);

	/* Check argument */
	if (getargv_int(client, 2, &interval, 0, USHRT_MAX) < 0) {
		return -1;
	}

	info("%s: poll setinterval %d", grp, interval);

	/* Set interval */
	ret = poll_setinterval(poll, interval);
	return poll_sendres(client, grp, ret);
}
