/*
 * tpool.c -- Functions for a thread pool
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

#include <stdlib.h>				/* for malloc() & free() */
#include <pthread.h>			/* for pthread_*() */
#include <signal.h>				/* for sigfillset() */
#include <time.h>				/* for clock_gettime() */
#include <errno.h>				/* for errno */
#include "log.h"
#include "tpool.h"

static const char *tpool_header = "tpool";

static void *tpool_thread(void *arg);

/*
 * Create a worker thread
 */
static int tpool_create_thread(tpool_t tpool)
{
	int ret;
	pthread_t tid;
	sigset_t fillmask, oldmask;

	/* Mask all signal and detach thread */
	sigfillset(&fillmask);
	pthread_sigmask(SIG_SETMASK, &fillmask, &oldmask);
	ret = pthread_create(&tid, NULL, tpool_thread, (void *)tpool);
	if (ret) {
		errno = ret;
		error_num(errno, "%s: cannot create thread", tpool_header);
		ret = -1;
	} else {
		pthread_detach(tid);
	}
	pthread_sigmask(SIG_SETMASK, &oldmask, NULL);

	return ret;
}

/*
 * Cleanup routine at terminating worker thread
 */
static void tpool_thread_cleanup(tpool_t tpool)
{
	pthread_t my_tid = pthread_self();

	pthread_mutex_lock(&(tpool->lock));
	pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, NULL);

	debug("%s: thread cleanup (tid = %d)", tpool_header, my_tid);

	tpool->num_threads--;

	/* Create new thread if no shutdown or no idle threads */
	if (tpool->shutdown) {
		if (tpool->num_threads == 0) {
			pthread_cond_signal(&(tpool->no_threads));
		}
	} else if ((tpool->num_threads < tpool->min_threads)
		|| ((tpool->num_idles < 1)
			&& (tpool->num_threads < tpool->max_threads-1))) {
		tpool_create_thread(tpool);
	}

	pthread_mutex_unlock(&(tpool->lock));
}

/*
 * Cleanup routine for work data
 */
static void tpool_work_cleanup(tpool_t tpool)
{
	tpool_work_t *workp, **workpp;
	pthread_t my_tid = pthread_self();

	pthread_mutex_lock(&(tpool->lock));
	pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, NULL);

	/* Remove work from list of active works */
	for (workpp = &(tpool->active_works);
		(workp = *workpp) != NULL; workpp = &(workp->next)) {
		if (pthread_equal(workp->tid, my_tid)) {
			*workpp = workp->next;
			break;
		}
	}

	debug("%s: work cleanup (workp = %p)", tpool_header, workp);

	/* Handle waiting a destroyer thread */
	if (tpool->active_works == NULL) {
		pthread_cond_signal(&(tpool->no_active_works));
	}

	/*
	 * Free work data if detach is set,
	 * otherwise add it into list of works finished
	 */
	if (workp->detach && pthread_cond_destroy(&(workp->finished)) == 0) {
		free(workp);
	} else {
		workp->next = tpool->finished_works;
		tpool->finished_works = workp;
		workp->state = TPOOL_WORK_FINISHED;
		pthread_cond_signal(&(workp->finished));
	}

	pthread_mutex_unlock(&(tpool->lock));
}

/*
 * Cleanup idle state of thread
 */
static void tpool_idle_cleanup(tpool_t tpool)
{
	tpool->num_idles--;
	pthread_mutex_unlock(&(tpool->lock));
}

/*
 *  Main routine for worker thread
 */
