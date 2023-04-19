/*
 * tlock.h -- Definitions for exclusive processing of threads
 *
 * 2008/11/05 Makoto WATANABE -- Initial version
 */

#ifndef _TLOCK_H
#define _TLOCK_H

#include <pthread.h>			/* for pthread_* */

/* Structure for exclusive control of threads */

typedef struct tlock {
	int count;				/* count of locks */
	pthread_t tid;			/* id of thread has this lock */
	pthread_cond_t cv; 		/* condition variable to signal change in data */
	pthread_mutex_t lock; 	/* lock of data */
} tlock_t;

#ifdef __cplusplus
extern "C" {
#endif

/* Function prototypes */

void tlock_init(tlock_t *tlock);
void tlock_free(tlock_t *tlock);
void tlock_lock(tlock_t *tlock);
void tlock_unlock(tlock_t *tlock);

#ifdef __cplusplus
}
#endif

#endif /* _TLOCK_H */
