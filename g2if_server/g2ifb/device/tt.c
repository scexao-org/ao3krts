/* -------------------------------------------------------------------------
 * tt.c -- Function for handling TT control
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
#include <math.h>                       /* for ceil */
#include <errno.h>			/* for errno */
#include "log.h"			/* for error(), info(), debug() */
#include "comm.h"			/* for comm_t, comm_*() */
#include "device.h"			/* for struct device_operations */
#include "server.h"			/* for client_t */
#include "stringx.h"			/* for strncatx(), strsplit_delim() */
#include "tt.h"			        /* for tt_t */
#include "status.h"			/* for dm_t */

/* Device handler operation functions */

const struct device_operations tt_ops = {
	.init = (int (*)(void *, const char *))tt_init,
	.free = (int (*)(void *))tt_free,
	.open = (int (*)(void *))tt_open,
	.close = (int (*)(void *))tt_close,
	.procconf = (int (*)(void *, const char *, int,	const char **))tt_procconf,
	.postconf = (int (*)(void *))tt_postconf,
	.proccmd = (int (*)(client_t *, void *))tt_proccmd,
};

/*
 * Initialize data to handle controller
 */
int tt_init(tt_t *tt, const char *header){

    if (header != NULL) {
	debug("%s: init", header);
	tt->header = strdup(header);
    } else {
	debug("%s: init", TT_HEADER_DEFAULT);
	tt->header = strdup(TT_HEADER_DEFAULT);
    }
    if (tt->header == NULL) {
	return -1;
    }

    return 0;
}

/*
 * Free resources in data
 */
int tt_free(tt_t *tt){
  debug("%s: free", tt->header);
  free(tt->header);
    
  return 0;
}

/*
 * Open device
 */
int tt_open(tt_t *tt){
  shms_t *shms = tt->shms;
  struct cacao_shm *shm;
  char errstr[TT_ERRSTR_MAX + 1];

  /* set dmtt shm shortcut */
  if((shm = bsearch(KEY_TTM_TT, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) == NULL){
    sprintf(errstr, "\"%s\" no matched keyword", KEY_TTM_TT);
    error_num(errno, "%s", errstr);
    return -1;
  }
  tt->dmtt = shm->image.array.F;
  tt->shm_dmtt = &(shm->image);

  return 0;
}

/*
 * Close device
 */
int tt_close(tt_t *tt){
    return 0;
}


int tt_make_flat(tt_t *tt, int timersec, char *errstr){
  int ret = 0;
  int k, i, cnt = 0;
  int ttnum = 8;
  float flat[ttnum];
  struct timespec ts1, ts2;
  int stat_timeout = 0;
  char script[TT_COMM_BUFSIZ];

  /* init flat */
  for(k=0; k<ttnum; k++) flat[k] = 0;

  /* get current time */
  clock_gettime(CLOCK_REALTIME, &ts1);
  clock_gettime(CLOCK_REALTIME, &ts2);
  ts1.tv_sec += timersec;

  /* loop to get dm volt */
  for(;;){
    /* sem_wait for dmapply */
    ts2.tv_sec += 2;
    ImageStreamIO_semtimedwait(tt->shm_dmtt, 5, &ts2);
    if(errno == ETIMEDOUT){
      stat_timeout = -1;
      break;
    }

    /* count frame */
    cnt ++;

    /* get dm voltage from shm */
    for(i=0; i<ttnum; i++) flat[i] += tt->dmtt[i];

    /* check timeout */
    clock_gettime(CLOCK_REALTIME, &ts2);
    if(cmp_timespec(&ts1, &ts2) <= 0){
      stat_timeout = 1;
      break;
    }

  }

  if(stat_timeout >= 0){

    info("%s: Succes to get flat from %d frames\n", tt->header, cnt);	  

    /* averaging */
    for(i=0; i<ttnum; i++) flat[i] /= cnt;

    /* save and update flat */
    if((ret = fits_write_flt(TT_FLATFILE_NAME, flat, ttnum, 1))<0){
      info(RES_HEAD_ERR"%s: Failed to make fits file\n", tt->header);	
      sprintf(errstr,"Failed to make fits file\n");
      return ret;
    }
    /* rename flat file */
    sprintf(script,"python %s",tt->updateflat);
    system(script);

  } else if(stat_timeout == -1){
    info(RES_HEAD_ERR"%s: ImageStreamIO_semtimedwait (%s) is failed because of timeout\n", tt->header, KEY_TTM_TT);
    sprintf(errstr,"ImageStreamIO_semtimedwait (%s) is failed because of timeout\n", KEY_TTM_TT);
    return -1;
  }

  return 0;
}
