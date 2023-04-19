/* -------------------------------------------------------------------------
 * entshut_conf.c -- Functions to configure parameters for device handler 
 *                of ENTSHUT serer
 * 
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/05/13   Y. Ono        Initial version
 *
 * -------------------------------------------------------------------------
 */

#include <stdio.h>			/* for snprintf() */
#include <string.h>			/* for strcmp(), strncpy() */
#include <limits.h>			/* for USHRT_MAX */
#include <errno.h>			/* for errno */
#include "log.h"			/* for error(), info(), debug() */
#include "conf.h"			/* for setpar_int() and etc */
#include "tool.h"			/* for setpar_int() and etc */
#include "stringx.h"			/* for strjoin() */
#include "entshut.h"			/* for entshut_t */

/*
 * Process a configuration parameter for controller
 */
int entshut_procconf(entshut_t *entshut, const char *sect, int argc,
		  const char **argv)
{
  char subsect[32];
  comm_t *comm = &(entshut->comm);
  const char *key = argv[0];

  if (getsubsect(sect, 1, subsect, sizeof(subsect))) {
    setpar_unknown_sect(sect);
    return 0;
  } else if (strcmp(key, "addr") == 0) {			/* ip address */
    return setpar_strdup(argc, argv, 1, &(comm->addr));
  } else if (strcmp(key, "port") == 0) {			/* port number */
    return setpar_int(argc, argv, 1, &(comm->port), 0, USHRT_MAX);
  } else if (strcmp(key, "timeout") == 0) {		/* timeout period */
    return setpar_int(argc, argv, 1, &(comm->timeout), 0, USHRT_MAX);
  } else if (strcmp(key, "dump") == 0) {			/* dump flag */
    return setpar_int(argc, argv, 1, &(comm->dump), 0, 1);
  }
    
  setpar_unknown_par(key);
  return 0;
}

/*
 * Print all configuration parameters
 */
int entshut_postconf(entshut_t *entshut)
{
  const char *header = entshut->header;
  comm_t *comm = &(entshut->comm);
    
  info("%s: comm.addr = \"%s\"", header, comm->addr);
  info("%s: comm.port = %d", header, comm->port);
  info("%s: comm.timeout = %d", header, comm->timeout);
  info("%s: comm.dump = %d", header, comm->dump);
    
  return 0;
}
