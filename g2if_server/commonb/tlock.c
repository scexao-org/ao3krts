/*
 * tlock.c -- Functions for exclusive processing of threads
 *
 * 2008/11/05 Makoto WATANABE -- Initial version
 */

#include <pthread.h>			/* for pthread_*() */
#include "tlock.h"

/*
 * Initialize exclusive processing data
 */
void tlock_init(tlock_t *tlock)
{
	tlock->count = 0;
	pthread_cond_init(&(tlock->cv), NULL);
	pthread_mutex_init(&(tlock->lock), NULL);
}

/*
 * Destroy exclusive processing data
 */
void tlock_free(tlock_t *tlock)
{
	pthread_cond_destroy(&(tlock->cv));
	pthread_mutex_destroy(&(tlock->lock));
}

/*
 * Wait until it is unlocked, and then lock by myself
 */
void tlock_lock(tlock_t *tlock)
{
	pthread_mutex_lock(&(tlock->lock));
	pthread_cleanup_push((void *)pthread_mutex_unlock,
		(void *)(&(tlock->lock)));

	while (tlock->count
		&& !pthread_equal(pthread_self(), tlock->tid)) {
		pthread_cond_wait(&(tlock->cv), &(tlock->lock));
	}

	tlock->count++;
	tlock->tid = pthread_self();

	pthread_cleanup_pop(1);	/* pthread_mutex_unlock(&(tlock->lock)); */
}

/*
 * Cleanup state of lock
 */
void tlock_unlock(tlock_t *tlock)
{
	pthread_mutex_lock(&(tlock->lock));
	tlock->count--;
	pthread_cond_signal(&(tlock->cv));
	pthread_mutex_unlock(&(tlock->lock));
}