static void *tpool_thread(void *arg)
{
	tpool_t tpool = (tpool_t)arg;
	tpool_work_t *workp;
	void *(*routine)(void *), *retval;
	sigset_t fillmask;
	struct timespec ts;

	/* Disable cancellation until start loop for debug() */
	pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, NULL);

	debug("%s: new thread (tid = %d)", tpool_header, pthread_self());

	sigfillset(&fillmask);

	/* Add myself into list of worker threads */
	pthread_mutex_lock(&(tpool->lock));
	tpool->num_threads++;
	pthread_mutex_unlock(&(tpool->lock));
	pthread_cleanup_push((void *)tpool_thread_cleanup, tpool);

	for (;;) {

		/* Reset signal mask and cancellation state into initial values */
		pthread_sigmask(SIG_SETMASK, &fillmask, NULL);
		pthread_setcanceltype(PTHREAD_CANCEL_DEFERRED, NULL);
		pthread_setcancelstate(PTHREAD_CANCEL_ENABLE, NULL);

		/*
		 * Wait for work forever if no other idle threads exists,
		 * otherwise wait only during specified seconds (linger)
		 */
		pthread_mutex_lock(&(tpool->lock));
		tpool->num_idles++;
		pthread_cleanup_push((void *)tpool_idle_cleanup, tpool);
		clock_gettime(CLOCK_REALTIME, &ts);
		ts.tv_sec += tpool->linger;
		while ((tpool->cur_queue_size == 0) && (!tpool->shutdown)) {
			if ((tpool->num_threads <= tpool->min_threads)
				|| (tpool->num_idles == 1)) {
				pthread_cond_wait(&(tpool->queue_not_empty), &(tpool->lock));
			} else {
				if (pthread_cond_timedwait(&(tpool->queue_not_empty),
					&(tpool->lock), &ts) == ETIMEDOUT) {
					break;
				}
			}
		};
		pthread_cleanup_pop(0);
		tpool->num_idles--;

		/* If no work for idle thread or shutdown is in progress, then exit */
		if ((tpool->cur_queue_size == 0) || tpool->shutdown) {
			pthread_mutex_unlock(&(tpool->lock));
			break;
		}

		/* Get to work, dequeue the next item */
		workp = tpool->queue_head;
		tpool->cur_queue_size--;
		if (tpool->cur_queue_size == 0) {
			tpool->queue_head = NULL;
			tpool->queue_tail = NULL;
		} else {
			tpool->queue_head = workp->next;
		}

		/* Add my work into list of active works */
		workp->state = TPOOL_WORK_ACTIVE;
		workp->tid = pthread_self();
		workp->next = tpool->active_works;
		tpool->active_works = workp;
		routine = workp->routine;
		arg = workp->arg;

		/* Handle waiting add_work threads when queue was full */
		if (tpool->cur_queue_size == (tpool->max_queue_size - 1)) {
			pthread_cond_signal(&(tpool->queue_not_full));
		}

		/* Handle waiting a destroyer thread */
		if (tpool->cur_queue_size == 0) {
			pthread_cond_signal(&(tpool->queue_empty));
		}

		pthread_mutex_unlock(&(tpool->lock));
		pthread_cleanup_push((void *)tpool_work_cleanup, tpool);

		/* Do this work item */
		retval = (*routine)(arg);

		/* Save return value of routine */
		pthread_mutex_lock(&(tpool->lock));
		workp->retval = retval;
		pthread_mutex_unlock(&(tpool->lock));

		/* Cleanup work data */
		pthread_cleanup_pop(1);		/* tpool_work_cleanup(tpool); */
	}

	/* Cleanup thread data */
	pthread_cleanup_pop(1);		/* tpool_thread_cleanup(tpool); */

	return NULL;
}

/*
 *  Create a thread pool
 */
