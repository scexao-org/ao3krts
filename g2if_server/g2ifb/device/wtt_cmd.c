/* -------------------------------------------------------------------------
 * wtt_conf.h -- Functions to parse and process commands for WTT wtt
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/06/17   Y. Ono        Initial version (tested with dummy shm)
 *    2019/09/20   Y. Ono        Add saveflat
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
#include "wtt.h"	              		/* for wtt_t and its functions */


/* Command "wtt help" */
static int wtt_cmd_help(client_t *client, wtt_t *wtt){

  sendres(client, "Usage: wtt <command> [<argument>]\n");
  sendres(client, "  commands and arguments:\n");
  sendres(client, "    zero           : set WTT voltage to 0[V]\n");
  sendres(client, "    flat           : set WTT voltage to flat with preset values\n");
  sendres(client, "    saveflat       : save current pattern as WTT preset flat voltage\n");
  sendres(client, "    help           : show this message\n");

  //sendres(client, "    load [<filename>]     : load WTT voltage pawttern from a file\n");
  //sendres(client, "    save [<filename>]     : save WTT voltage pawttern to a file\n");
  //sendres(client, "    loadflat [<filename>] : load WTT preset flat pawttern\n");
  sendres(client, "    tip X [r]             : set Tip voltage to X in V\n");
  sendres(client, "    tilt X [r]            : set Tilt voltage to X in V\n");

  return 0;
}

/* Command "wtt zero" */
static int wtt_cmd_zero(client_t *client, wtt_t *wtt){
  char *cmd = getargv(client, 1);
  char script[WTT_COMM_BUFSIZ];

  /* check number of argument */
  if (getargc(client) < 2) {
    sendres_missing_arg(client);
    return -1;
  }

  /* Log command */
  info("> %s: %s", wtt->header, cmd);

  /* wtt zero */
  sprintf(script,"bash %s",wtt->zero);
  system(script);
  usleep(100000); // wait 0.1s

  return 0;
}

/* Command "wtt flat" */
static int wtt_cmd_flat(client_t *client, wtt_t *wtt){
  char *cmd = getargv(client, 1);
  char script[WTT_COMM_BUFSIZ];

  /* check number of argument */
  if (getargc(client) < 2) {
    sendres_missing_arg(client);
    return -1;
  }

  /* Log command */
  info("> %s: %s", wtt->header, cmd);

  /* wtt flat */
  sprintf(script,"bash %s",wtt->flat);
  system(script);
  usleep(100000); // wait 0.1s

  return 0;
}

/* Command "wtt saveflat" */
static int wtt_cmd_saveflat(client_t *client, wtt_t *wtt){
  char *cmd = getargv(client, 1);
  char script[WTT_COMM_BUFSIZ];

  /* check number of argument */
  if (getargc(client) < 2) {
    sendres_missing_arg(client);
    return -1;
  }

  /* Log command */
  info("> %s: %s", wtt->header, cmd);

  /* wtt save flat */
  sprintf(script,"python %s",wtt->saveflat);
  system(script);
  usleep(100000); // wait 0.1s

  /* wtt update flat */
  sprintf(script,"bash %s",wtt->flat);
  system(script);
  usleep(100000); // wait 0.1s

  return 0;
}

/* Command "wtt tip" pr "wtt tilt" */
static int wtt_cmd_set(client_t *client, wtt_t *wtt){
  char *cmd = getargv(client, 1);
  int val;
  char script[WTT_COMM_BUFSIZ];

  /* check number of argument */
  if (getargc(client) < 3) {
    sendres_missing_arg(client);
    return -1;
  }

  /* check argument */
  if(getargv_int(client, 2, &val, 0.0, 10.0) < 0){
    return -1;
  }
  val = val*VOLT_TO_DAC;

  if (getargc(client) == 3) {

    /* Log command */
    info("> %s: %s %d", wtt->header, cmd, val);
    
    sprintf(script,"bash %s %s %d",wtt->set,cmd,(int)val);
    system(script);
    usleep(100000); // wait 0.1s
  }

  return 0;
}

/*
 * Process wtt commands
 */
int wtt_proccmd(client_t *client, wtt_t *wtt){
  char *cmd = getargv(client, 1);
  
  if (cmd != NULL) {
    strtolower(cmd);
  }
  
  if (cmd == NULL) { /* help */
    return wtt_cmd_help(client, wtt);
  }
  
  switch(cmd[0]) {
  case 'f':
    if (strcmp(cmd, "flat") == 0) { /* WTT flat */
      return wtt_cmd_flat(client, wtt);
    }
    break;
  case 'h':
    if (strcmp(cmd, "help") == 0) { /* help */
      return wtt_cmd_help(client, wtt);
    }
    break;
  case 's':
    if (strcmp(cmd, "saveflat") == 0) { /* wtt saveflat */
      return wtt_cmd_saveflat(client, wtt);
    }
    break;
 case 't':
    if (strcmp(cmd, "tip") == 0) { /* tt tip */
      return wtt_cmd_set(client, wtt);
    }
    if (strcmp(cmd, "tilt") == 0) { /* tt tip */
      return wtt_cmd_set(client, wtt);
    }
    break;
  case 'z':
    if (strcmp(cmd, "zero") == 0) { /* wtt zero */
      return wtt_cmd_zero(client, wtt);
    }
    break;
  }

  sendres_unknown_cmd(client, cmd);
  return 0;
}
