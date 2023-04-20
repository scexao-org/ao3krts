/* -------------------------------------------------------------------------
 * gain.c -- Function for handling GAIN control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/11   Y. Ono        Initial version
 *    2019/09/26   Y. Ono        Add fifo for DMG
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
#include "gain.h"			/* for gain_t */

/* Device handler operation functions */

const struct device_operations gain_ops = {
  .init = (int (*)(void *, const char *))gain_init,
  .free = (int (*)(void *))gain_free,
  .open = (int (*)(void *))gain_open,
  .close = (int (*)(void *))gain_close,
  .procconf = (int (*)(void *, const char *, int,	const char **))gain_procconf,
  .postconf = (int (*)(void *))gain_postconf,
  .proccmd = (int (*)(client_t *, void *))gain_proccmd,
};

/*
 * Initialize data to handle controller
 */
int gain_init(gain_t *gain, const char *header){
  int ret = 0;
  comm_t *comm = &(gain->comm);

  if (header != NULL) {
    debug("%s: init", header);
    gain->header = strdup(header);
  } else {
    debug("%s: init", GAIN_HEADER_DEFAULT);
    gain->header = strdup(GAIN_HEADER_DEFAULT);
  }
  if (gain->header == NULL) {
    return -1;
  }

  /* init cashe */
  gain->stat.dmg = 0.0;
  gain->stat.ttg = 0.0;
  gain->stat.htt = 0.0;
  gain->stat.hdf = 0.0;
  gain->stat.ltt[0] = 0.0;
  gain->stat.ltt[1] = 0.0;
  gain->stat.ldf = 0.0;
  gain->stat.wtt = 0.0;
  gain->stat.adf = 0.0;
  gain->scanstep = 0.05;
  gain->scaninterval = 10;
  pthread_rwlock_init(&(gain->cache_lock), NULL);

  /* init fifo */
  fifo_init(&(gain->fifo));
  fifo_set_name(&(gain->fifo), GAIN_FIFO_NAME);
  fifo_create(&(gain->fifo));

  if ((ret = comm_init(comm, gain->header)) < 0) {
    free(gain->header);
    return ret;
  }
  comm_setdelim(comm, GAIN_DELIM_IN, GAIN_DELIM_OUT);

  return 0;
}

/*
 * Free resources in data
 */
int gain_free(gain_t *gain){
  debug("%s: free", gain->header);
  free(gain->header);
  fifo_free(&(gain->fifo));

  comm_free(&(gain->comm));

  return 0;
}

/*
 * Open device
 */
