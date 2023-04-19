/* -------------------------------------------------------------------------
 * entshut_cmd.c -- Functions to parse and process user commands 
 *               for ENTSHUT server handler
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/05/13   Y. Ono        Initial version
 *
 * -------------------------------------------------------------------------
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE				/* for using GNU version of strerror_r() */
#endif /* _GNU_SOURCE */

#include <stdio.h>				/* for snprintf() */
#include <string.h>				/* for strcmp(), strlen() */
#include <ctype.h>				/* for tolower() */
#include <errno.h>				/* for errno */
#include <math.h>				/* for log10() */
#include <unistd.h>				/* for alarm() */
#include <signal.h>				/* for signal() */
#include "log.h"				/* for error(), info(), debug() */
#include "comm.h"				/* for comm_*() */
#include "server.h"				/* for sendres(), sendres_*() */
#include "stringx.h"			/* for strtolower() */
#include "entshut.h"				/* for entshut_t and its functions */

/*
 * Send error message to client if error exists
 */
int entshut_sendres(client_t *client, entshut_t *entshut, int ret, const char *retstr){
  char buf[RESSTR_MAX + 1];

  if (ret != 0) {
    retstr = strerror_r(errno, buf, sizeof(buf));
    sendres(client, RES_HEAD_ERR"%s: %s\n", entshut->header, retstr);
    return -1;
  }else if(strstr(retstr,"ERR") != NULL || strstr(retstr,"Error:") != NULL){
    sendres(client, RES_HEAD_ERR"%s: %s", entshut->header, retstr);
    return -1;
  }
  return 0;
}


/*
 * Send shutter close command to ENTSHUT server to control shutter
 */
static int entshut_cmd_close(client_t *client, entshut_t *entshut){
  int ret = 1;
  char errstr[ENTSHUT_ERRSTR_MAX + 1];
  char retstr[RESSTR_MAX + 1];
  comm_t *comm = &(entshut->comm);
    
  info("%s: close", entshut->header);
    
  errstr[0]='\0';

  if((ret = entshut_connect(entshut))<0){
    sendres(client, "cannot connect to entshut server (%s:%d)", comm->addr, comm->port);
    return -1;
  }

  /* Exclude other threads until end of communication */
  comm_lock(comm);
  pthread_cleanup_push((void *)comm_unlock, comm);

  /* Check connection */
  if (comm_chkconn(comm) >= 0){
    ret = comm_sendrecv(comm, ENTSHUT_CMD_ENTSHUT_CLOSE, retstr, sizeof(retstr));
    sendres(client, "%s", retstr);
  }
  pthread_cleanup_pop(1);

  if((ret = entshut_disconnect(entshut))<0){
    sendres(client, "cannot disconnect from entshut server (%s:%d)", comm->addr, comm->port);
    return -1;
  }
  return entshut_sendres(client, entshut, ret, errstr);
}


/*
 * Send status command to ENTSHUT server 
 */
static int entshut_cmd_st(client_t *client, entshut_t *entshut){
  int ret = 1;
  char errstr[ENTSHUT_ERRSTR_MAX + 1];
  char retstr[RESSTR_MAX + 1];
  comm_t *comm = &(entshut->comm);
    
  info("%s: close", entshut->header);
    
  errstr[0]='\0';

  if((ret = entshut_connect(entshut))<0){
    sendres(client, "cannot connect to entshut server (%s:%d)", comm->addr, comm->port);
    return -1;
  }

  /* Exclude other threads until end of communication */
  comm_lock(comm);
  pthread_cleanup_push((void *)comm_unlock, comm);

  /* Check connection */
  if (comm_chkconn(comm) >= 0){
    ret = comm_sendrecv(comm, ENTSHUT_CMD_ENTSHUT_ST, retstr, sizeof(retstr));
    sendres(client, "%s", retstr);
  }
  pthread_cleanup_pop(1);

  if((ret = entshut_disconnect(entshut))<0){
    sendres(client, "cannot disconnect from entshut server (%s:%d)", comm->addr, comm->port);
    return -1;
  }
  return entshut_sendres(client, entshut, ret, errstr);
}


/*
 * Process "help" command
 */
static int entshut_cmd_help(client_t *client, entshut_t *entshut){
    
  char *grp = getargv(client, 0);

  if (strcmp(grp, "entshut") == 0){
    sendres(client, "Usage: entshut <command> [<argument>]\n");
    sendres(client, "  control command and arguments:\n");
    sendres(client, "    close          : close ENTSHUT lenslet shutter\n");
    sendres(client, "    st             : show status of ENTSHUT lenslet shutter\n");
    sendres(client, "    help           : show this message\n");
  }
  return 0;
}


/*
 * Process entshut commands
 */
int entshut_proccmd(client_t *client, entshut_t *entshut){
  char *cmd = getargv(client, 1);
  char *arg = getargv(client, 2);
    
  if (cmd != NULL) {
    strtolower(cmd);
  }
    
  if (cmd == NULL) { /* help */
    return entshut_cmd_help(client, entshut);
  }
    
  if (arg == NULL) {
    arg = "";
  }
    
  switch(cmd[0]) {
  case 'c':
    if (strcmp(cmd, "close") == 0) { /* close shutter */
      return entshut_cmd_close(client, entshut);
    }
    break;
  case 'h':
    if (strcmp(cmd, "help") == 0) { /* help */
      return entshut_cmd_help(client, entshut);
    }
    break;
  case 's':
    if (strcmp(cmd, "st") == 0) { /* show status */
      return entshut_cmd_st(client, entshut);
    }
    break;
  }
  sendres_unknown_cmd(client, cmd);
    
  return 0;
}
