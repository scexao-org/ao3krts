/*
 * tpool.h -- Definitions for thread pool
 *
 * Written by Makoto WATANABE, July 2008.
 * Modified by Makoto WATANABE, October 2008.
 *
 * The following codes originate from the example codes in "Pthreads
 * Programming" by B. Nichols, D. Buttlar, & J. P. Farrell (O'Reilly, 1996)
 * and its Japanese translation by M. Sakaki (O'Reilly, 1998). Also, some
 * codes originate from "Multithreaded Programming Guide" (Sun Microsystems,
 * 2008; P/N: 816-5137-11) and its Japanese translation (P/N: 819-0390-11).
 *
 * The following modifications and additions of functions are done from the
 * original version.
 *
 * 1. Dynamical change of number of active worker threads within specified
 *    minimum and maximum numbers (at least one thread is always maintained as
 *    idle, and extra idle threads will exit after specified linger period)
 * 2. Timed wait mode of add work function
 * 3. Cancellation and waiting functions for individual work
 */

#ifndef _TPOOL_H
#define _TPOOL_H

#include <pthread.h>

/*
 * Structure for linked list of work
 */
typedef struct tpool_work {
	void *(*routine)(void *);		/* pointer to work routine */
	void *arg;						/* argument for work routine */
	int detach;						/* flag to free work data after work finished */
	int state;						/* state of work */
	void *retval;					/* return value of work routine */
	pthread_t tid;					/* thread performing this work */
	pthread_cond_t finished;		/* cv to signal work is finished */
	struct tpool_work *next;		/* pointer to next work data */
} tpool_work_t;

/* States of work */
enum {
	TPOOL_WORK_WAIT,				/* work is wating */
	TPOOL_WORK_ACTIVE,				/* work is running */
	TPOOL_WORK_FINISHED,			/* work is finished */
};

/*
 * Structure pool data
 */
typedef struct tpool {
	int num_threads;				/* current number of threads */
	int min_threads;				/* minimum of number of threads */
	int max_threads;				/* maximum of number of threads */
	int num_idles;					/* number of idle threads */
	unsigned int linger;			/* period (sec) until idle thread exit */
	int cur_queue_size;				/* current queue size */
	int max_queue_size;				/* maximum size of work queue */
	tpool_work_t *queue_head;		/* pointer to head of waiting works */
	tpool_work_t *queue_tail;		/* pointer to tail of waiting works */
	tpool_work_t *active_works;		/* linked list of active works */
	tpool_work_t *finished_works;	/* linked list of works finished */
	int queue_closed;				/* flag for closed queue */
	int shutdown;					/* shutdown flag */
	pthread_mutex_t lock;			/* mutex to lock tpool data */
	pthread_cond_t queue_empty;		/* for signal queue is empty */
	pthread_cond_t queue_not_empty;	/* for signal queue is not empty */
	pthread_cond_t queue_not_full;	/* for signal queue is not full */
	pthread_cond_t no_active_works;	/* for signal no active works exists */
	pthread_cond_t no_threads;		/* for signal no worker exists */
} *tpool_t;

/* Function prototypes */

#ifdef __cplusplus
extern "C" {
#endif

int tpool_init(tpool_t *tpoolp, int min_threads, int max_threads,
	int max_queue_size, unsigned int ligner);
int tpool_work_add(tpool_t tpool, tpool_work_t **workpp,
	void *(*routine)(void *), void *arg, int detach, int timeout);
int tpool_work_cancel(tpool_t tpool, tpool_work_t *workp);
int tpool_work_timedwait(tpool_t tpool, tpool_work_t *workp, void **retval,
	long timeout);
int tpool_work_wait(tpool_t tpool, tpool_work_t *workp, void **retval);
int tpool_destroy(tpool_t tpool, int finish);

#ifdef __cplusplus
}
#endif

#endif /* _TPOOL_H */
