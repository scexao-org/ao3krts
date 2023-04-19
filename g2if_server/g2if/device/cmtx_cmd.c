/* -------------------------------------------------------------------------
 * cmtx_conf.h -- Functions to parse and process commands for CMTX cmtx
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/06/17   Y. Ono        Initial version
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
#include "cmtx.h"		        /* for cmtx_t and its functions */


/* Command "cmtx help" */
static int cmtx_cmd_help(client_t *client, cmtx_t *cmtx){

  sendres(client, "Usage: cmtx <command> [<argument>]\n");
  sendres(client, "  commands and arguments:\n");
  sendres(client, "    load {ngs|lgs}   : load ngs|lgs command matrix\n");
  sendres(client, "    help             : show this message\n");

  return 0;
}


/* Command "cmtx load" */
static int cmtx_cmd_load(client_t *client, cmtx_t *cmtx){
  char *cmd = getargv(client, 1);
  char *opt;
  char script[CMTX_COMM_BUFSIZ];
  gain_t *gain = cmtx->gain;

  /* check number of argument */
  if (getargc(client) < 2) {
    sendres_missing_arg(client);
    return -1;
  }

  /* check argument */
  opt = getargv(client, 2);

  /* Log command */
  info("> %s: %s %s", cmtx->header, cmd, opt);

  /* set and send command */
  if(strcmp(opt,"ngs") == 0){
    sprintf(script,"python %s",cmtx->ngs);
    system(script);
    sprintf(script, "%s %s 1 0", gain->change, KEY_HTT_GAIN);
    system(script);
    sprintf(script, "%s %s 1 0", gain->change, KEY_HDF_GAIN);
    system(script);
  } else if(strcmp(opt,"lgs") == 0){
    sprintf(script,"python %s",cmtx->lgs);
    system(script);
    /*
    sprintf(script, "%s %s 0 0", gain->change, KEY_HTT_GAIN);
    system(script);
    sprintf(script, "%s %s 0 0", gain->change, KEY_HDF_GAIN);
    system(script);
    */
  } else{
    sendres(client, RES_HEAD_ERR"%s: unkown option \"%s %s\" (should be ngs or lgs)", cmtx->header, cmd, opt);
    return -1;
  }

  sleep(1); // wait 1s

  return 0;
}


/*
 * Process cmtx commands
 */
int cmtx_proccmd(client_t *client, cmtx_t *cmtx){
  char *cmd = getargv(client, 1);
  
  if (cmd != NULL) {
    strtolower(cmd);
  }
  
  if (cmd == NULL) { /* help */
    return cmtx_cmd_help(client, cmtx);
  }
  
  switch(cmd[0]) {
  case 'h':
    if (strcmp(cmd, "help") == 0) { /* help */
      return cmtx_cmd_help(client, cmtx);
    }
    break;
  case 'l':
    if (strcmp(cmd, "load") == 0) { /* load */
      return cmtx_cmd_load(client, cmtx);
    }
    break;
  }

  sendres_unknown_cmd(client, cmd);
  return 0;
}
