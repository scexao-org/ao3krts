/*
 * log.c -- Functions for logging message into file and/or console
 *
 * Written by Makoto WATANABE
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE		/* for program_invocation_short_name, and also
							for using GNU version of strerror_r() */
#endif /* _GNU_SOURCE */

#include <stdio.h>				/* for snprintf(), fopen(), fclose() */
#include <stdlib.h>				/* for free() */
#include <stdarg.h>				/* for va_list, va_start(), va_end() */
#include <string.h>				/* for strdup(), strerror_r() */
#include <errno.h>				/* for errno, program_invocation_name */
#include <time.h>				/* for time(), strftime(), localtime_r() */
#include <sys/time.h>			/* for gettimeofday() */
#include <pthread.h>			/* for pthread_*() */
#include "stringx.h"			/* for strrmcrlf(), strncatf() */
#include "log.h"

#define progname program_invocation_short_name

#define MILLISEC

/* logging control data */
static char *logfile = NULL;		/* pointer to filename of logfile */
static int logterm = 1;				/* flag to put log onto terminal too */
static int loglevel = LOG_INFO;		/* level of message to be printed */

/* mutex to lock logging control dat */
static pthread_mutex_t loglock = PTHREAD_MUTEX_INITIALIZER;

/*
 * Set filename of logfile
 */
int setlogfile(const char *path)
{
	char *s;

	pthread_mutex_lock(&loglock);

	if (path == NULL) {
		s = NULL;
	} else if ((s = strdup(path)) == NULL) {
		pthread_mutex_unlock(&loglock);
		return -1;
	}

	free(logfile);
	logfile = s;

	pthread_mutex_unlock(&loglock);

	return 0;
}

/*
 * Set flag to enable/disable logging onto terminal (stderr)
 */
int setlogterm(int use)
{
	pthread_mutex_lock(&loglock);
	logterm = use;
	pthread_mutex_unlock(&loglock);

	return 0;
}

/*
 * Set loglevel (lower number is more critial message)
 */
int setloglevel(int level)
{
	pthread_mutex_lock(&loglock);
	loglevel = level;
	pthread_mutex_unlock(&loglock);

	return 0;
}

/*
 * Get current loglevel
 */
int getloglevel(void)
{
	int ret;

	pthread_mutex_lock(&loglock);
	ret = loglevel;
	pthread_mutex_unlock(&loglock);

	return ret;
}

/*
 * Check if message w/ this priority is printed or not
 */
int logisprint(int priority)
{
	int level;

	pthread_mutex_lock(&loglock);
	level = loglevel;
	pthread_mutex_unlock(&loglock);

	if (priority > level) {
		return 0;
	}

	return 1;
}

/*
 * Write message into logfile w/ time stamp
 */
static int putlog_file(const char *header, const char *msg)
{
	char timestr[32];
	FILE *fp;
	struct tm tm;

	/* Get current time string */

#ifdef MILLISEC
	struct timeval tv;
	gettimeofday(&tv, NULL);
	strftime(timestr, sizeof(timestr), "[%Y/%m/%d %H:%M:%S",
		localtime_r(&(tv.tv_sec), &tm));
	strncatf(timestr, sizeof(timestr), ".%03d] ", tv.tv_usec / 1000);
#else
	time_t t;
	time(&t);
	strftime(timestr, sizeof(timestr), "[%Y/%m/%d %H:%M:%S] ",
		localtime_r(&t, &tm));
#endif

	/* Put message into file */
	if ((fp = fopen(logfile, "a")) == NULL) {
		return -1;
	} else if (fputs(timestr, fp) == EOF || fputs(header, fp) == EOF
		|| fputs(msg, fp) == EOF || fputs("\n", fp) == EOF) {
		fclose(fp);
		return -1;
	} else if (fclose(fp) == EOF) {
		return -1;
	}

	return 0;
}

/*
 * Print message and logging into file
 */
int putlog(int priority, const char *format, ...)
{
	int level, ret = 0;
	int saved_errno = errno;
	char msg[LOG_MSG_BUFSIZ];
	const char *header;
	va_list ap;

	pthread_mutex_lock(&loglock);
	level = loglevel;
	pthread_mutex_unlock(&loglock);

	/* Check priority first */
	if (priority > level) {
		errno = saved_errno;
		return 0;
	}

	/* Get formatted message */
	va_start(ap, format);
	vsnprintf(msg, sizeof(msg), format, ap);
	va_end(ap);

	/* Remove CR and LF charactors at end of message */
	strrmcrlf(msg);

	/* If no actual string, return */
	if (!msg[0]) {
		errno = saved_errno;
		return 0;
	}

	/* Set header of message */
	switch (priority) {
	case LOG_ERR:
		header = LOG_HEAD_ERR": ";
		break;
	case LOG_WARN:
		header = LOG_HEAD_WARN": ";
		break;
	default:
		header = "";
	}

	pthread_mutex_lock(&loglock);

	/* if logterm = 1, error, or warning, put message to console */
	if (logterm || priority == LOG_ERR || priority == LOG_WARN) {
		if (priority == LOG_ERR || priority == LOG_WARN) {
			fputs(progname, stderr);
			fputs(": ", stderr);
		}
		fputs(header, stderr);
		fputs(msg, stderr);
		fputs("\n", stderr);
	}

	/* Put message into file */
	if (logfile != NULL) {
		if ((ret = putlog_file(header, msg)) < 0) {
			fprintf(stderr,
				"%s: "LOG_HEAD_ERR": cannot write into logfile (%s): %s\n",
				progname, logfile, strerror_r(errno, msg, sizeof(msg)));
		}
	}

	pthread_mutex_unlock(&loglock);
	errno = saved_errno;

	return ret;
}

/*
 *	Print error message defined by error number
 */
int error_num(int errnum, const char *format, ...)
{
	int ret, saved_errno = errno;
	char buf[256], msg[LOG_MSG_BUFSIZ];
	const char *errstr;
	va_list ap;

	/* Get error string */
	errstr = strerror_r(errnum, buf, sizeof(buf));

	/* If no additional message, just print error string */
	if (format == NULL) {
		ret = putlog(LOG_ERR, errstr);
	} else {
		va_start(ap, format);
		vsnprintf(msg, sizeof(msg), format, ap);
		va_end(ap);
		ret = putlog(LOG_ERR, "%s: %s", msg, errstr);
	}

	errno = saved_errno;
	return ret;
}
