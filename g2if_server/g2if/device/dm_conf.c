/* -------------------------------------------------------------------------
 * dm_conf.c -- Functions for reading configuration file
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/06/17   Y. Ono        Initial version
 *    2019/09/20   Y. Ono        Add saveflat
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
#include "dm.h"		        	/* for dm_t */


/*
 * Process a configuration parameter for dmler
 */
int dm_procconf(dm_t *dm, const char *sect, int argc, const char **argv){
  const char *key = argv[0];
  char subsect[32];
  
  if (getsubsect(sect, 1, subsect, sizeof(subsect))) {
    setpar_unknown_sect(sect);
    return 0;
  } else if (strcmp(key, "flat") == 0){  /* keyword for flat script */
    return setpar_strdup(argc, argv, 1, &(dm->flat));
  } else if (strcmp(key, "zero") == 0){  /* keyword for zero script */
    return setpar_strdup(argc, argv, 1, &(dm->zero));
  } else if (strcmp(key, "saveflat") == 0){  /* keyword for save script */
    return setpar_strdup(argc, argv, 1, &(dm->saveflat));
  } else if (strcmp(key, "updateflat") == 0){  /* keyword for save script */
    return setpar_strdup(argc, argv, 1, &(dm->updateflat));
  }
  setpar_unknown_par(key);
  return 0;
}

/*
 * Print all configuration parameters
 */
int dm_postconf(dm_t *dm){
  const char *header = dm->header;

  info("%s: flat script = \"%s\"", header, dm->flat);
  info("%s: zero script = \"%s\"", header, dm->zero);
  info("%s: saveflat script = \"%s\"", header, dm->saveflat);
  info("%s: updateflat script = \"%s\"", header, dm->saveflat);

  return 0;
}
