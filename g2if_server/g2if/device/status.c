/* -------------------------------------------------------------------------
 * status.c -- Function for handling STATUS control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/11   Y. Ono        Initial version
 *    2019/10/01   Y. Ono        Complete loop and gain status through fifo
 *    2023/04/19   V. Deo        See https://github.com/scexao-org/ao3krts
 * -------------------------------------------------------------------------
 */

#include <stdio.h>			/* for snprintf() */
#include <math.h>			/* for sqrt() */
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
#include "status.h"			/* for status_t */

/* Device handler operation functions */
const struct device_operations status_ops = {
  .init = (int (*)(void *, const char *))status_init,
  .free = (int (*)(void *))status_free,
  .open = (int (*)(void *))status_open,
  .close = (int (*)(void *))status_close,
  .procconf = (int (*)(void *, const char *, int,	const char **))status_procconf,
  .postconf = (int (*)(void *))status_postconf,
  .proccmd = (int (*)(client_t *, void *))status_proccmd,
};

void init_statistics(struct statistics *stat){
  stat->ave = 0;
  stat->std = 0;
  stat->min = 0;
  stat->max = 0;
}

/*
 *  compute ave, std, min, max from data
 */
void get_statistics(float *data, const int n, struct statistics *stat){
  int i;
  float tmp;

  /* ave, min, max */
  stat->ave = 0;
  stat->min = data[0];
  stat->max = data[0];
  for(i=0; i<n; i++){
    stat->ave += data[i];
    if(stat->min > data[i]) stat->min = data[i];
    if(stat->max < data[i]) stat->max = data[i];
  }
  stat->ave /= n;

  /* std */
  stat->std = 0;
  for(i=0; i<n; i++){
    tmp = data[i] - stat->ave;
    stat->std += tmp*tmp;
  }
  stat->std = sqrt(stat->std / n);

  return ;
}


/*
 *  initialize status_fast
 */
void init_status_fast(struct status_fast *stat){
  int i;

  for(i=0; i<HOAPD_NUM; i++) stat->ave_hapdcnt[i] = 0;
  for(i=0; i<CURV_NUM; i++) stat->ave_curv[i] = 0;
  for(i=0; i<DMACT_NUM; i++) stat->ave_dmvolt[i] = 0;
  for(i=0; i<LOAPD_NUM; i++) stat->ave_lapdcnt[i] = 0;
  stat->ave_dmtt[0] = 0;
  stat->ave_dmtt[1] = 0;
  stat->ave_wtt[0] = 0;
  stat->ave_wtt[1] = 0;
  stat->ave_lott[0] = 0;
  stat->ave_lott[1] = 0;
  stat->ave_lodf = 0;
  stat->ave_hmag = 0;
  stat->ave_lmag = 0;

  init_statistics(&(stat->ave_hapdstat));
  init_statistics(&(stat->ave_lapdstat));
  init_statistics(&(stat->ave_curvstat));
  init_statistics(&(stat->ave_dmvoltstat));

  return ;
}


/*
 *  Status polling routine (fast)
 */