int gain_open(gain_t *gain){
  shms_t *shms = gain->shms;
  struct cacao_shm *shm;

  if(fifo_open(&(gain->fifo)) < 0){
    info(RES_HEAD_ERR"%s: Failed to open fifo (%s)\n", gain->header, gain->fifo.name);
    return -1;
  }

  /* set DM volt shm shortcut */
  if((shm = bsearch(KEY_CURV, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) == NULL){
    info(RES_HEAD_ERR"%s: No matched keyword (%s)\n", gain->header, gain->fifo.name);
    return -1;
  }
  gain->curv = shm->image.array.F;
  gain->shm_curv = &(shm->image);

  return 0;
}

/*
 * Close device
 */
int gain_close(gain_t *gain){
  if((fifo_close(&(gain->fifo))) < 0){
    info(RES_HEAD_ERR"%s: Failed to close fifo (%s)\n", gain->header, gain->fifo.name);
    return -1;
  }
  return 0;
}

/*
 * Get DMG from CACAO through fifo
 */
int gain_getdmg(gain_t *gain, float *dmg){
  int ret = 0;
  char buff[GAIN_COMM_BUFSIZ];
  char *arg[GAIN_STATARG_MAX];

  /* send fwrval command to cacao */
  system("echo \""FIFO_GET_COMMAND" "GAIN_FIFO_DMG" "GAIN_FIFO_NAME"\" >> "FIFO_FPSCTRL_NAME);

  /* read fifo */
  if((ret = fifo_read(&(gain->fifo), buff)) == 0){
    /* parse text */
    ret = strsplit_delim(buff, arg, " ,=:{}()[]'\n\r\t\v\f", GAIN_STATARG_MAX);
    *dmg = (float)atof(arg[4]);
  } else{
    info(RES_HEAD_ERR"%s: %s\n", gain->header, buff);
    *dmg = -99;
    return -1;
  }
  return 0;
}

/*
 * Get TTG from CACAO through fifo
 */
int gain_getttg(gain_t *gain, float *ttg){
  int ret = 0;
  char buff[GAIN_COMM_BUFSIZ];
  char *arg[GAIN_STATARG_MAX];

  /* send fwrval command to cacao */
  system("echo \""FIFO_GET_COMMAND" "GAIN_FIFO_TTG" "GAIN_FIFO_NAME"\" >> "FIFO_FPSCTRL_NAME);

  /* read fifo */
  if((ret = fifo_read(&(gain->fifo), buff)) == 0){
    /* parse text */
    ret = strsplit_delim(buff, arg, " ,=:{}()[]'\n\r\t\v\f", GAIN_STATARG_MAX);
    *ttg = (float)atof(arg[4]);
  } else{
    info(RES_HEAD_ERR"%s: %s\n", gain->header, buff);
    *ttg = -99;
    return -1;
  }
  return 0;
}

/*
 * Set DMG through fifo
 */
int gain_setdmg(gain_t *gain, float dmg){
  char script[GAIN_COMM_BUFSIZ];

  /* make command string */
  sprintf(script,"echo \""FIFO_SET_COMMAND" "GAIN_FIFO_DMG" %.4f\" >> "FIFO_FPSCTRL_NAME, dmg);

  /* send command to fifo */
  system(script);

  return 0;
}

/*
 * Set TTG through fifo
 */
int gain_setttg(gain_t *gain, float ttg){
  char script[GAIN_COMM_BUFSIZ];

  /* make command string */
  sprintf(script,"echo \""FIFO_SET_COMMAND" "GAIN_FIFO_TTG" %.4f\" >> "FIFO_FPSCTRL_NAME, ttg);

  /* send command to fifo */
  system(script);

  return 0;
}

/*
 * Get status from shared memory
 */
int gain_getstat(gain_t *gain, struct gain_stat *stat){
  shms_t *shms = gain->shms;
  char errstr[GAIN_ERRSTR_MAX + 1];

  /* read DMG gain */
  gain_getdmg(gain, &(stat->dmg));

  /* read TTG gain */
  gain_getttg(gain, &(stat->ttg));


  /* read HTT gain */
  if(shms_read_float(shms, KEY_HTT_GAIN, &(stat->htt), 1, errstr) != 0)
    stat->htt = 0.0;

  /* read HDF gain */
  if(shms_read_float(shms, KEY_HDF_GAIN, &(stat->hdf), 1, errstr) != 0)
    stat->hdf = 0.0;

  /* read LTT gain */
  if(shms_read_float(shms, KEY_LTT_GAIN, stat->ltt, 2, errstr) != 0){
    stat->ltt[0] = 0.0;
    stat->ltt[1] = 0.0;
  }

  /* read LDF gain */
  if(shms_read_float(shms, KEY_LDF_GAIN, &(stat->ldf), 1, errstr) != 0)
    stat->ldf = 0.0;

  /* read WTT gain */
  if(shms_read_float(shms, KEY_WTT_GAIN, &(stat->wtt), 1, errstr) != 0)
    stat->wtt = 0.0;

  /* read ADF gain */
  if(shms_read_float(shms, KEY_ADF_GAIN, &(stat->adf), 1, errstr) != 0)
    stat->adf = 0.0;

  return 0;
}


/*
 * Save status into cashe
 */
int gain_savestat(gain_t *gain, struct gain_stat *stat){
  pthread_rwlock_wrlock(&(gain->cache_lock));
  gain->stat = *stat;
  pthread_rwlock_unlock(&(gain->cache_lock));
  return 0;
}
