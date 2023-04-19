/* -------------------------------------------------------------------------
 * lowfs.c -- Function for handling LOWFS server
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/05/13   Y. Ono        Initial version
 *    2019/09/20   Y. Ono        Add cashe
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
#include "conf.h"			/* for setpar_flt */
#include "device.h"			/* for struct device_operations */
#include "server.h"			/* for client_t */
#include "stringx.h"			/* for strncatx(), strsplit_delim() */
#include "lowfs.h"			/* for lowfs_t */

/* Device handler operation functions */

const struct device_operations lowfs_ops = {
	.init = (int (*)(void *, const char *))lowfs_init,
	.free = (int (*)(void *))lowfs_free,
	.open = (int (*)(void *))lowfs_open,
	.close = (int (*)(void *))lowfs_close,
	.procconf = (int (*)(void *, const char *, int,	const char **))lowfs_procconf,
	.postconf = (int (*)(void *))lowfs_postconf,
	.proccmd = (int (*)(client_t *, void *))lowfs_proccmd,
};

/*
 * Initialize data to handle controller
 */
int lowfs_init(lowfs_t *lowfs, const char *header){
    int ret;
    comm_t *comm = &(lowfs->comm);

    if (header != NULL) {
	debug("%s: init", header);
	lowfs->header = strdup(header);
    } else {
	debug("%s: init", LOWFS_HEADER_DEFAULT);
	lowfs->header = strdup(LOWFS_HEADER_DEFAULT);
    }
    if (lowfs->header == NULL) {
	return -1;
    }

    if ((ret = comm_init(comm, lowfs->header)) < 0) {
	free(lowfs->header);
	return ret;
    }
    comm_setdelim(comm, LOWFS_DELIM_IN, LOWFS_DELIM_OUT);

    /* init cashe */
    lowfs->stat.lash = 0;
    strcpy(lowfs->stat.lafw,"CLOSE");
    pthread_rwlock_init(&(lowfs->cache_lock), NULL);

    return 0;
}

/*
 * Free resources in data
 */
int lowfs_free(lowfs_t *lowfs){
    debug("%s: free", lowfs->header);
    
    free(lowfs->header);
    comm_free(&(lowfs->comm));
    
    return 0;
}

/*
 * Connect to controller and start status polling (if flag is set)
 */
int lowfs_connect(lowfs_t *lowfs){
    int ret;
    comm_t *comm = &(lowfs->comm);

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
int lowfs_disconnect(lowfs_t *lowfs){
    comm_t *comm = &(lowfs->comm);

    /* Check connection */
    if (comm_isconn(comm) == 0) {
	return 0;
    }
    
    return comm_disconnect_nolog(comm);
}

/*
 * Open device
 */
int lowfs_open(lowfs_t *lowfs){
    return 0;
}

/*
 * Close device
 */
int lowfs_close(lowfs_t *lowfs){
    if (lowfs_disconnect(lowfs) < 0) {
	return -1;
    }
    return 0;
}


/*
 * Get status from LOWFS server
 */
int lowfs_getstat(lowfs_t *lowfs, struct lowfs_stat *stat, char *errstr){
  int ret = 0;
  char retstr[RESSTR_MAX + 1];
  char *argv[LOWFS_STATARG_MAX];
  comm_t *comm = &(lowfs->comm);

  if((ret = lowfs_connect(lowfs))<0){
    sprintf(errstr, "cannot connect to lowfs server (%s:%d)", comm->addr, comm->port);
    return -1;
  }

  /* Exclude other threads until end of communication */
  comm_lock(comm);
  pthread_cleanup_push((void *)comm_unlock, comm);

  if (comm_chkconn(comm) >= 0){

    /* LASH st */
    if((ret = comm_sendrecv(comm, LOWFS_CMD_LASH_ST, retstr, sizeof(retstr))) < 0){
      sprintf(errstr, "%s", retstr);
    } else{
      strsplit_delim(retstr, argv, " ,=:{}()[]'\n\r\t\v\f", LOWFS_STATARG_MAX);
      if(strcmp(argv[2],"OPEN") == 0) stat->lash = 1;
      else stat->lash = 0;
    }

    /* LAFW st */
    if((ret = comm_sendrecv(comm, LOWFS_CMD_LAFW_ST, retstr, sizeof(retstr))) < 0){
      sprintf(errstr, "%s", retstr);
    } else{
      strsplit_delim(retstr, argv, " ,=:{}()[]'\n\r\t\v\f", LOWFS_STATARG_MAX);
      strcpy(stat->lafw, argv[2]);
    }

  }
  pthread_cleanup_pop(1);

  if((ret = lowfs_disconnect(lowfs))<0){
    sprintf(errstr, "cannot disconnect from lowfs server (%s:%d)", comm->addr, comm->port);
    return -1;
  }

  return ret;
}

/*
 * Save status into cashe
 */
int lowfs_savestat(lowfs_t *lowfs, struct lowfs_stat *stat){
  pthread_rwlock_wrlock(&(lowfs->cache_lock));
  lowfs->stat = *stat;
  pthread_rwlock_unlock(&(lowfs->cache_lock));
  return 0;
}


/*
 * shutter close
 */
int lowfs_lash_close(lowfs_t *lowfs, char *errstr){
  int ret = 0;
  char retstr[RESSTR_MAX + 1];
  comm_t *comm = &(lowfs->comm);
      
  /* init errstr */
  errstr[0]='\0';

  /* connect lowfs server */
  if((ret = lowfs_connect(lowfs))<0){
    sprintf(errstr, RES_HEAD_ERR"%s: cannot connect to lowfs server (%s:%d)", lowfs->header, comm->addr, comm->port);
    return -1;
  }

  /* Exclude other threads until end of communication */
  comm_lock(comm);
  pthread_cleanup_push((void *)comm_unlock, comm);

  /* send command */
  if (comm_chkconn(comm) >= 0){
    ret = comm_sendrecv(comm, LOWFS_CMD_LASH_CLOSE, retstr, sizeof(retstr));
    if(ret < 0) sprintf(errstr,"%s",retstr);
  }

  pthread_cleanup_pop(1);

  /* disconnect from lowfs server */
  if((ret = lowfs_disconnect(lowfs))<0){
    sprintf(errstr, RES_HEAD_ERR"%s: cannot disconnect from lowfs server (%s:%d)", lowfs->header, comm->addr, comm->port);
    return -1;
  }
  return 0;
}