static void *status_poll_fast(status_t *status){
  int i, k, nFrame;
  int i1, i2, i3, i4;
  float *data;
  struct status_fast stat;
  howfs_t *vm = status->howfs;
  struct timespec ts1;
  char timestr[32];
  struct timeval tv;
  struct tm tm;

  /* init */
  init_status_fast(&stat);
  pthread_rwlock_rdlock(&(status->cache_lock));
  nFrame = status->nFrame;
  pthread_rwlock_unlock(&(status->cache_lock));

  for(k=0; k<nFrame; k++){
    /* sem_wait for apdmatrix */
    // FIXME the timeout is purposefully extremely slow to offset the fact that
    // APDs are NOT running at this point.
    clock_gettime(CLOCK_REALTIME, &ts1);
        ts1.tv_sec += (ts1.tv_nsec + 5000000) / 1000000000;
        ts1.tv_nsec = (ts1.tv_nsec + 5000000) % 1000000000;
    ImageStreamIO_semtimedwait(status->shm_apdcnt, 5, &ts1);

    /* get howfs apd count (+) from shm */
    for(i=0; i<HOAPD_NUM; i++) stat.ave_hapdcnt[i] += status->apdcnt[status->hapdmap[i]];

    /* get lowfs apd count from shm */
    for(i=0; i<LOAPD_NUM; i++) stat.ave_lapdcnt[i] += status->apdcnt[status->lapdmap[i]] + status->apdcnt[status->lapdmap[i]+APD_NUM];

    /* get curvature from shm */
    for(i=0; i<CURV_NUM; i++) stat.ave_curv[i] += status->curv[i];

    /* get dm voltage from shm */
    for(i=0; i<DMACT_NUM; i++) stat.ave_dmvolt[i] += status->dmvolt[i];

    /* get dmtt from shm */
    stat.ave_dmtt[0] += status->dmtt[0];
    stat.ave_dmtt[1] += status->dmtt[1];

    /* get wtt from shm */
    stat.ave_wtt[0] += status->wtt[0];
    stat.ave_wtt[1] += status->wtt[1];

    /* get LO tip/tilt/defocus */
    stat.ave_lott[0] += status->lott[0];
    stat.ave_lott[1] += status->lott[1];
    stat.ave_lodf += status->lodf[0];
  }

  // average
  for(i=0; i<HOAPD_NUM; i++) stat.ave_hapdcnt[i] /= nFrame;
  for(i=0; i<LOAPD_NUM; i++) stat.ave_lapdcnt[i] /= nFrame;
  for(i=0; i<CURV_NUM; i++) stat.ave_curv[i] /= nFrame;
  for(i=0; i<DMACT_NUM; i++) stat.ave_dmvolt[i] /= nFrame;
  stat.ave_dmtt[0] /= nFrame;
  stat.ave_dmtt[1] /= nFrame;
  stat.ave_wtt[0] /= nFrame;
  stat.ave_wtt[1] /= nFrame;
  stat.ave_lott[0] /= nFrame;
  stat.ave_lott[1] /= nFrame;
  stat.ave_lodf /= nFrame;

  // unit conversion
  for(i=0; i<HOAPD_NUM; i++) stat.ave_hapdcnt[i] *= vm->stat.freq/1000.*2;
  for(i=0; i<LOAPD_NUM; i++) stat.ave_lapdcnt[i] *= vm->stat.freq/1000.*2; // what is LOWFS framerate???

  // LOWFS slope
  data = stat.ave_lapdcnt;
  i1 = 0; i2 = 1; i3 = 4; i4 = 5; 
  stat.ave_lslope[0] = ((data[i2]+data[i4])-(data[i1]+data[i3]))/2/(data[i1]+data[i2]+data[i3]+data[i4]);
  stat.ave_lslope[1] = ((data[i1]+data[i2])-(data[i3]+data[i4]))/2/(data[i1]+data[i2]+data[i3]+data[i4]);
  i1 = 2; i2 = 3; i3 = 6; i4 = 7; 
  stat.ave_lslope[2] = ((data[i2]+data[i4])-(data[i1]+data[i3]))/2/(data[i1]+data[i2]+data[i3]+data[i4]);
  stat.ave_lslope[3] = ((data[i1]+data[i2])-(data[i3]+data[i4]))/2/(data[i1]+data[i2]+data[i3]+data[i4]);
  i1 = 8; i2 = 9; i3 = 12; i4 = 13; 
  stat.ave_lslope[4] = ((data[i2]+data[i4])-(data[i1]+data[i3]))/2/(data[i1]+data[i2]+data[i3]+data[i4]);
  stat.ave_lslope[5] = ((data[i1]+data[i2])-(data[i3]+data[i4]))/2/(data[i1]+data[i2]+data[i3]+data[i4]);
  i1 = 10; i2 = 11; i3 = 14; i4 = 15; 
  stat.ave_lslope[6] = ((data[i2]+data[i4])-(data[i1]+data[i3]))/2/(data[i1]+data[i2]+data[i3]+data[i4]);
  stat.ave_lslope[7] = ((data[i1]+data[i2])-(data[i3]+data[i4]))/2/(data[i1]+data[i2]+data[i3]+data[i4]);

  // get statistics
  get_statistics(stat.ave_hapdcnt, HOAPD_NUM, &(stat.ave_hapdstat));
  get_statistics(stat.ave_lapdcnt, LOAPD_NUM, &(stat.ave_lapdstat));
  get_statistics(stat.ave_curv, CURV_NUM, &(stat.ave_curvstat));
  get_statistics(stat.ave_dmvolt, DMACT_NUM, &(stat.ave_dmvoltstat));

  // corresponding GS magnitude
  stat.ave_hmag = FUNC_APD_HMAG(stat.ave_hapdstat.ave);
  if(isinf(stat.ave_hmag)) stat.ave_hmag = -99;
  stat.ave_lmag = FUNC_APD_LMAG(stat.ave_lapdstat.ave);
  if(isinf(stat.ave_lmag)) stat.ave_lmag = -99;

  // update cashe
  pthread_rwlock_wrlock(&(status->cache_lock));
  status->stat_fast = stat;
  pthread_rwlock_unlock(&(status->cache_lock));
  
  if(status->log_telemetry == 1){
    pthread_rwlock_rdlock(&(status->cache_lock));
    gettimeofday(&tv, NULL);
    strftime(timestr, sizeof(timestr), "[%Y/%m/%d %H:%M:%S",
	     localtime_r(&(tv.tv_sec), &tm));
    strncatf(timestr, sizeof(timestr), ".%03d] ", tv.tv_usec / 1000);
    fprintf(status->fp_telemetry,"%s: %7.2f  %7.2f  %.4f  %7.2f  %7.2f  %7.4f  %7.4f  %7.4f  %7.4f\n",
	    timestr,
	    status->stat_fast.ave_hapdstat.ave,
	    status->stat_fast.ave_lapdstat.ave,
	    status->stat_fast.ave_curvstat.std,
	    status->stat_fast.ave_dmvoltstat.ave,
	    status->stat_fast.ave_dmvoltstat.std,
	    stat.ave_dmtt[0], stat.ave_dmtt[1],
	    stat.ave_wtt[0], stat.ave_wtt[1]);
    pthread_rwlock_unlock(&(status->cache_lock));
  }

  return NULL;
}


