/* -------------------------------------------------------------------------
 * obcp.c -- Function for handling OBCP server
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
#include "obcp.h"			/* for obcp_t */

/* Device handler operation functions */

const struct device_operations obcp_ops = {
	.init = (int (*)(void *, const char *))obcp_init,
	.free = (int (*)(void *))obcp_free,
	.open = (int (*)(void *))obcp_open,
	.close = (int (*)(void *))obcp_close,
	.procconf = (int (*)(void *, const char *, int,	const char **))obcp_procconf,
	.postconf = (int (*)(void *))obcp_postconf,
	.proccmd = (int (*)(client_t *, void *))obcp_proccmd,
};

/*
 * Initialize data to handle controller
 */
int obcp_init(obcp_t *obcp, const char *header){
    int ret;
    comm_t *comm = &(obcp->comm);

    if (header != NULL) {
	debug("%s: init", header);
	obcp->header = strdup(header);
    } else {
	debug("%s: init", OBCP_HEADER_DEFAULT);
	obcp->header = strdup(OBCP_HEADER_DEFAULT);
    }
    if (obcp->header == NULL) {
	return -1;
    }

    if ((ret = comm_init(comm, obcp->header)) < 0) {
	free(obcp->header);
	return ret;
    }
    comm_setdelim(comm, OBCP_DELIM_IN, OBCP_DELIM_OUT);

    return 0;
}

/*
 * Free resources in data
 */
int obcp_free(obcp_t *obcp){
    debug("%s: free", obcp->header);
    
    free(obcp->header);
    comm_free(&(obcp->comm));
    
    return 0;
}

/*
 * Connect to controller and start status polling (if flag is set)
 */
int obcp_connect(obcp_t *obcp){
    int ret;
    comm_t *comm = &(obcp->comm);

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
int obcp_disconnect(obcp_t *obcp){
    comm_t *comm = &(obcp->comm);

    /* Check connection */
    if (comm_isconn(comm) == 0) {
	return 0;
    }
    
    return comm_disconnect_nolog(comm);
}

/*
 * Open device
 */
int obcp_open(obcp_t *obcp){
    return 0;
}

/*
 * Close device
 */
int obcp_close(obcp_t *obcp){
    if (obcp_disconnect(obcp) < 0) {
	return -1;
    }
    return 0;
}
