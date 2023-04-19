/* -------------------------------------------------------------------------
 * apdsafe_conf.h -- Functions to parse and process commands for APDSAFE apdsafe
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/06/20   Y. Ono        Initial version
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
#include "apdsafe.h"			/* for apdsafe_t and its functions */


/* Command "apdsafe help" */
static int apdsafe_cmd_help(client_t *client, apdsafe_t *apdsafe){

  sendres(client, "Usage: apdsafe <command> [<argument>]\n");
  sendres(client, "  commands and arguments:\n");
  sendres(client, "    poll {on|off}        : turn on/off apdsafe program\n");
  sendres(client, "    emergency {on|off}   : turn on/off emergency mode\n");
  sendres(client, "    limit [X]            : set APD MAX LIMIT\n");
  sendres(client, "    frame [X]            : set APD FRAME LIMIT\n");
  sendres(client, "    st                   : show status\n");
  sendres(client, "    help                 : show this message\n");  
  return 0;
}

/* Command to on/off emergency function */
static int apdsafe_cmd_emergency(client_t *client, apdsafe_t *apdsafe){
  char *cmd = getargv(client, 1);
  char *arg;

  /* check number of argument */
  if (getargc(client) < 3) {
    sendres_missing_arg(client);
    return -1;
  }

  arg = getargv(client, 2);

  if(strcmp(arg,"on")!= 0 && strcmp(arg,"off")!= 0){
    sendres_invalid_arg(client, cmd);
    return -1;
  }

  info("> %s: %s %s", apdsafe->header, cmd, arg);

  pthread_rwlock_wrlock(&(apdsafe->cache_lock));
  if(strcmp(arg,"on") == 0) apdsafe->emergency = 1;
  else if(strcmp(arg,"off") == 0) apdsafe->emergency = 0;
  pthread_rwlock_unlock(&(apdsafe->cache_lock));

  return 0;
}

/* Command to change limit */
static int apdsafe_cmd_limit(client_t *client, apdsafe_t *apdsafe){
  char *cmd = getargv(client, 1);
  float val;

  /* check number of argument */
  if (getargc(client) < 3) {
    sendres_missing_arg(client);
    return -1;
  }

  /* check argument */
  if(getargv_flt(client, 2, &val, APDSAFE_MIN_LIMIT, APDSAFE_MAX_LIMIT) < 0){
    return -1;
  }

  info("> %s: %s %.4f", apdsafe->header, cmd, val);

  pthread_rwlock_wrlock(&(apdsafe->cache_lock));
  apdsafe->max_limit = val;
  pthread_rwlock_unlock(&(apdsafe->cache_lock));

  return 0;
}


/* Command to change frame limit */
static int apdsafe_cmd_frame(client_t *client, apdsafe_t *apdsafe){
  char *cmd = getargv(client, 1);
  int val;

  /* check number of argument */
  if (getargc(client) < 3) {
    sendres_missing_arg(client);
    return -1;
  }

  /* check argument */
  if(getargv_int(client, 2, &val, APDSAFE_MIN_NFRAME, APDSAFE_MAX_NFRAME) < 0){
    return -1;
  }

  info("> %s: %s %d", apdsafe->header, cmd, val);

  pthread_rwlock_wrlock(&(apdsafe->cache_lock));
  apdsafe->nframe = val;
  pthread_rwlock_unlock(&(apdsafe->cache_lock));

  return 0;
}


/* Command "apdsafe st" */
static int apdsafe_cmd_st(client_t *client, apdsafe_t *apdsafe){
  int nframe;
  float max_limit;
  int emergency;

  /* copy to local */
  pthread_rwlock_rdlock(&(apdsafe->cache_lock));
  nframe = apdsafe->nframe;
  max_limit = apdsafe->max_limit;
  emergency = apdsafe->emergency;
  pthread_rwlock_unlock(&(apdsafe->cache_lock));

  /* check if the program is running */
  if (poll_isrunning(&(apdsafe->poll)) == 1) sendres(client, "APDSAFE = Running,   ");
  else sendres(client, "APDSAFE = Stop,   ");

  /* check safety function */
  if(emergency == 1) sendres(client, "Emergency Mode = ON,   ");
  else sendres(client, "Emergency Mode = OFF,   ");

  /* check limit */
  sendres(client, "MAX_LIMIT = %.4f,   ", max_limit);

  /* check frame */
  sendres(client, "FRAME_LIMIT = %d", nframe);

  return 0;
}

/*
 * Process apdsafe commands
 */
int apdsafe_proccmd(client_t *client, apdsafe_t *apdsafe){
  char *cmd = getargv(client, 1);
  
  if (cmd != NULL) {
    strtolower(cmd);
  }
  
  if (cmd == NULL) { /* help */
    return apdsafe_cmd_help(client, apdsafe);
  }
  
  switch(cmd[0]) {
  case 'e':
    if (strcmp(cmd, "emergency") == 0) { /* set frame */
      return apdsafe_cmd_emergency(client, apdsafe);
    }
    break;
  case 'f':
    if (strcmp(cmd, "frame") == 0) { /* set frame */
      return apdsafe_cmd_frame(client, apdsafe);
    }
    break;
  case 'h':
    if (strcmp(cmd, "help") == 0) { /* help */
      return apdsafe_cmd_help(client, apdsafe);
    }
    break;
  case 'l':
    if (strcmp(cmd, "limit") == 0) { /* limit */
      return apdsafe_cmd_limit(client, apdsafe);
    }
    break;
  case 'p':
    if (strcmp(cmd, "poll") == 0) { /* on|off */
      return poll_cmd_poll(client, &(apdsafe->poll));
    }
    break;
  case 's':
    if (strcmp(cmd, "st") == 0) { /* st */
      return apdsafe_cmd_st(client, apdsafe);
    }
    break;
  }

  sendres_unknown_cmd(client, cmd);
  return 0;
}
