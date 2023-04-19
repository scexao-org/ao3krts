/* -------------------------------------------------------------------------
 * apdsafe.c -- Function for handling APDSAFE control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/06/20   Y. Ono        Initial version
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
#include "apdsafe.h"			/* for apdsafe_t */
#include "status.h"			/* for APD_NUM */

/* Device handler operation functions */

const struct device_operations apdsafe_ops = {
	.init = (int (*)(void *, const char *))apdsafe_init,
	.free = (int (*)(void *))apdsafe_free,
	.open = (int (*)(void *))apdsafe_open,
	.close = (int (*)(void *))apdsafe_close,
	.procconf = (int (*)(void *, const char *, int,	const char **))apdsafe_procconf,
	.postconf = (int (*)(void *))apdsafe_postconf,
	.proccmd = (int (*)(client_t *, void *))apdsafe_proccmd,
};


/*
 *  Status polling routine
 */
static void *apdsafe_poll(apdsafe_t *apdsafe){
  int cnt;
  int nframe;
  float max_limit;
  int emergency;
  float data[APD_NUM];
  int *hapdmap = apdsafe->hapdmap;
  int *lapdmap = apdsafe->lapdmap;
  int i;
  float f, tmp, have, hmax, lave, lmax;
  char errstr[APDSAFE_ERRSTR_MAX + 1];
  struct timespec ts1;

  // copy to local
  pthread_rwlock_rdlock(&(apdsafe->cache_lock));
  cnt = apdsafe->cnt;
  nframe = apdsafe->nframe;
  max_limit = apdsafe->max_limit;
  emergency = apdsafe->emergency; // on|off
  pthread_rwlock_unlock(&(apdsafe->cache_lock));

  pthread_rwlock_rdlock(&(apdsafe->howfs->cache_lock));
  f = apdsafe->howfs->stat.freq/1000.*2.;
  pthread_rwlock_unlock(&(apdsafe->howfs->cache_lock));

  /* semwait for apdcnt */
  clock_gettime(CLOCK_REALTIME, &ts1);
  ts1.tv_sec += 2;
  ImageStreamIO_semtimedwait(apdsafe->shm_apdcnt, 5, &ts1);

  // if semwait timeout
  if(errno == ETIMEDOUT) return NULL;

  /* copy APD count to local */
  memcpy(data, apdsafe->apdcnt, APD_NUM*sizeof(float));

  /* check HOWFS APD count */
  have = data[hapdmap[0]]*f;
  hmax = have;
  for(i=1; i<HOAPD_NUM; i++){
    tmp = data[hapdmap[i]]*f; // kcnt/s
    have += tmp;
    if(hmax < tmp)
      hmax = tmp;
  }
  have /= HOAPD_NUM;

  /* check LOWFS APD count */
  lave = data[lapdmap[0]]*f;
  lmax = have;
  for(i=1; i<LOAPD_NUM; i++){
    tmp = data[lapdmap[i]]*f; // kcnt/s
    lave += tmp;
    if(lmax < tmp)
      lmax = tmp;
  }
  lave /= LOAPD_NUM;

  /* if hmax|lmax is above the limit, add cnt */
  if(hmax > max_limit || lmax > max_limit) cnt++;
  else cnt=0;

  /* if cnt is larger than nframe, go to emergency mode */
  if(cnt>=nframe){
 

    /* emergency shutter close */
    if(emergency == 1){
      if(hmax > max_limit) 
	info("%s : Too high APD count in HOAPDs (Max = %.0f kcnt/s) !!!!", apdsafe->header, hmax);
      if(lmax > max_limit) 
	info("%s : Too high APD count in LOAPDs (Max = %.0f kcnt/s) !!!!", apdsafe->header, lmax);

      info("%s : Emergency Shutter Close !!!!", apdsafe->header);
      info("%s : loop off", apdsafe->header);
      system("echo \""FIFO_SET_COMMAND" "LOOP_FIFO_ONOFF" OFF\" >> "FIFO_FPSCTRL_NAME);
      if(hmax > max_limit){
	info("%s : howfs lash close", apdsafe->header);
	howfs_lash_close(apdsafe->howfs, errstr);
      }
      if(lmax > max_limit){
	info("%s : lowfs lash close", apdsafe->header);
	lowfs_lash_close(apdsafe->lowfs, errstr);
      }
      cnt = 0;
    }

  }

  pthread_rwlock_wrlock(&(apdsafe->cache_lock));
  apdsafe->cnt = cnt;
  pthread_rwlock_unlock(&(apdsafe->cache_lock));

  return NULL;
}


/*
 * Initialize data to handle controller
 */
int apdsafe_init(apdsafe_t *apdsafe, const char *header){
  int ret = 0;
  poll_t *poll = &(apdsafe->poll);

  if (header != NULL) {
    debug("%s: init", header);
    apdsafe->header = strdup(header);
  } else {
    debug("%s: init", APDSAFE_HEADER_DEFAULT);
    apdsafe->header = strdup(APDSAFE_HEADER_DEFAULT);
  }
  if (apdsafe->header == NULL) {
    return -1;
  }

  /* initialize polling */
  if ((ret = poll_init(poll, (void *)apdsafe_poll, apdsafe, apdsafe->header)) < 0) {
    apdsafe_free(apdsafe);
    return ret;
  }
  poll_setinterval(poll, APDSAFE_POLL_INTERVAL);

  /* init cashe */
  pthread_rwlock_init(&(apdsafe->cache_lock), NULL);
  apdsafe->cnt = 0;
  apdsafe->nframe = APDSAFE_DEF_NFRAME;
  apdsafe->max_limit = APDSAFE_DEF_LIMIT;
  apdsafe->emergency = 1; // emergency mode on

  return 0;
}

/*
 * Free resources in data
 */
int apdsafe_free(apdsafe_t *apdsafe){
  debug("%s: free", apdsafe->header);
  free(apdsafe->header);
    
  return 0;
}

/*
 * Open device
 */
int apdsafe_open(apdsafe_t *apdsafe){
  shms_t *shms = apdsafe->shms;
  struct cacao_shm *shm;
  char errstr[APDSAFE_ERRSTR_MAX + 1];

 /* set APD shm shortcut */
  if((shm = bsearch(KEY_APD_COUNT2, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) == NULL){
    sprintf(errstr, "\"%s\" no matched keyword", KEY_APD_COUNT2);
    error_num(errno, "%s", errstr);
    return -1;
  }
  apdsafe->apdcnt = shm->image.array.F;
  apdsafe->shm_apdcnt = &(shm->image);

  /* start polling by default */
  poll_start(&(apdsafe->poll));

  return 0;
}

/*
 * Close device
 */
int apdsafe_close(apdsafe_t *apdsafe){
  return 0;
}
