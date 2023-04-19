/* -------------------------------------------------------------------------
 * shms_conf.h -- Functions to parse and process commands for cacao SHM
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/16   Y. Ono        Initial version (tested with dummy shm)
 *
 * -------------------------------------------------------------------------
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE				/* for using GNU version of strerror_r() */
#endif /* _GNU_SOURCE */

#include <stdio.h>			/* for snprintf() */
#include <string.h>			/* for strcmp(), strlen() */
#include <stdlib.h>			/* for bsearch() */
#include <ctype.h>			/* for tolower() */
#include <errno.h>			/* for errno */
#include <math.h>			/* for log10() */
#include <unistd.h>			/* for alarm() */
#include <signal.h>			/* for signal() */
#include "log.h"			/* for error(), info(), debug() */
#include "comm.h"			/* for comm_*() */
#include "server.h"			/* for sendres(), sendres_*() */
#include "stringx.h"			/* for strtolower() */
#include "shms.h"			/* for shms_t and its functions */

/* Command "loop help" */
static int shms_cmd_help(client_t *client, shms_t *shms){

  sendres(client, "Usage: shms <command>\n");
  sendres(client, "    list               : list all sheard memories\n");
  sendres(client, "    help               : show this message\n");

  return 0;
}

/* Command "loop help" */
static int shms_cmd_list(client_t *client, shms_t *shms){

  int i;
  sendres(client, "Shared Memory List\n");
  sendres(client, " %-20s    %-s\n", "SHM Name", "N_Element");
  for(i=0; i<shms->shm_num; i++){
    sendres(client, "   %-20s    %d\n", shms->shm[i].key, shms->shm[i].image.md[0].nelement); 
  }
  return 0;
}

/*
 * Process shms commands
 */
int shms_proccmd(client_t *client, shms_t *shms){
  char *cmd = getargv(client, 1);
  
  if (cmd != NULL) {
    strtolower(cmd);
  }
  
  if (cmd == NULL) { /* help */
    return shms_cmd_help(client, shms);
  }
  
  switch(cmd[0]) {
  case 'h':
    if (strcmp(cmd, "help") == 0) { /* help */
      return shms_cmd_help(client, shms);
    }
    break;
  case 'l':
    if (strcmp(cmd, "list") == 0) { /* list */
      return shms_cmd_list(client, shms);
    }
    break;
  }
  
  sendres_unknown_cmd(client, cmd);
  return 0;
}