int tpool_init(tpool_t *tpoolp, int min_threads, int max_threads,
	int max_queue_size, unsigned int linger)
{
	int i, ret;
	tpool_t tpool;

	/* Allocate a pool data structure */
	tpool = (tpool_t)malloc(sizeof(struct tpool));
	if (tpool == NULL) {
		errno = ENOMEM;
		error_num(errno, "%s: cannot allocate memory", tpool_header);
		return -1;
	}

	debug("%s: new pool (tpoolp = %p, min_threads = %d, max_threads = %d,"
		" max_queue_size = %d, linger = %d)", tpool_header, tpool, min_threads,
		max_threads, max_queue_size, linger);

	/* Initialize fields */
	tpool->num_threads = 0;
	tpool->min_threads = min_threads;
	tpool->max_threads = max_threads;
	tpool->num_idles = 0;
	tpool->linger = linger;
	tpool->cur_queue_size = 0;
	tpool->max_queue_size = max_queue_size;
	tpool->queue_head = NULL;
	tpool->queue_tail = NULL;
	tpool->active_works = NULL;
	tpool->finished_works = NULL;
	tpool->queue_closed = 0;
	tpool->shutdown = 0;
	pthread_mutex_init(&(tpool->lock), NULL);
	pthread_cond_init(&(tpool->queue_not_empty), NULL);
	pthread_cond_init(&(tpool->queue_not_full), NULL);
	pthread_cond_init(&(tpool->queue_empty), NULL);
	pthread_cond_init(&(tpool->no_active_works), NULL);
	pthread_cond_init(&(tpool->no_threads), NULL);

	/* Create initial threads */
	for (i = 0; i < min_threads; i++) {
		if ((ret = tpool_create_thread(tpool)) < 0) {
			tpool_destroy(tpool, 0);
			return ret;
		}
	}

	*tpoolp = tpool;

	return 0;
}

/*
 *  Add a work in queue for thread pool
 */
int tpool_work_add(tpool_t tpool, tpool_work_t **workpp,
	void *(*routine)(void *), void *arg, int detach, int timeout)
{
	int timedout, num_threads, max_threads, num_idles;
	tpool_work_t *workp;
	struct timespec ts;

	/* If queue is full, wait until queue is not full */
	if (timeout > 0) {
		clock_gettime(CLOCK_REALTIME, &ts);
		ts.tv_sec += timeout;
	}
	timedout = 0;
	pthread_mutex_lock(&(tpool->lock));
	pthread_cleanup_push((void *)pthread_mutex_unlock, &(tpool->lock));
	while ((tpool->cur_queue_size == tpool->max_queue_size)
		&& (!(tpool->shutdown || tpool->queue_closed))) {
		if (timeout < 0) {
			pthread_cond_wait(&(tpool->queue_not_full), &(tpool->lock));
		} else if (timeout == 0
			|| pthread_cond_timedwait(&(tpool->queue_not_full),
				&(tpool->lock), &ts) == ETIMEDOUT) {
			timedout = 1;
			break;
		}
	}
	pthread_cleanup_pop(0);

	/* If the pool is in the process of being destroyed, then return */
	if (tpool->shutdown || tpool->queue_closed) {
		pthread_mutex_unlock(&(tpool->lock));
		errno = ECANCELED;
		error_num(errno, "%s: pool is in the process of being destroyed",
			tpool_header);
		return -1;
	}
	pthread_mutex_unlock(&(tpool->lock));

	/* If timed out, return w/ errer */
	if (timedout) {
		errno = EAGAIN;
		error_num(errno, "%s: pool is full", tpool_header);
		return -1;
	}

	/* Allocate work data */
	workp = (tpool_work_t *)malloc(sizeof(tpool_work_t));
	if (workp == NULL) {
		error_num(errno, "%s: cannot allocate memory for work", tpool_header);
		errno = ENOMEM;
		return -1;
	}
	workp->routine = routine;
	workp->arg = arg;
	workp->detach = detach;
	workp->state = TPOOL_WORK_WAIT;
	workp->retval = PTHREAD_CANCELED;
	pthread_cond_init(&(workp->finished), NULL);
	workp->next = NULL;

	pthread_mutex_lock(&(tpool->lock));

	/* Add work into list of queue */
	if (tpool->cur_queue_size == 0) {
		tpool->queue_head = tpool->queue_tail = workp;
	} else {
		tpool->queue_tail->next = workp;
		tpool->queue_tail = workp;
	}
	tpool->cur_queue_size++;
	pthread_cond_signal(&(tpool->queue_not_empty));

	/* Copy values to use later */
	num_threads = tpool->num_threads;
	max_threads = tpool->max_threads;
	num_idles = tpool->num_idles;

	pthread_mutex_unlock(&(tpool->lock));

	debug("%s: new work (workp = %p)", tpool_header, workp);

	/* Create new thread if only one thread is idle */
	if ((num_idles <= 1) && (num_threads < max_threads - 1)) {
		tpool_create_thread(tpool);
	}

	/* Return work id if needed */
	if (workpp != NULL) {
		*workpp = workp;
	}

	return 0;
}

