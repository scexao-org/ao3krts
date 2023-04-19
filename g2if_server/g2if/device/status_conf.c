/* -------------------------------------------------------------------------
 * status_conf.c -- Functions for reading configuration file
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/01/19   Y. Ono        Initial version
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
#include "status.h"			/* for status_t */


/*
 * Process a configuration parameter for statusler
 */
int status_procconf(status_t *status, const char *sect, int argc, const char **argv){
  const char *key = argv[0];
  char subsect[32];
  
  if (getsubsect(sect, 1, subsect, sizeof(subsect))) {
    setpar_unknown_sect(sect);
    return 0;
  } else if (strcmp(key, "hapdconf") == 0){  /* keyword for howfs apd map */
    return setpar_strdup(argc, argv, 1, &(status->hapdconf));
  } else if (strcmp(key, "lapdconf") == 0){  /* keyword for howfs apd map */
    return setpar_strdup(argc, argv, 1, &(status->lapdconf));
  }

  setpar_unknown_par(key);
  return 0;
}

/*
 * Print all configuration parameters
 */
int status_postconf(status_t *status){
  const char *header = status->header;

  info("%s: HOWFS apd config = \"%s\"", header, status->hapdconf);
  info("%s: LOWFS apd config = \"%s\"", header, status->lapdconf);

  return 0;
}
