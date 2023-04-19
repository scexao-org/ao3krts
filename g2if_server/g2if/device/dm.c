/* -------------------------------------------------------------------------
 * dm.c -- Function for handling DM control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/06/17   Y. Ono        Initial version
 *    2019/09/26   Y. Ono        Add cashe for updating DM flat
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
#include "dm.h"			        /* for dm_t */
#include "status.h"			/* for dm_t */

/* Device handler operation functions */

const struct device_operations dm_ops = {
  .init = (int (*)(void *, const char *))dm_init,
  .free = (int (*)(void *))dm_free,
  .open = (int (*)(void *))dm_open,
  .close = (int (*)(void *))dm_close,
  .procconf = (int (*)(void *, const char *, int,	const char **))dm_procconf,
  .postconf = (int (*)(void *))dm_postconf,
  .proccmd = (int (*)(client_t *, void *))dm_proccmd,
};

/*
 * Initialize data to handle controller
 */
int dm_init(dm_t *dm, const char *header){

  if (header != NULL) {
    debug("%s: init", header);
    dm->header = strdup(header);
  } else {
    debug("%s: init", DM_HEADER_DEFAULT);
    dm->header = strdup(DM_HEADER_DEFAULT);
  }
  if (dm->header == NULL) {
    return -1;
  }

  return 0;
}

/*
 * Free resources in data
 */
int dm_free(dm_t *dm){
  debug("%s: free", dm->header);
  free(dm->header);

  return 0;
}

/*
 * Open device
 */
int dm_open(dm_t *dm){
  shms_t *shms = dm->shms;
  struct cacao_shm *shm;
  char errstr[DM_ERRSTR_MAX + 1];

  /* set DM volt shm shortcut */
  if((shm = bsearch(KEY_DM01DISP, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) == NULL){
    sprintf(errstr, "\"%s\" no matched keyword", KEY_DM01DISP);
    error_num(errno, "%s", errstr);
    return -1;
  }
  dm->dmvolt = shm->image.array.F;
  dm->shm_dmvolt = &(shm->image);

  return 0;
}

/*
 * Close device
 */
int dm_close(dm_t *dm){
  return 0;
}

int dm_make_flat(dm_t *dm, int timersec, char *errstr){
  int ret = 0;
  int k, i, cnt = 0;
  float flat[DMACT_NUM];
  struct timespec ts1, ts2;
  int stat_timeout = 0;
  char script[DM_COMM_BUFSIZ];

  /* init flat */
  for(k=0; k<DMACT_NUM; k++) flat[k] = 0;

  /* get current time */
  clock_gettime(CLOCK_REALTIME, &ts1);
  clock_gettime(CLOCK_REALTIME, &ts2);
  ts1.tv_sec += timersec;

  /* loop to get dm volt */
  for(;;){
    /* sem_wait for dmapply */
    ts2.tv_sec += 2;
    ImageStreamIO_semtimedwait(dm->shm_dmvolt, 5, &ts2);
    if(errno == ETIMEDOUT){
      stat_timeout = -1;
      break;
    }

    /* count frame */
    cnt ++;

    /* get dm voltage from shm */
    for(i=0; i<DMACT_NUM; i++) flat[i] += dm->dmvolt[i];

    /* check timeout */
    clock_gettime(CLOCK_REALTIME, &ts2);
    if(cmp_timespec(&ts1, &ts2) <= 0){
      stat_timeout = 1;
      break;
    }

  }

  if(stat_timeout >= 0){

    info("%s: Succes to get flat from %d frames\n", dm->header, cnt);	  

    /* averaging */
    for(i=0; i<DMACT_NUM; i++) flat[i] /= cnt;

    /* save and update flat */
    if((ret = fits_write_flt(DM_FLATFILE_NAME, flat, DMACT_NUM, 1))<0){
      info(RES_HEAD_ERR"%s: Failed to make fits file\n", dm->header);
      sprintf(errstr,"Failed to make fits file\n");
      return ret;
    }

    /* rename flat file */
    sprintf(script,"python %s",dm->updateflat);
    system(script);

  } else if(stat_timeout == -1){
    info(RES_HEAD_ERR"%s: ImageStreamIO_semtimedwait (%s) is failed because of timeout\n", dm->header, KEY_DM_VOLT);
    sprintf(errstr,"ImageStreamIO_semtimedwait (%s) is failed because of timeout\n", KEY_DM_VOLT);
    return -1;
  }

  return 0;
}
