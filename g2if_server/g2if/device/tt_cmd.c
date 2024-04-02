/* -------------------------------------------------------------------------
 * tt_conf.h -- Functions to parse and process commands for TT tt
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
#include "tt.h"	              		/* for tt_t and its functions */


/* Command "tt help" */
static int tt_cmd_help(client_t *client, tt_t *tt){

  sendres(client, "Usage: tt <command> [<argument>]\n");
  sendres(client, "  commands and arguments:\n");
  sendres(client, "    zero            : set TT voltage to 0[V]\n");
  sendres(client, "    flat            : set TT voltage to flat with preset values\n");
  sendres(client, "    saveflat        : save current pattern as TT preset flat voltage\n");
  sendres(client, "    makeflat [X]    : create new flat by averaging TT for X sec\n");
  sendres(client, "    help            : show this message\n");

  //sendres(client, "    load [<filename>]     : load TT voltage pattern from a file\n");
  //sendres(client, "    save [<filename>]     : save TT voltage pattern to a file\n");
  //sendres(client, "    loadflat [<filename>] : load TT preset flat pattern\n");
  sendres(client, "    tip X [r]             : set Tip voltage to X in V\n");
  sendres(client, "    tilt X [r]            : set Tilt voltage to X in V\n");

  return 0;
}

/* Command "tt zero" */
static int tt_cmd_zero(client_t *client, tt_t *tt){
  char *cmd = getargv(client, 1);
  char script[TT_COMM_BUFSIZ];

  /* check number of argument */
  if (getargc(client) < 2) {
    sendres_missing_arg(client);
    return -1;
  }

  /* Log command */
  info("> %s: %s", tt->header, cmd);

  /* tt zero */
  sprintf(script,"%s all",tt->zero);
  system(script);
  usleep(100000); // wait 0.1s

  return 0;
}

/* Command "tt flat" */
static int tt_cmd_flat(client_t *client, tt_t *tt){
  char *cmd = getargv(client, 1);
  char script[TT_COMM_BUFSIZ];

  /* check number of argument */
  if (getargc(client) < 2) {
    sendres_missing_arg(client);
    return -1;
  }

  /* Log command */
  info("> %s: %s", tt->header, cmd);

  /* tt flat */
  sprintf(script,"bash %s",tt->flat);
  system(script);
  usleep(100000); // wait 0.1s

  return 0;
}

/* Command "tt saveflat" */
static int tt_cmd_saveflat(client_t *client, tt_t *tt){
  char *cmd = getargv(client, 1);
  char script[TT_COMM_BUFSIZ];

  /* check number of argument */
  if (getargc(client) < 2) {
    sendres_missing_arg(client);
    return -1;
  }

  /* Log command */
  info("> %s: %s", tt->header, cmd);

  /* tt save flat */
  sprintf(script,"python %s",tt->saveflat);
  system(script);
  usleep(100000); // wait 0.1s

  /* tt update flat */
  sprintf(script,"bash %s",tt->flat);
  system(script);
  usleep(100000); // wait 0.1s

  return 0;
}

/* Command "tt makeflat" */
static int tt_cmd_makeflat(client_t *client, tt_t *tt){
  char *cmd = getargv(client, 1);
  char errstr[TT_ERRSTR_MAX];
  int val;

  /* check number of argument */
  if (getargc(client) < 3) {
    sendres_missing_arg(client);
    return -1;
  }

  /* check argument */
  if(getargv_int(client, 2, &val, TT_MIN_MAKEFLAT_SEC, TT_MAX_MAKEFLAT_SEC) < 0){
    return -1;
  }

  /* Log command */
  info("> %s: %s %d", tt->header, cmd, val);

  if(tt_make_flat(tt, val, errstr)<0){
    sendres(client, RES_HEAD_ERR"%s: %s", tt->header, errstr);
  }

  return 0;
}

/* Command "tt tip" pr "tt tilt" */
static int tt_cmd_set(client_t *client, tt_t *tt){
  char *cmd = getargv(client, 1);
  int val;
  char script[TT_COMM_BUFSIZ];

  /* check number of argument */
  if (getargc(client) < 3) {
    sendres_missing_arg(client);
    return -1;
  }

  /* check argument */
  if(getargv_int(client, 2, &val, -10.0, 10.0) < 0){
    return -1;
  }
  val = val*VOLT_TO_DAC; // TODO

  if (getargc(client) == 3) {

    /* Log command */
    info("> %s: %s %d", tt->header, cmd, val);

    sprintf(script,"bash %s %s %d",tt->set,cmd,(int)val); // TODO python
    system(script);
    usleep(100000); // wait 0.1s
  }

  return 0;
}

/*
 * Process tt commands
 */
int tt_proccmd(client_t *client, tt_t *tt){
  char *cmd = getargv(client, 1);

  if (cmd != NULL) {
    strtolower(cmd);
  }

  if (cmd == NULL) { /* help */
    return tt_cmd_help(client, tt);
  }

  switch(cmd[0]) {
  case 'f':
    if (strcmp(cmd, "flat") == 0) { /* TT flat */
      return tt_cmd_flat(client, tt);
    }
    break;
  case 'h':
    if (strcmp(cmd, "help") == 0) { /* help */
      return tt_cmd_help(client, tt);
    }
    break;
  case 'm':
    if (strcmp(cmd, "makeflat") == 0) { /* make flat */
      return tt_cmd_makeflat(client, tt);
    }
    break;
  case 's':
    if (strcmp(cmd, "saveflat") == 0) { /* tt saveflat */
      return tt_cmd_saveflat(client, tt);
    }
    break;
  case 't':
    if (strcmp(cmd, "tip") == 0) { /* tt tip */
      return tt_cmd_set(client, tt);
    }
    if (strcmp(cmd, "tilt") == 0) { /* tt tip */
      return tt_cmd_set(client, tt);
    }
    break;
  case 'z':
    if (strcmp(cmd, "zero") == 0) { /* tt zero */
      return tt_cmd_zero(client, tt);
    }
    break;
  }

  sendres_unknown_cmd(client, cmd);
  return 0;
}
