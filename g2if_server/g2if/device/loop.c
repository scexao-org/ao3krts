/* -------------------------------------------------------------------------
 * loop.c -- Function for handling LOOP control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/11   Y. Ono        Initial version
 *    2019/09/26   Y. Ono        Add fifo for LOOP status
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
#include "loop.h"			/* for loop_t */

/* Device handler operation functions */

const struct device_operations loop_ops = {
  .init = (int (*)(void *, const char *))loop_init,
  .free = (int (*)(void *))loop_free,
  .open = (int (*)(void *))loop_open,
  .close = (int (*)(void *))loop_close,
  .procconf = (int (*)(void *, const char *, int,	const char **))loop_procconf,
  .postconf = (int (*)(void *))loop_postconf,
  .proccmd = (int (*)(client_t *, void *))loop_proccmd,
};

/*
 * Initialize data to handle controller
 */
int loop_init(loop_t *loop, const char *header){

  if (header != NULL) {
    debug("%s: init", header);
    loop->header = strdup(header);
  } else {
    debug("%s: init", LOOP_HEADER_DEFAULT);
    loop->header = strdup(LOOP_HEADER_DEFAULT);
  }
  if (loop->header == NULL) {
    return -1;
  }

  /* init cashe */
  loop->stat.onoff = 0;
  pthread_rwlock_init(&(loop->cache_lock), NULL);

  /* init fifo */
  fifo_init(&(loop->fifo));
  fifo_set_name(&(loop->fifo), LOOP_FIFO_NAME);
  fifo_create(&(loop->fifo));

  /* init mutex lock */
  pthread_mutex_init(&(loop->lock), NULL);

  return 0;
}

/*
 * Free resources in data
 */
int loop_free(loop_t *loop){
  debug("%s: free", loop->header);
  free(loop->header);
  fifo_free(&(loop->fifo));
  pthread_mutex_destroy(&(loop->lock));

  return 0;
}

/*
 * Open device
 */
int loop_open(loop_t *loop){
  if(fifo_open(&(loop->fifo)) < 0){
    info(RES_HEAD_ERR"%s: Failed to open fifo %s\n", loop->header, loop->fifo.name);
    return -1;
  }
  return 0;
}

/*
 * Close device
 */
int loop_close(loop_t *loop){
  if((fifo_close(&(loop->fifo))) < 0){
    info(RES_HEAD_ERR"%s: Failed to close fifo %s\n", loop->header, loop->fifo.name);
    return -1;
  }
  return 0;
}

/*
 * Get loop status
 */
int loop_getstat(loop_t *loop, struct loop_stat *stat){
  int ret = 0;
  char buff[LOOP_COMM_BUFSIZ];
  char *arg[LOOP_STATARG_MAX];

  /* send fwrval command to cacao */
  system("echo \""FIFO_GET_COMMAND" "LOOP_FIFO_ONOFF" "LOOP_FIFO_NAME"\" >> "FIFO_FPSCTRL_NAME);

  /* read fifo */
  ret = fifo_read(&(loop->fifo), buff);

  /* parse text */
  if(ret == 0){
    ret = strsplit_delim(buff, arg, " ,=:{}()[]'\n\r\t\v\f", LOOP_STATARG_MAX);
    if(strcmp(arg[4],"ON") == 0) stat->onoff = 1;
    else if(strcmp(arg[4],"OFF") == 0) stat->onoff = 0;
    else{
      info(RES_HEAD_ERR"%s: FIFO format is worng %s\n", loop->header, buff);
      stat->onoff = -1;
      return -1;
    }
  } else{
    info(RES_HEAD_ERR"%s: %s\n", loop->header, buff);
    stat->onoff = -1;
    return -1;
  }
  return 0;
}

/*
 * Save status into cashe
 */
int loop_savestat(loop_t *loop, struct loop_stat *stat){
  pthread_rwlock_wrlock(&(loop->cache_lock));
  loop->stat = *stat;
  pthread_rwlock_unlock(&(loop->cache_lock));
  return 0;
}

