/* -------------------------------------------------------------------------
 * adf_conf.c -- Functions for reading configuration file
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
#include "adf.h"			/* for adf_t */


/*
 * Process a configuration parameter for adfler
 */
int adf_procconf(adf_t *adf, const char *sect, int argc, const char **argv){
  const char *key = argv[0];
  char subsect[32];
  
  if (getsubsect(sect, 1, subsect, sizeof(subsect))) {
    setpar_unknown_sect(sect);
    return 0;
  }
  setpar_unknown_par(key);
  return 0;
}

/*
 * Print all configuration parameters
 */
int adf_postconf(adf_t *adf){

  return 0;
}
