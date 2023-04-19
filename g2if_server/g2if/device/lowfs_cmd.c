/* -------------------------------------------------------------------------
 * lowfs_cmd.c -- Functions to parse and process user commands 
 *               for LOWFS server handler
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/05/13   Y. Ono        Initial version
 *    2019/09/20   Y. Ono        Add cashe
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
#include "lowfs.h"				/* for lowfs_t and its functions */

/*
 * Send error message to client if error exists
 */
int lowfs_sendres(client_t *client, lowfs_t *lowfs, int ret, const char *retstr){
  char buf[RESSTR_MAX + 1];

  if (ret != 0) {
    retstr = strerror_r(errno, buf, sizeof(buf));
    sendres(client, RES_HEAD_ERR"%s: %s\n", lowfs->header, retstr);
    return -1;
  }else if(strstr(retstr,"ERR") != NULL || strstr(retstr,"Error:") != NULL){
    sendres(client, RES_HEAD_ERR"%s: %s", lowfs->header, retstr);
    return -1;
  }
  return 0;
}


/*
 * Send shutter close command to LOWFS server to control shutter
 */
static int lowfs_cmd_close(client_t *client, lowfs_t *lowfs){
  int ret = 0;
  char errstr[LOWFS_ERRSTR_MAX + 1];
    
  info("%s: close", lowfs->header);

  if((ret = lowfs_lash_close(lowfs, errstr))<0){
    sendres(client, "%s", errstr);
  }

  return ret;
}


/*
 * Get status from LOWFS server 
 */
static int lowfs_cmd_st(client_t *client, lowfs_t *lowfs, const int cashe){
  int ret = 0;
  char errstr[LOWFS_ERRSTR_MAX + 1];
  struct lowfs_stat stat;

  /* get status from LOWFS server */
  if(cashe==1)
    stat = lowfs->stat;
  else{
    ret = lowfs_getstat(lowfs, &stat, errstr);
    if(ret == 0) lowfs_savestat(lowfs, &stat);
    else sendres(client, RES_HEAD_ERR"%s: %s",lowfs->header, errstr);
  }

  /* responce to client */
  if(ret == 0){
    if(stat.lash == 1)
      sendres(client, "LA Shutter      : [ OPEN         ]\n");
    else
      sendres(client, "LA Shutter      : [ CLOSE        ]\n");
    sendres(client, "LA FW           : [ %-6s       ]",lowfs->stat.lafw);
  }

  return ret;
}


/*
 * Process "help" command
 */
static int lowfs_cmd_help(client_t *client, lowfs_t *lowfs){
    
  char *grp = getargv(client, 0);

  if (strcmp(grp, "lowfs") == 0){
    sendres(client, "Usage: lowfs <command> [<argument>]\n");
    sendres(client, "  control command and arguments:\n");
    sendres(client, "    close          : close LOWFS lenslet shutter\n");
    sendres(client, "    st             : show status of LOWFS lenslet shutter\n");
    sendres(client, "    stc            : show status of HOWFS lenslet shutter (cashe)\n");
    sendres(client, "    help           : show this message\n");
  }
  return 0;
}


/*
 * Process lowfs commands
 */
int lowfs_proccmd(client_t *client, lowfs_t *lowfs){
  char *cmd = getargv(client, 1);
  char *arg = getargv(client, 2);
    
  if (cmd != NULL) {
    strtolower(cmd);
  }
    
  if (cmd == NULL) { /* help */
    return lowfs_cmd_help(client, lowfs);
  }
    
  if (arg == NULL) {
    arg = "";
  }
    
  switch(cmd[0]) {
  case 'c':
    if (strcmp(cmd, "close") == 0) { /* close shutter */
      return lowfs_cmd_close(client, lowfs);
    }
    break;
  case 'h':
    if (strcmp(cmd, "help") == 0) { /* help */
      return lowfs_cmd_help(client, lowfs);
    }
    break;
  case 's':
    if (strcmp(cmd, "st") == 0) { /* show status */
      return lowfs_cmd_st(client, lowfs, 0);
    }
    if (strcmp(cmd, "stc") == 0) { /* show status (cashe)*/
	return lowfs_cmd_st(client, lowfs, 1);
    }
    break;
  }
  sendres_unknown_cmd(client, cmd);
    
  return 0;
}