/*
 *  Status polling routine (slow)
 */
static void *status_poll_slow(status_t *status){
  int ret = 0;
  struct gain_stat gstat;
  struct howfs_stat hwstat;
  struct lowfs_stat lwstat;
  struct loop_stat lstat;
  char errstr[STATUS_ERRSTR_MAX + 1];

  /* update loop */
  loop_getstat(status->loop, &lstat);
  loop_savestat(status->loop, &lstat);

  /* update gain */
  gain_getstat(status->gain, &gstat);
  gain_savestat(status->gain, &gstat);

  /* update howfs */
  // FIXME COMMENTED ENTIRELY CAUSE THIS WILL STALL FOR
  // A VERY LONG TIMEOUT if no ping on 10.0.0.3
  /*
  ret = howfs_getstat(status->howfs, &hwstat, errstr);
  if(ret == 0) howfs_savestat(status->howfs, &hwstat);
  //*/

  /* update lowfs */
  /*
  ret = lowfs_getstat(status->lowfs, &lwstat, errstr);
  if(ret == 0) lowfs_savestat(status->lowfs, &lwstat);
  //*/

  return NULL;
}

/*
 * Initialize data to handle controller
 */
int status_init(status_t *status, const char *header){
  int ret = 0;
  poll_t *poll_fast = &(status->poll_fast);
  poll_t *poll_slow = &(status->poll_slow);
    printf("ptr poll_fast %p %p\n", poll_fast, &(status->poll_fast));
    printf("ptr poll_slow %p %p\n", poll_slow, &(status->poll_slow));

  if (header != NULL) {
    debug("%s: init", header);
    status->header = strdup(header);
  } else {
    debug("%s: init", STATUS_HEADER_DEFAULT);
    status->header = strdup(STATUS_HEADER_DEFAULT);
  }
  if (status->header == NULL) {
    return -1;
  }

  /* initialize fast polling */
  if ((ret = poll_init(poll_fast, (void *)status_poll_fast, status, status->header)) < 0) {
    status_free(status);
    return ret;
  }
  poll_setinterval(poll_fast, STATUS_POLL_INTERVAL_FAST);

  /* initialize slow polling */
  if ((ret = poll_init(poll_slow, (void *)status_poll_slow, status, status->header)) < 0) {
    status_free(status);
    return ret;
  }
  poll_setinterval(poll_slow, STATUS_POLL_INTERVAL_SLOW);

  /* init nFrame */
  status->nFrame = STATUS_DEF_NFRAME;

  /* init cashe */
  init_status_fast(&(status->stat_fast));
  pthread_rwlock_init(&(status->cache_lock), NULL);

  /* init log but not yet*/
  status->log_telemetry = 0;

  return 0;
}

/*
 * Free resources in data
 */
