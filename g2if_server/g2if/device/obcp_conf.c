/* -------------------------------------------------------------------------
 * obcp_conf.c -- Functions to configure parameters for device handler 
 *                of OBCP serer
 * 
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/18   Y. Ono        Initial version
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
#include "obcp.h"			/* for obcp_t */

/*
 * Process a configuration parameter for controller
 */
int obcp_procconf(obcp_t *obcp, const char *sect, int argc,
		  const char **argv)
{
  char subsect[32];
  comm_t *comm = &(obcp->comm);
  const char *key = argv[0];
  char **ip;

  if (getsubsect(sect, 1, subsect, sizeof(subsect))) {
    setpar_unknown_sect(sect);
    return 0;
  } else if (strcmp(key, "addr") == 0) {			/* ip address */
    return setpar_strdup(argc, argv, 1, &(comm->addr));
  } else if (strcmp(key, "hostname") == 0) {		/* hostname */
    ip = (char**)malloc(sizeof(char*));
    ip[0] = (char*)malloc(sizeof(char)*100);
    get_ip(argv[1], ip[0]);
    return setpar_strdup(1, (const char**)ip, 0, &(comm->addr));
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
int obcp_postconf(obcp_t *obcp)
{
  const char *header = obcp->header;
  comm_t *comm = &(obcp->comm);
    
  info("%s: comm.addr = \"%s\"", header, comm->addr);
  info("%s: comm.port = %d", header, comm->port);
  info("%s: comm.timeout = %d", header, comm->timeout);
  info("%s: comm.dump = %d", header, comm->dump);
    
  return 0;
}