/*
 * Search a work in work list
 */
static tpool_work_t **tpool_search_work(tpool_work_t **listp,
	tpool_work_t *my_workp)
{
	tpool_work_t *workp, **workpp;

	for (workpp = listp; (workp = *workpp) != NULL; workpp = &(workp->next)) {
		if (workp == my_workp) {
			return workpp;
		}
	}

	return NULL;
}

/*
 * Cancel a work in queue
 */
int tpool_work_cancel(tpool_t tpool, tpool_work_t *workp)
{
	int ret = 0;
	tpool_work_t **workpp;

	pthread_mutex_lock(&(tpool->lock));

	if ((workpp = tpool_search_work(&(tpool->queue_head), workp)) != NULL) {

		debug("%s: work cancel (workp = %p, state = waiting)", tpool_header,
			workp);

		/* Remove work from list of waiting works */
		*workpp = workp->next;
		tpool->cur_queue_size--;
		if (tpool->cur_queue_size == 0) {
			tpool->queue_tail = NULL;
			pthread_cond_signal(&(tpool->queue_empty));
		}

		/* Free data, or add it into list of finished works */
		if (workp->detach) {
			free(workp);
		} else {
			workp->next = tpool->finished_works;
			tpool->finished_works = workp;
		}

	} else if (tpool_search_work(&(tpool->active_works), workp) != NULL) {

		debug("%s: work cancel (workp = %p, state = active)", tpool_header,
			workp);

		/* Cancel thread performing this work */
		if ((ret = pthread_cancel(workp->tid)) != 0) {
			errno = ret;
			error_num(errno, "%s: cannot cancel work", tpool_header);
			ret = -1;
		}

	} else if (tpool_search_work(&(tpool->finished_works), workp) == NULL) {

		/* If work not exists in list, return error */
		errno = ESRCH;
		error_num(errno, "%s: cannot find work", tpool_header);
		ret = -1;
	} else {
		debug("%s: work cancel (workp = %p, state = finished)", tpool_header,
			workp);
	}

	pthread_mutex_unlock(&(tpool->lock));

	return ret;
}

/*
 * Wait until work is finished or timedout
 */
int tpool_work_timedwait(tpool_t tpool, tpool_work_t *workp, void **retval,
	long timeout)
{
	int timedout;
	tpool_work_t **workpp;
	struct timespec ts;
	time_t sec;

	pthread_mutex_lock(&(tpool->lock));

	/* Check if work exists in any of work lists */
	if ((tpool_search_work(&(tpool->queue_head), workp) == NULL)
		&& (tpool_search_work(&(tpool->active_works), workp) == NULL)
		&& (tpool_search_work(&(tpool->finished_works), workp) == NULL)) {
		pthread_mutex_unlock(&(tpool->lock));
		errno = ESRCH;
		error_num(errno, "%s: cannot find work", tpool_header);
		return -1;
	}

	/* If work is detachable, return w/ error */
	if (workp->detach) {
		pthread_mutex_unlock(&(tpool->lock));
		errno = EINVAL;
		error_num(errno, "%s: work is detachable", tpool_header);
		return -1;
	}

	/* Determine absolute time for timedout */
	if (timeout > 0) {
		clock_gettime(CLOCK_REALTIME, &ts);
		ts.tv_nsec += timeout * 1000;
		sec = ts.tv_nsec / 1000000000;
		ts.tv_nsec %= 1000000000;
		ts.tv_sec += sec;
	}

	/* Wait until work is finished */
	pthread_cleanup_push((void *)pthread_mutex_unlock, &(tpool->lock));
	timedout = 0;
	while (workp->state != TPOOL_WORK_FINISHED) {
		if (timeout < 0) {
			pthread_cond_wait(&(workp->finished), &(tpool->lock));
		} else if (timeout == 0
			|| pthread_cond_timedwait(&(workp->finished), &(tpool->lock),
				&ts) == ETIMEDOUT) {
			timedout = 1;
			break;
		}
	}
	pthread_cleanup_pop(0);

	if (timedout) {
		pthread_mutex_unlock(&(tpool->lock));
		errno = ETIMEDOUT;
		return -1;
	}

	/* Remove work data from list of works finished */
	workpp = tpool_search_work(&(tpool->finished_works), workp);
	if (workpp != NULL) {
		*workpp = workp->next;
	}
	if (retval != NULL) {
		*retval = workp->retval;
	}
	pthread_cond_destroy(&(workp->finished));
	free(workp);

	pthread_mutex_unlock(&(tpool->lock));

	return 0;
}

