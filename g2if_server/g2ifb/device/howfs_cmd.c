/* -------------------------------------------------------------------------
 * howfs_cmd.c -- Functions to parse and process user commands 
 *               for HOWFS server handler
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
#include "howfs.h"				/* for howfs_t and its functions */

/*
 * Send error message to client if error exists
 */
int howfs_sendres(client_t *client, howfs_t *howfs, int ret, const char *retstr){
  char buf[RESSTR_MAX + 1];

  if (ret != 0) {
    retstr = strerror_r(errno, buf, sizeof(buf));
    sendres(client, RES_HEAD_ERR"%s: %s\n", howfs->header, retstr);
    return -1;
  }else if(strstr(retstr,"ERR") != NULL || strstr(retstr,"Error:") != NULL){
    sendres(client, RES_HEAD_ERR"%s: %s", howfs->header, retstr);
    return -1;
  }
  return 0;
}


/*
 * Send shutter close command to HOWFS server to control shutter
 */
static int howfs_cmd_close(client_t *client, howfs_t *howfs){
  int ret = 0;
  char errstr[HOWFS_ERRSTR_MAX + 1];
    
  info("%s: close", howfs->header);

  if((ret = howfs_lash_close(howfs, errstr))<0){
    sendres(client, "%s", errstr);
  }

  return ret;
}

/*
 * Get status from HOWFS server 
 */
static int howfs_cmd_st(client_t *client, howfs_t *howfs, const int cashe){
  int ret = 0;
  char errstr[HOWFS_ERRSTR_MAX + 1];
  struct howfs_stat stat;

  /* get status from HOWFS server */
  if(cashe==1)
    stat = howfs->stat;
  else{
    ret = howfs_getstat(howfs, &stat, errstr);
    if(ret == 0) howfs_savestat(howfs, &stat);
    else sendres(client, RES_HEAD_ERR"%s: %s", howfs->header, errstr);
  }

  /* responce to client */
  if(ret == 0){
    if(stat.lash == 1)
      sendres(client, "LA Shutter      : [ OPEN         ]\n");
    else
      sendres(client, "LA Shutter      : [ CLOSE        ]\n");
    sendres(client, "LA FW           : [ %-6s       ]",howfs->stat.lafw);
  }
  return ret;
}


/*
 * Send vm status command to HOWFS server 
 */
static int howfs_cmd_vmst(client_t *client, howfs_t *howfs, const int cashe){
  int ret = 0;
  char errstr[HOWFS_ERRSTR_MAX + 1];
  struct howfs_stat stat;

  /* get status from HOWFS server */
  if(cashe==1)
    stat = howfs->stat;
  else{
    ret = howfs_getstat(howfs, &stat, errstr);
    if(ret == 0) howfs_savestat(howfs, &stat);
    else sendres(client, RES_HEAD_ERR"%s: %s", howfs->header, errstr);
  }

  /* responce to client */
  if(ret == 0){
    if(stat.vm == 1)
      sendres(client, "Drive: ON, Freq: %.1f Hz, Volt: %.2f VPP, Phase: %.1f deg (0x0)", stat.freq, stat.volt, stat.phase);
    else
      sendres(client, "Drive: OFF, Freq: %.1f Hz, Volt: %.2f VPP, Phase: %.1f deg (0x0)", stat.freq, stat.volt, stat.phase);
  }
  return ret;
}

/*
 * Process "help" command
 */
static int howfs_cmd_help(client_t *client, howfs_t *howfs){
    
  char *grp = getargv(client, 0);

  if (strcmp(grp, "howfs") == 0){
    sendres(client, "Usage: howfs <command> [<argument>]\n");
    sendres(client, "  control command and arguments:\n");
    sendres(client, "    close          : close HOWFS lenslet shutter\n");
    sendres(client, "    st             : show status of HOWFS lenslet shutter\n");
    sendres(client, "    stc            : show status of HOWFS lenslet shutter (cashe)\n");
    sendres(client, "    help           : show this message\n");
  }
  else if (strcmp(grp, "vm") == 0){
    sendres(client, "Usage: vm <command> [<argument>]\n");
    sendres(client, "  control command and arguments:\n");
    sendres(client, "    st             : show status of vibrating mirror\n");
    sendres(client, "    stc            : show status of vibrating mirror (cashe)\n");
    sendres(client, "    help           : show this message\n");
  }
  return 0;
}


/*
 * Process howfs commands
 */
int howfs_proccmd(client_t *client, howfs_t *howfs){
  char *grp = getargv(client, 0);
  char *cmd = getargv(client, 1);
  char *arg = getargv(client, 2);
    
  if (cmd != NULL) {
    strtolower(cmd);
  }
    
  if (cmd == NULL) { /* help */
    return howfs_cmd_help(client, howfs);
  }
    
  if (arg == NULL) {
    arg = "";
  }
    
  if(strcmp(grp, "howfs") == 0){
    switch(cmd[0]) {
    case 'c':
      if (strcmp(cmd, "close") == 0) { /* close shutter */
	return howfs_cmd_close(client, howfs);
      }
      break;
    case 'h':
      if (strcmp(cmd, "help") == 0) { /* help */
	return howfs_cmd_help(client, howfs);
      }
      break;
    case 's':
      if (strcmp(cmd, "st") == 0) { /* show status */
	return howfs_cmd_st(client, howfs, 0);
      }
      if (strcmp(cmd, "stc") == 0) { /* show status (cashe)*/
	return howfs_cmd_st(client, howfs, 1);
      }
      break;
    }
  }
  else if (strcmp(grp, "vm") == 0){
    switch(cmd[0]) {
    case 'h':
      if (strcmp(cmd, "help") == 0) { /* help */
	return howfs_cmd_help(client, howfs);
      }
      break;
    case 's':
      if (strcmp(cmd, "st") == 0) { /* show status */
	return howfs_cmd_vmst(client, howfs, 0);
      }
      if (strcmp(cmd, "stc") == 0) { /* show status  (cashe)*/
	return howfs_cmd_vmst(client, howfs, 1);
      }
      break;
    }
  }
  sendres_unknown_cmd(client, cmd);

  return 0;
}
