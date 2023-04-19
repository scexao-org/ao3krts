/* -------------------------------------------------------------------------
 * wtt.c -- Function for handling WTT control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/06/17   Y. Ono        Initial version
 *
 * -------------------------------------------------------------------------
 */

#include <stdio.h>			/* for snprintf() */
#include <stdlib.h>			/* for realloc(), free() */
#include <string.h>			/* for strncat(), strlen(), strstr() */
#include <pthread.h>			/* for pthread_*() */
#include <sys/time.h>			/* for gettimeofday() */
#include <errno.h>			/* for errno */
#include "log.h"			/* for error(), info(), debug() */
#include "comm.h"			/* for comm_t, comm_*() */
#include "device.h"			/* for struct device_operations */
#include "server.h"			/* for client_t */
#include "stringx.h"			/* for strncatx(), strsplit_delim() */
#include "wtt.h"			        /* for wtt_t */

/* Device handler operation functions */

const struct device_operations wtt_ops = {
	.init = (int (*)(void *, const char *))wtt_init,
	.free = (int (*)(void *))wtt_free,
	.open = (int (*)(void *))wtt_open,
	.close = (int (*)(void *))wtt_close,
	.procconf = (int (*)(void *, const char *, int,	const char **))wtt_procconf,
	.postconf = (int (*)(void *))wtt_postconf,
	.proccmd = (int (*)(client_t *, void *))wtt_proccmd,
};

/*
 * Initialize data to handle controller
 */
int wtt_init(wtt_t *wtt, const char *header){

    if (header != NULL) {
	debug("%s: init", header);
	wtt->header = strdup(header);
    } else {
	debug("%s: init", WTT_HEADER_DEFAULT);
	wtt->header = strdup(WTT_HEADER_DEFAULT);
    }
    if (wtt->header == NULL) {
	return -1;
    }

    return 0;
}

/*
 * Free resources in data
 */
int wtt_free(wtt_t *wtt){
    debug("%s: free", wtt->header);
    free(wtt->header);
    
    return 0;
}

/*
 * Open device
 */
int wtt_open(wtt_t *wtt){
    return 0;
}

/*
 * Close device
 */
int wtt_close(wtt_t *wtt){
    return 0;
}
