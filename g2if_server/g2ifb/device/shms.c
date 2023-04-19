/* -------------------------------------------------------------------------
 * shms.h -- Function for handling cacao SHM
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/18   Y. Ono        Initial version
 *
 * -------------------------------------------------------------------------
 */

#include <stdio.h>				/* for snprintf() */
#include <stdlib.h>				/* for free() */
#include <string.h>				/* for strcmp(), strlen() */
#include <ctype.h>				/* for tolower() */
#include <math.h>				/* for round() */
#include <errno.h>				/* for errno */
#include "log.h"				/* for error(), info(), debug() */
#include "conf.h"				/* for getsubsect(), setpar_*() */
#include "comm.h"				/* for comm_*() */
#include "device.h"				/* for struct device_operations */
#include "server.h"				/* for sendres(), sendres_*() */
#include "stringx.h"			        /* for strtolower() */
#include "shms.h"                                /* for shms_t */

/* Device handler operation functions */
const struct device_operations shms_ops = {
    .init = (int (*)(void *, const char *))shms_init,
    .free = (int (*)(void *))shms_free,
    .open = (int (*)(void *))shms_open,
    .close = (int (*)(void *))shms_close,
    .procconf = (int (*)(void *, const char *, int, const char **))shms_procconf,
    .postconf = (int (*)(void *))shms_postconf,
    .proccmd = (int (*)(client_t *, void *))shms_proccmd,
};
 
/* Comparison for search */
int shms_search_comp(const void *key, const void *shm){
  return strcmp((char *)key, ((struct cacao_shm *)shm)->key);
}

/*
 * Initialize data for handling shms shms
 */
int shms_init(shms_t *shms, const char *header){

  if (header != NULL) {
    debug("%s: init", header);
    shms->header = strdup(header);
  } else {
    debug("%s: init", SHMS_HEADER_DEFAULT);
    shms->header = strdup(SHMS_HEADER_DEFAULT);
  }
  if (shms->header == NULL) {
    return -1;
  }

  /* initialize the number of shared memory to read */
  shms->shm_num = 0;
  
  return 0;
}

/*
 * Free resources in data for handling shmslers
 */
int shms_free(shms_t *shms){
  debug("%s: free", shms->header);
  free(shms->header);

  return 0;
}

/*
 * Close device
 */
int shms_close(shms_t *shms){
    return 0;
}

/*
 * Open device 
 */
int shms_open(shms_t *shms){

  return 0;
}


/*
 * write in shared memory (float)
 */
int shms_write_float(shms_t *shms, const char *key, const float *value, const int num, char *errstr){
  struct cacao_shm *shm;
  int i;

  if((shm = bsearch(key, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) != NULL){
    if(shm->image.md[0].nelement != num){
      sprintf(errstr, "Wrong number of elements in shared memory (%s)-- %ld vs %d", key, shm->image.md[0].nelement, num);
      error_num(errno, "%s", errstr);
      return -1;
    }
    for (i=0; i<num; i++) shm->image.array.F[i] = value[i];
  }
  else{
    sprintf(errstr, "%s : No matched keyword", key);
    error_num(errno, "%s", errstr);
    return -1;
  }
  return 0;
}

/*
 * write in shared memory (uint32)
 */
int shms_write_uint32(shms_t *shms, const char *key, const uint32_t *value, const int num, char *errstr){
  struct cacao_shm *shm;
  int i;

  if((shm = bsearch(key, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) != NULL){
    if(shm->image.md[0].nelement != num){
      sprintf(errstr, "Wrong number of elements in shared memory (%s)-- %ld vs %d", key, shm->image.md[0].nelement, num);
      error_num(errno, "%s", errstr);
      return -1;
    }
    for (i=0; i<num; i++) shm->image.array.UI32[i] = value[i];
  }
  else{
    sprintf(errstr, "%s : No matched keyword", key);
    error_num(errno, "%s", errstr);
    return -1;
  }
  return 0;
}

/*
 * read shared memory (float)
 */
int shms_read_float(shms_t *shms, const char *key, float *value, const int num, char *errstr){
  struct cacao_shm *shm;
  int i;

  if((shm = bsearch(key, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) != NULL){
    if(shm->image.md[0].nelement != num){
      sprintf(errstr, "Wrong number of elements in shared memory (%s)-- %ld vs %d", key, shm->image.md[0].nelement, num);
      error_num(errno, "%s", errstr);
      return -1;
    }
    for (i=0; i<num; i++) value[i] = shm->image.array.F[i];
  }
  else{
    sprintf(errstr, "%s : No matched keyword", key);

    error_num(errno, "%s", errstr);
    return -1;
  }
  return 0;
}

/*
 * read shared memory (uint32)
 */
int shms_read_uint32(shms_t *shms, const char *key, uint32_t *value, const int num, char *errstr){
  struct cacao_shm *shm;
  int i;

  if((shm = bsearch(key, shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_search_comp)) != NULL){
    if(shm->image.md[0].nelement != num){
      sprintf(errstr, "Wrong number of elements in shared memory (%s)-- %ld vs %d", key, shm->image.md[0].nelement, num);
      error_num(errno, "%s", errstr);
      return -1;
    }
    for (i=0; i<num; i++) value[i] = shm->image.array.UI32[i];
  }
  else{
    sprintf(errstr, "%s : No matched keyword", key);
    error_num(errno, "%s", errstr);
    return -1;
  }
  return 0;
}

