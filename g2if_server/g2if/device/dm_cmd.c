/* -------------------------------------------------------------------------
 * dm_conf.h -- Functions to parse and process commands for DM dm
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
#include "dm.h"		        	/* for dm_t and its functions */


/* Command "dm help" */
static int dm_cmd_help(client_t *client, dm_t *dm){

  sendres(client, "Usage: dm <command> [<argument>]\n");
  sendres(client, "  commands and arguments:\n");
  sendres(client, "    zero            : set DM voltage to 0[V]\n");
  sendres(client, "    flat            : set DM voltage to flat with preset values (\n");
  sendres(client, "    saveflat        : save current pattern as DM preset flat voltage\n");
  sendres(client, "    makeflat [X]    : create new flat by averaging DM voltage for X sec\n");
  sendres(client, "    help            : show this message\n");

  return 0;
}


/* Command "dm zero" */
static int dm_cmd_zero(client_t *client, dm_t *dm){
  char *cmd = getargv(client, 1);
  char script[DM_COMM_BUFSIZ];

  /* Log command */
  info("> %s: %s", dm->header, cmd);

  /* dm zero */
  system(dm->zero);

  return 0;
}

/* Command "dm flat" */
static int dm_cmd_flat(client_t *client, dm_t *dm){
  char *cmd = getargv(client, 1);
  char script[DM_COMM_BUFSIZ];

  /* Log command */
  info("> %s: %s", dm->header, cmd);

  /* dm flat */

  system(dm->flat);

  return 0;
}

/* Command "dm saveflat" */
static int dm_cmd_saveflat(client_t *client, dm_t *dm){
  char *cmd = getargv(client, 1);
  char script[DM_COMM_BUFSIZ];

  /* Log command */
  info("> %s: %s", dm->header, cmd);

  /* dm save flat */
  system(dm->saveflat);
  usleep(100000); // wait 0.1s

  /* dm load flat */
  system(dm->flat);
  usleep(100000); // wait 0.1s

  return 0;
}


/* Command "dm makeflat" */
static int dm_cmd_makeflat(client_t *client, dm_t *dm){
  char *cmd = getargv(client, 1);
  char errstr[DM_ERRSTR_MAX];
  int val;

  /* check number of argument */
  if (getargc(client) < 3) {
    sendres_missing_arg(client);
    return -1;
  }

  /* check argument */
  if(getargv_int(client, 2, &val, DM_MIN_MAKEFLAT_SEC, DM_MAX_MAKEFLAT_SEC) < 0){
    return -1;
  }

  /* Log command */
  info("> %s: %s %d", dm->header, cmd, val);

  if(dm_make_flat(dm, val, errstr)<0){
    sendres(client, RES_HEAD_ERR"%s: %s", dm->header, errstr);
  }

  return 0;
}


/*
 * Process dm commands
 */
int dm_proccmd(client_t *client, dm_t *dm){
  char *cmd = getargv(client, 1);

  if (cmd != NULL) {
    strtolower(cmd);
  }

  if (cmd == NULL) { /* help */
    return dm_cmd_help(client, dm);
  }

  switch(cmd[0]) {
  case 'f':
    if (strcmp(cmd, "flat") == 0) { /* DM flat */
      return dm_cmd_flat(client, dm);
    }
    break;
  case 'h':
    if (strcmp(cmd, "help") == 0) { /* help */
      return dm_cmd_help(client, dm);
    }
    break;
  case 'm':
    if (strcmp(cmd, "makeflat") == 0) { /* make flat */
      return dm_cmd_makeflat(client, dm);
    }
    break;
  case 's':
    if (strcmp(cmd, "saveflat") == 0) { /* dm save */
      return dm_cmd_saveflat(client, dm);
    }
    break;
  case 'z':
    if (strcmp(cmd, "zero") == 0) { /* dm zero */
      return dm_cmd_zero(client, dm);
    }
    break;
  }

  sendres_unknown_cmd(client, cmd);
  return 0;
}
