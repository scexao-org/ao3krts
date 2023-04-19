/* -------------------------------------------------------------------------
 * tt_conf.c -- Functions for reading configuration file
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/06/17   Y. Ono        Initial version
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
#include "tt.h"		        	/* for tt_t */


/*
 * Process a configuration parameter for ttler
 */
int tt_procconf(tt_t *tt, const char *sect, int argc, const char **argv){
  const char *key = argv[0];
  char subsect[32];
  
  if (getsubsect(sect, 1, subsect, sizeof(subsect))) {
    setpar_unknown_sect(sect);
    return 0;
  } else if (strcmp(key, "flat") == 0){  /* keyword for flat script */
    return setpar_strdup(argc, argv, 1, &(tt->flat));
  } else if (strcmp(key, "zero") == 0){  /* keyword for zero script */
    return setpar_strdup(argc, argv, 1, &(tt->zero));
  } else if (strcmp(key, "saveflat") == 0){  /* keyword for zero script */
    return setpar_strdup(argc, argv, 1, &(tt->saveflat));
  } else if (strcmp(key, "updateflat") == 0){  /* keyword for save script */
    return setpar_strdup(argc, argv, 1, &(tt->updateflat));
  } else if (strcmp(key, "set") == 0){  /* keyword for set script */
    return setpar_strdup(argc, argv, 1, &(tt->set));
  }
  setpar_unknown_par(key);
  return 0;
}

/*
 * Print all configuration parameters
 */
int tt_postconf(tt_t *tt){
  const char *header = tt->header;

  info("%s: flat script = \"%s\"", header, tt->flat);
  info("%s: zero script = \"%s\"", header, tt->zero);
  info("%s: saveflat script = \"%s\"", header, tt->saveflat);
  info("%s: updateflat script = \"%s\"", header, tt->updateflat);
  info("%s: set script = \"%s\"", header, tt->set);

  return 0;
}