/*
 * Wait until work is finished
 */
int tpool_work_wait(tpool_t tpool, tpool_work_t *workp, void **retval)
{
	return tpool_work_timedwait(tpool, workp, retval, -1);
}

/*
 * Destroy thread pool
 *
 * if wait > 0, wait for workers to drain queue and finish them during this
 * periods (in seconds)
 */
int tpool_destroy(tpool_t tpool, int wait)
{
	int ret;
	tpool_work_t *workp;
	struct timespec ts;

	pthread_mutex_lock(&(tpool->lock));
	pthread_cleanup_push((void *)pthread_mutex_unlock, &(tpool->lock));

	tpool->queue_closed = 1;

	/*
	 * If wait > 0, wait for workers to drain queue, then wait for
	 * finishing works during this periods
	 */
	if (wait > 0) {
		while (tpool->cur_queue_size != 0) {
			pthread_cond_wait(&(tpool->queue_empty), &(tpool->lock));
		}
		if (tpool->active_works != NULL) {
			clock_gettime(CLOCK_REALTIME, &ts);
			ts.tv_sec += wait;
			pthread_cond_timedwait(&(tpool->no_active_works),
				&(tpool->lock), &ts);
		}
	}

	tpool->shutdown = 1;

	/* Wake up idle threads so they recheck shutdown flag */
	pthread_cond_broadcast(&(tpool->queue_not_empty));

	/* Cancel active workers */
	for (workp = tpool->active_works; workp != NULL; workp = workp->next) {
		debug("%s: thread cancel (tid = %d)", tpool_header, workp->tid);
		if ((ret = pthread_cancel(workp->tid)) != 0) {
			error_num(ret, "%s: cannot cancel thread", tpool_header);
		}
	}

	/* Wait for workers to exit */
	while (tpool->num_threads != 0) {
		pthread_cond_wait(&(tpool->no_threads), &(tpool->lock));
	}
	pthread_cleanup_pop(1);		/* pthread_mutex_unlock(&(tpool->lock)); */

	debug("%s: pool destroy (tpoolp = %p)", tpool_header, tpool);

	/* Free pool structure */
	while ((workp = tpool->queue_head) != NULL) {
		tpool->queue_head = workp->next;
		free(workp);
	}
	while ((workp = tpool->finished_works) != NULL) {
		tpool->finished_works = workp->next;
		free(workp);
	}
	pthread_mutex_destroy(&(tpool->lock));
	pthread_cond_destroy(&(tpool->queue_empty));
	pthread_cond_destroy(&(tpool->queue_not_empty));
	pthread_cond_destroy(&(tpool->queue_not_full));
	pthread_cond_destroy(&(tpool->no_active_works));
	pthread_cond_destroy(&(tpool->no_threads));
	free(tpool);

	return 0;
}
