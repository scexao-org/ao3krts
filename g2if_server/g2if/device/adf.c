/* -------------------------------------------------------------------------
 * adf.c -- Function for handling ADF control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/18   Y. Ono        Initial version
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
#include "adf.h"			/* for adf_t */

/* Device handler operation functions */

const struct device_operations adf_ops = {
	.init = (int (*)(void *, const char *))adf_init,
	.free = (int (*)(void *))adf_free,
	.open = (int (*)(void *))adf_open,
	.close = (int (*)(void *))adf_close,
	.procconf = (int (*)(void *, const char *, int,	const char **))adf_procconf,
	.postconf = (int (*)(void *))adf_postconf,
	.proccmd = (int (*)(client_t *, void *))adf_proccmd,
};

/*
 * Initialize data to handle controller
 */
int adf_init(adf_t *adf, const char *header){

    if (header != NULL) {
	debug("%s: init", header);
	adf->header = strdup(header);
    } else {
	debug("%s: init", ADF_HEADER_DEFAULT);
	adf->header = strdup(ADF_HEADER_DEFAULT);
    }
    if (adf->header == NULL) {
	return -1;
    }

    return 0;
}

/*
 * Free resources in data
 */
int adf_free(adf_t *adf){
    debug("%s: free", adf->header);
    free(adf->header);
    
    return 0;
}

/*
 * Open device
 */
int adf_open(adf_t *adf){
    return 0;
}

/*
 * Close device
 */
int adf_close(adf_t *adf){
    return 0;
}
