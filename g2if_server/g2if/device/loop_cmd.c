/* -------------------------------------------------------------------------
 * loop_conf.h -- Functions to parse and process commands for LOOP loop
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>
 *    2019/04/18   Y. Ono        Initial version (tested with dummy shm)
 *    2019/10/01   Y. Ono        Add fifo control for loop on/off status
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
#include "log.h"			/* for error(), info(), debug() */
#include "comm.h"			/* for comm_*() */
#include "server.h"			/* for sendres(), sendres_*() */
#include "stringx.h"			/* for strtolower() */
#include "loop.h"			/* for loop_t and its functions */
#include "tool.h"			/* for timer */
#include "gain.h"			/* for timer */


/* Command "loop help" */
static int loop_cmd_help(client_t *client, loop_t *loop){

  sendres(client, "Usage: loop <command> [<argument>]\n");
  sendres(client, "  commands and arguments:\n");
  sendres(client, "    on/close         : start closed loop\n");
  sendres(client, "    off/open         : stop closed loop\n");
  sendres(client, "    st               : show loop status\n");
  sendres(client, "    stc              : show loop status (cashe)\n");
  sendres(client, "    help             : show this message\n");

  return 0;
}

/* Command "loop st" */
static int loop_cmd_st(client_t *client, loop_t *loop, const int cashe){
  struct loop_stat stat;

  /* get status from shared memories */
  if(cashe == 1)
    stat = loop->stat;
  else{
    loop_getstat(loop, &stat);
    loop_savestat(loop, &stat);
  }

  /* print */
  if(loop->stat.onoff == 1)
    sendres(client, "LOOP : State = ON");
  else if(loop->stat.onoff == 0)
    sendres(client, "LOOP : State = OFF");
  else
    sendres(client, "LOOP : State = ERROR");

  return 0;
}

/* Command "loop on" */
static int loop_cmd_on(client_t *client, loop_t *loop){
  struct loop_stat stat;
  struct timespec ts1, ts2;
  int stat_timeout = 0;

  pthread_mutex_lock(&(loop->lock));

  /* Log command */
  info("> %s: on", loop->header);
  system("echo \""FIFO_SET_COMMAND" "LOOP_FIFO_FLUSH" ON\" >> "FIFO_FPSCTRL_NAME);
  system("echo \""FIFO_SET_COMMAND" "LOOPTT_FIFO_FLUSH" ON\" >> "FIFO_FPSCTRL_NAME);
  sleep(0.1);
  system("echo \""FIFO_SET_COMMAND" "LOOP_FIFO_ONOFF" ON\" >> "FIFO_FPSCTRL_NAME);
  system("echo \""FIFO_SET_COMMAND" "LOOPTT_FIFO_ONOFF" ON\" >> "FIFO_FPSCTRL_NAME);

  /* get current time */
  clock_gettime(CLOCK_REALTIME, &ts1);
  ts1.tv_sec += LOOP_TIMEOUT;

  while(1){
    loop_getstat(loop, &stat);

    if(stat.onoff == 1){
      break;
    }

    /* check timeout */
    clock_gettime(CLOCK_REALTIME, &ts2);
    if(cmp_timespec(&ts1, &ts2) <= 0){
      stat_timeout = 1;
      break;
    }
  }

  pthread_mutex_unlock(&(loop->lock));

  /* timeout error message */
  if(stat_timeout != 0){
    sendres(client, RES_HEAD_ERR"%s: Failed to close loop due to timeout.", loop->header);
    return -1;
  }


  return 0;
}

/* Command "loop off" */
static int loop_cmd_off(client_t *client, loop_t *loop){
  struct loop_stat stat;
  struct timespec ts1, ts2;
  int stat_timeout = 0;

  pthread_mutex_lock(&(loop->lock));

  /* Log command */
  info("> %s: off", loop->header);
  system("echo \""FIFO_SET_COMMAND" "LOOP_FIFO_ONOFF" OFF\" >> "FIFO_FPSCTRL_NAME);
  system("echo \""FIFO_SET_COMMAND" "LOOPTT_FIFO_ONOFF" OFF\" >> "FIFO_FPSCTRL_NAME);
  sleep(0.1);
  system("echo \""FIFO_SET_COMMAND" "LOOP_FIFO_FLUSH" ON\" >> "FIFO_FPSCTRL_NAME);
  system("echo \""FIFO_SET_COMMAND" "LOOPTT_FIFO_FLUSH" ON\" >> "FIFO_FPSCTRL_NAME);

  /* get current time */
  clock_gettime(CLOCK_REALTIME, &ts1);
  ts1.tv_sec += LOOP_TIMEOUT;

  while(1){
    loop_getstat(loop, &stat);

    if(stat.onoff == 0){
      break;
    }

    /* check timeout */
    clock_gettime(CLOCK_REALTIME, &ts2);
    if(cmp_timespec(&ts1, &ts2) <= 0){
      stat_timeout = 1;
      break;
    }
  }

  pthread_mutex_unlock(&(loop->lock));

  /* timeout error message */
  if(stat_timeout != 0){
    sendres(client, RES_HEAD_ERR"%s: Failed to open loop due to timeout.", loop->header);
    return -1;
  }

  return 0;
}

/*
 * Process loop commands
 */
int loop_proccmd(client_t *client, loop_t *loop){
  char *cmd = getargv(client, 1);

  if (cmd != NULL) {
    strtolower(cmd);
  }

  if (cmd == NULL) { /* help */
    return loop_cmd_help(client, loop);
  }

  switch(cmd[0]) {
  case 'c':
    if (strcmp(cmd, "close") == 0) { /* loop on */
      return loop_cmd_on(client, loop);
    }
    break;
  case 'h':
    if (strcmp(cmd, "help") == 0) { /* help */
      return loop_cmd_help(client, loop);
    }
    break;
  case 'o':
    if (strcmp(cmd, "on") == 0) { /* loop on */
      return loop_cmd_on(client, loop);
    }
    if (strcmp(cmd, "off") == 0) { /* loop off */
      return loop_cmd_off(client, loop);
    }
    if (strcmp(cmd, "open") == 0) { /* loop off */
      return loop_cmd_off(client, loop);
    }
    break;
  case 's':
    if (strcmp(cmd, "st") == 0) { /* status */
      return loop_cmd_st(client, loop, 0);
    }
    if (strcmp(cmd, "stc") == 0) { /* status (cashe)*/
      return loop_cmd_st(client, loop, 1);
    }
    break;
  }

  sendres_unknown_cmd(client, cmd);
  return 0;
}
