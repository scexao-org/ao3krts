/* -------------------------------------------------------------------------
 * cmtx_conf.c -- Functions for reading configuration file
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/09/24   Y. Ono        Initial version
 *
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
#include "cmtx.h"	               	/* for cmtx_t */


/*
 * Process a configuration parameter for cmtxler
 */
int cmtx_procconf(cmtx_t *cmtx, const char *sect, int argc, const char **argv){
  const char *key = argv[0];
  char subsect[32];
  
  if (getsubsect(sect, 1, subsect, sizeof(subsect))) {
    setpar_unknown_sect(sect);
    return 0;
  } else if (strcmp(key, "ngs") == 0){  /* keyword for ngs */
    return setpar_strdup(argc, argv, 1, &(cmtx->ngs));
  } else if (strcmp(key, "lgs") == 0){  /* keyword for lgs */
    return setpar_strdup(argc, argv, 1, &(cmtx->lgs));
  }
  setpar_unknown_par(key);
  return 0;
}

/*
 * Print all configuration parameters
 */
int cmtx_postconf(cmtx_t *cmtx){
  const char *header = cmtx->header;

  info("%s: load ngs = \"%s\"", header, cmtx->ngs);
  info("%s: load lgs = \"%s\"", header, cmtx->lgs);

  return 0;
}
