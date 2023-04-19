/* -------------------------------------------------------------------------
 * entshut.c -- Function for handling ENTSHUT server
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/05/13   Y. Ono        Initial version
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
#include "entshut.h"			/* for entshut_t */

/* Device handler operation functions */

const struct device_operations entshut_ops = {
	.init = (int (*)(void *, const char *))entshut_init,
	.free = (int (*)(void *))entshut_free,
	.open = (int (*)(void *))entshut_open,
	.close = (int (*)(void *))entshut_close,
	.procconf = (int (*)(void *, const char *, int,	const char **))entshut_procconf,
	.postconf = (int (*)(void *))entshut_postconf,
	.proccmd = (int (*)(client_t *, void *))entshut_proccmd,
};

/*
 * Initialize data to handle controller
 */
int entshut_init(entshut_t *entshut, const char *header){
    int ret;
    comm_t *comm = &(entshut->comm);

    if (header != NULL) {
	debug("%s: init", header);
	entshut->header = strdup(header);
    } else {
	debug("%s: init", ENTSHUT_HEADER_DEFAULT);
	entshut->header = strdup(ENTSHUT_HEADER_DEFAULT);
    }
    if (entshut->header == NULL) {
	return -1;
    }

    if ((ret = comm_init(comm, entshut->header)) < 0) {
	free(entshut->header);
	return ret;
    }
    comm_setdelim(comm, ENTSHUT_DELIM_IN, ENTSHUT_DELIM_OUT);

    return 0;
}

/*
 * Free resources in data
 */
int entshut_free(entshut_t *entshut){
    debug("%s: free", entshut->header);
    
    free(entshut->header);
    comm_free(&(entshut->comm));
    
    return 0;
}

/*
 * Connect to controller and start status polling (if flag is set)
 */
int entshut_connect(entshut_t *entshut){
    int ret;
    comm_t *comm = &(entshut->comm);

    /* Check connection */
    if (comm_isconn(comm)) {
	return 0;
    }
    
    /* Open connection */
    if ((ret = comm_connect_nolog(comm)) < 0) {
	return ret;
    }
  
    return 0;
}

/*
 * Disconnect from controller (also stop status polling)
 */
int entshut_disconnect(entshut_t *entshut){
    comm_t *comm = &(entshut->comm);

    /* Check connection */
    if (comm_isconn(comm) == 0) {
	return 0;
    }
    
    return comm_disconnect_nolog(comm);
}

/*
 * Open device
 */
int entshut_open(entshut_t *entshut){
    return 0;
}

/*
 * Close device
 */
int entshut_close(entshut_t *entshut){
    if (entshut_disconnect(entshut) < 0) {
	return -1;
    }
    return 0;
}
