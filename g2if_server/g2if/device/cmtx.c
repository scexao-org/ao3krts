/* -------------------------------------------------------------------------
 * cmtx.c -- Function for handling CMTX control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/09/24   Y. Ono        Initial version
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
#include "cmtx.h"			/* for cmtx_t */

/* Device handler operation functions */

const struct device_operations cmtx_ops = {
	.init = (int (*)(void *, const char *))cmtx_init,
	.free = (int (*)(void *))cmtx_free,
	.open = (int (*)(void *))cmtx_open,
	.close = (int (*)(void *))cmtx_close,
	.procconf = (int (*)(void *, const char *, int,	const char **))cmtx_procconf,
	.postconf = (int (*)(void *))cmtx_postconf,
	.proccmd = (int (*)(client_t *, void *))cmtx_proccmd,
};

/*
 * Initialize data to handle controller
 */
int cmtx_init(cmtx_t *cmtx, const char *header){

    if (header != NULL) {
	debug("%s: init", header);
	cmtx->header = strdup(header);
    } else {
	debug("%s: init", CMTX_HEADER_DEFAULT);
	cmtx->header = strdup(CMTX_HEADER_DEFAULT);
    }
    if (cmtx->header == NULL) {
	return -1;
    }

    return 0;
}

/*
 * Free resources in data
 */
int cmtx_free(cmtx_t *cmtx){
    debug("%s: free", cmtx->header);
    free(cmtx->header);
    
    return 0;
}

/*
 * Open device
 */
int cmtx_open(cmtx_t *cmtx){
    return 0;
}

/*
 * Close device
 */
int cmtx_close(cmtx_t *cmtx){
    return 0;
}
