/* -------------------------------------------------------------------------
 * shms_conf.c -- Functions for reading configuration file
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/18   Y. Ono        Initial version
 * -------------------------------------------------------------------------
 */
#include <stdio.h>			/* for snprintf() */
#include <string.h>			/* for strcmp(), strncpy() */
#include <limits.h>			/* for USHRT_MAX */
#include <values.h>                     /* for DBL_MAX */
#include <errno.h>			/* for errno */
#include "log.h"			/* for error(), info(), debug() */
#include "conf.h"			/* for setpar_int() and etc */
#include "stringx.h"			/* for strjoin() */
#include "shms.h"			/* for shms_t */

/* Comparison for sort */
static int shms_sort_comp(const void *shm1, const void *shm2){
  return strcmp(((struct cacao_shm *)shm1)->key, ((struct cacao_shm *)shm2)->key);
}

static int shms_key_setpar(int argc, const char **argv, struct cacao_shm *shm){

  /* check number of arguments */
  if (setpar_chkargi(argc, argv, 1) < 0){
    return -1;
  }

  /* check status parameter length */
  if (strlen(argv[1]) > KEY_STR_MAX -1){
    error_num(errno, "keyword length too lonng -- %s", argv[1]);
    return -1;
  }

  /*initialize status*/
  shm->key[0] = '\0';

  /* get status parameter name */
  strncat(shm->key, argv[1], KEY_STR_MAX -1);

  /* Allocate address to the shared memory to read */
  if((ImageStreamIO_read_sharedmem_image_toIMAGE(shm->key, &shm->image)) != 0){
    return -1;
  }

  return 0;
}


/*
 * Process a configuration parameter for shmler
 */
int shms_procconf(shms_t *shms, const char *sect, int argc, const char **argv){
  const char *key = argv[0];
  char subsect[32];
  int ret;
  
  if (getsubsect(sect, 1, subsect, sizeof(subsect))) {
    setpar_unknown_sect(sect);
    return 0;
  } else if (strcmp(key, "key") == 0){  /* keyword for shared memory to read/write */
    ret = shms_key_setpar(argc, argv, &(shms->shm[shms->shm_num]));
    if (ret == 0){
      shms->shm_num += 1;
    }
    else if(ret < 0){
      error_num(errno, "Faild to read sheard memory during configuration process: %s", argv[1]);
      return -1;
    }
    return 0;
  }
  setpar_unknown_par(key);
  return 0;
}

/*
 * Print all configuration parameters
 */
int shms_postconf(shms_t *shms){
  const char *header = shms->header;

  /* sort shared memory array */
  qsort(shms->shm, shms->shm_num, sizeof(struct cacao_shm), shms_sort_comp);

  int i;
    
  for (i=0;i<shms->shm_num;i++){
    info("%s: key = %s", header, shms->shm[i].key);
  }
  return 0;

}
