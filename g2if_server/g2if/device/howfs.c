/* -------------------------------------------------------------------------
 * howfs.c -- Function for handling HOWFS server
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
#include "howfs.h"			/* for howfs_t */

/* Device handler operation functions */

const struct device_operations howfs_ops = {
	.init = (int (*)(void *, const char *))howfs_init,
	.free = (int (*)(void *))howfs_free,
	.open = (int (*)(void *))howfs_open,
	.close = (int (*)(void *))howfs_close,
	.procconf = (int (*)(void *, const char *, int,	const char **))howfs_procconf,
	.postconf = (int (*)(void *))howfs_postconf,
	.proccmd = (int (*)(client_t *, void *))howfs_proccmd,
};

/*
 * Initialize data to handle controller
 */
int howfs_init(howfs_t *howfs, const char *header){
    int ret;
    comm_t *comm = &(howfs->comm);

    if (header != NULL) {
	debug("%s: init", header);
	howfs->header = strdup(header);
    } else {
	debug("%s: init", HOWFS_HEADER_DEFAULT);
	howfs->header = strdup(HOWFS_HEADER_DEFAULT);
    }
    if (howfs->header == NULL) {
	return -1;
    }

    if ((ret = comm_init(comm, howfs->header)) < 0) {
	free(howfs->header);
	return ret;
    }
    comm_setdelim(comm, HOWFS_DELIM_IN, HOWFS_DELIM_OUT);

    /* init cashe */
    howfs->stat.lash = 0;
    howfs->stat.vm = 0;
    howfs->stat.freq = 1000.0;
    howfs->stat.volt = 0.0;
    howfs->stat.phase = 0.0;
    strcpy(howfs->stat.lafw,"CLOSE");
    pthread_rwlock_init(&(howfs->cache_lock), NULL);

    return 0;
}

/*
 * Free resources in data
 */
int howfs_free(howfs_t *howfs){
    debug("%s: free", howfs->header);
    
    free(howfs->header);
    comm_free(&(howfs->comm));
    
    return 0;
}

/*
 * Connect to controller and start status polling (if flag is set)
 */
int howfs_connect(howfs_t *howfs){
    int ret;
    comm_t *comm = &(howfs->comm);

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
int howfs_disconnect(howfs_t *howfs){
    comm_t *comm = &(howfs->comm);

    /* Check connection */
    if (comm_isconn(comm) == 0) {
	return 0;
    }
    
    return comm_disconnect_nolog(comm);
}

/*
 * Open device
 */
int howfs_open(howfs_t *howfs){
    return 0;
}

/*
 * Close device
 */
int howfs_close(howfs_t *howfs){
    if (howfs_disconnect(howfs) < 0) {
	return -1;
    }
    return 0;
}

/*
 * Get status from HOWFS server
 */
int howfs_getstat(howfs_t *howfs, struct howfs_stat *stat, char *errstr){
  int ret = 0;
  char retstr[RESSTR_MAX + 1];
  int argc;
  char *argv[HOWFS_STATARG_MAX];
  comm_t *comm = &(howfs->comm);

  /* connect to HOWFS server */
  if((ret = howfs_connect(howfs))<0){
    sprintf(errstr, "cannot connect to howfs server (%s:%d)", comm->addr, comm->port);
    return -1;
  }

  /* Exclude other threads until end of communication */
  comm_lock(comm);
  pthread_cleanup_push((void *)comm_unlock, comm);

  if (comm_chkconn(comm) >= 0){

    /* LASH st */
    if((ret = comm_sendrecv(comm, HOWFS_CMD_LASH_ST, retstr, sizeof(retstr))) < 0){
      sprintf(errstr, "%s", retstr);
    } else{
      argc = strsplit_delim(retstr, argv, " ,=:{}()[]'\n\r\t\v\f", HOWFS_STATARG_MAX);
      if(strcmp(argv[2],"OPEN") == 0) stat->lash = 1; // lash open/close
      else stat->lash = 0;
    }

    /* LAFW st */
    if((ret = comm_sendrecv(comm, HOWFS_CMD_LAFW_ST, retstr, sizeof(retstr))) < 0){
      sprintf(errstr, "%s", retstr);
    } else{
      argc = strsplit_delim(retstr, argv, " ,=:{}()[]'\n\r\t\v\f", HOWFS_STATARG_MAX);
      strcpy(stat->lafw, argv[2]);
    }

    /* VM st */
    if((ret = comm_sendrecv(comm, HOWFS_CMD_VMST, retstr, sizeof(retstr))) < 0){
      sprintf(errstr, "%s", retstr);
    } else{
      argc = strsplit_delim(retstr, argv, " ,=:{}()[]'\n\r\t\v\f", HOWFS_STATARG_MAX);
      if(strcmp(argv[1],"ON") == 0) stat->vm = 1; // vm on/off
      else stat->vm = 0;
      setpar_flt(argc, (const char **)argv, 3, &(stat->freq), 0, 0); // vm frequency
      setpar_flt(argc, (const char **)argv, 6, &(stat->volt), 0, 0); // vm volt
      setpar_flt(argc, (const char **)argv, 9, &(stat->phase), 0, 0); // vm phase
    }
  }

  /* unlock thread */
  pthread_cleanup_pop(1);

  /* disconnect from HOWFS server */
  if((ret = howfs_disconnect(howfs))<0){
    sprintf(errstr, "cannot disconnect from howfs server (%s:%d)", comm->addr, comm->port);
    return -1;
  }

  return ret;
}

/*
 * Store status in cashe
 */
int howfs_savestat(howfs_t *howfs, struct howfs_stat *stat){
  pthread_rwlock_wrlock(&(howfs->cache_lock));
  howfs->stat = *stat;
  pthread_rwlock_unlock(&(howfs->cache_lock));
  return 0;
}

/*
 * shutter close
 */
int howfs_lash_close(howfs_t *howfs, char *errstr){
  int ret = 0;
  char retstr[RESSTR_MAX + 1];
  comm_t *comm = &(howfs->comm);
      
  /* init errstr */
  errstr[0]='\0';

  /* connect howfs server */
  if((ret = howfs_connect(howfs))<0){
    sprintf(errstr, RES_HEAD_ERR"%s: cannot connect to howfs server (%s:%d)", howfs->header, comm->addr, comm->port);
    return -1;
  }

  /* Exclude other threads until end of communication */
  comm_lock(comm);
  pthread_cleanup_push((void *)comm_unlock, comm);

  /* send command */
  if (comm_chkconn(comm) >= 0){
    ret = comm_sendrecv(comm, HOWFS_CMD_LASH_CLOSE, retstr, sizeof(retstr));
    if(ret < 0) sprintf(errstr,"%s",retstr);
  }

  pthread_cleanup_pop(1);

  /* disconnect from howfs server */
  if((ret = howfs_disconnect(howfs))<0){
    sprintf(errstr, RES_HEAD_ERR"%s: cannot disconnect from howfs server (%s:%d)", howfs->header, comm->addr, comm->port);
    return -1;
  }
  return 0;
}