int status_free(status_t *status){
  debug("%s: free", status->header);
  free(status->header);
  fclose(status->fp_telemetry);
  return 0;
}

/*
 * Open device
 */
int status_open(status_t *status){
  const char *header = status->header;
  shms_t *shms = status->shms;
  struct cacao_shm *shm;
  int i, k1, k2;
  FILE *fp;
  char errstr[STATUS_ERRSTR_MAX + 1];

  /* load configuration file for HOWFS APD */
  info("%s: load howfs apd config \"%s\"", header, status->hapdconf);
  status->hapdmap = (int *)malloc(HOAPD_NUM * sizeof(int));
  fp = fopen(status->hapdconf, "r");
  for(i=0; i<HOAPD_NUM; i++){
    fscanf(fp, "%d  %d", &k1, &k2);
    status->hapdmap[k1-1] = k2-1;
  }
  fclose(fp);
  status->apdsafe->hapdmap = status->hapdmap;

  /* load configuration file for LOWFS APD */
  info("%s: load lowfs apd config \"%s\"", header, status->lapdconf);
  status->lapdmap = (int *)malloc(LOAPD_NUM * sizeof(int));
  fp = fopen(status->lapdconf, "r");
  for(i=0; i<LOAPD_NUM; i++){
    fscanf(fp, "%d  %d", &k1, &k2);
    status->lapdmap[k1-188-1] = k2-1;
  }
  fclose(fp);
  status->apdsafe->lapdmap = status->lapdmap;

  /* set APD shm shortcut */
  if((shm = bsearch(KEY_APD_COUNT, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) == NULL){
    sprintf(errstr, "\"%s\" no matched keyword", KEY_APD_COUNT);
    error_num(errno, "%s", errstr);
    return -1;
  }
  status->apdcnt = shm->image.array.F;
  status->shm_apdcnt = &(shm->image);

  /* set DM volt shm shortcut */
  if((shm = bsearch(KEY_DM_VOLT, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) == NULL){
    sprintf(errstr, "\"%s\" no matched keyword", KEY_DM_VOLT);
    error_num(errno, "%s", errstr);
    return -1;
  }
  status->dmvolt = shm->image.array.F;
  /* set Curv shm shortcut */
  if((shm = bsearch(KEY_CURV, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) == NULL){
    sprintf(errstr, "\"%s\" no matched keyword", KEY_CURV);
    error_num(errno, "%s", errstr);
    return -1;
  }
  status->curv = shm->image.array.F;
  /* set DMTT shm shortcut */
  if((shm = bsearch(KEY_TTM_TT, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) == NULL){
    sprintf(errstr, "\"%s\" no matched keyword", KEY_TTM_TT);
    error_num(errno, "%s", errstr);
    return -1;
  }
  status->dmtt = shm->image.array.F;
  /* set WTT shm shortcut */
  if((shm = bsearch(KEY_WTT_TT, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) == NULL){
    sprintf(errstr, "\"%s\" no matched keyword", KEY_WTT_TT);
    error_num(errno, "%s", errstr);
    return -1;
  }
  status->wtt = shm->image.array.F;
  /* set LO_TT shm shortcut */
  if((shm = bsearch(KEY_LO_TT, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) == NULL){
    sprintf(errstr, "\"%s\" no matched keyword", KEY_LO_TT);
    error_num(errno, "%s", errstr);
    return -1;
  }
  status->lott = shm->image.array.F;
  /* set LO_DF shm shortcut */
  if((shm = bsearch(KEY_LO_DF, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) == NULL){
    sprintf(errstr, "\"%s\" no matched keyword", KEY_LO_DF);
    error_num(errno, "%s", errstr);
    return -1;
  }
  status->lodf = shm->image.array.F;

  /* Create the telemetry log file */
  time_t timer;
  struct tm *ut;
  char fname[256];

  timer = time(NULL);
  ut = gmtime(&timer);
  sprintf(fname, "%s/g2if_telemetry_%04d%02d%02d.txt", status->foldtele,
          ut->tm_year + 1900, ut->tm_mon + 1, ut->tm_mday);
  status->fp_telemetry = fopen(fname, "a");
  status->log_telemetry = 1;

  /* start polling */
  poll_start(&(status->poll_fast));
  poll_start(&(status->poll_slow));

  return 0;
}

/*
 * Close device
 */
int status_close(status_t *status){
  fclose(status->fp_telemetry);
  return 0;
}
