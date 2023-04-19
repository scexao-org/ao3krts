/* -------------------------------------------------------------------------
 * apdsafe_conf.c -- Functions for reading configuration file
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/06/20    Y. Ono        Initial version
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
#include "apdsafe.h"			/* for apdsafe_t */


/*
 * Process a configuration parameter for apdsafeler
 */
int apdsafe_procconf(apdsafe_t *apdsafe, const char *sect, int argc, const char **argv){
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
int apdsafe_postconf(apdsafe_t *apdsafe){

  return 0;
}
