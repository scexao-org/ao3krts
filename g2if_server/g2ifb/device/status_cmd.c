/* -------------------------------------------------------------------------
 * status_conf.h -- Functions to parse and process commands for STATUS status
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/18   Y. Ono        Initial version (tested with dummy shm)
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
#include "status.h"			/* for status_t and its functions */


/*
 * Process cntmonst communication "help" command
 */
static int status_cmd_help(client_t *client, status_t *status){
    sendres(client, "status handler commands and arguments:\n");
    sendres(client, "  st                : show status of status server\n");
    sendres(client, "  gen2              : show parameters for Gen2\n");
    sendres(client, "  nframe [X]        : set averaging frame number for fast status\n");
    sendres(client, "  pollfast {on|off} : turn on/off fast status polling\n");
    sendres(client, "  pollslow {on|off} : turn on/off slow status polling\n");
    sendres(client, "  log {on|off}      : turn on/off telemetry log\n");
    sendres(client, "  help              : show this message\n");
    
    return 0;
}


/* Command "status nframe" */
static int status_cmd_nframe(client_t *client, status_t *status){
  int val;

    /* check number of argument */
  if (getargc(client) < 3) {
    sendres_missing_arg(client);
    return -1;
  }

    /* check argument */
  if(getargv_int(client, 2, &val, STATUS_MIN_NFRAME, STATUS_MAX_NFRAME) < 0){
    return -1;
  }

  info("%s: nframe %d", status->header, val);

  pthread_rwlock_wrlock(&(status->cache_lock));
  status->nFrame = val;
  pthread_rwlock_unlock(&(status->cache_lock));

  return 0;
}


/* Command "status nframe" */
static int status_cmd_log(client_t *client, status_t *status){
  char *arg;

  /* check number of argument */
  if (getargc(client) < 3) {
    sendres_missing_arg(client);
    return -1;
  }

  arg = getargv(client, 2);

  info("%s: log %s", status->header, arg);

  pthread_rwlock_wrlock(&(status->cache_lock));
  if(strcmp(arg,"on")==0) status->log_telemetry = 1;
  else status->log_telemetry = 0;
  pthread_rwlock_unlock(&(status->cache_lock));

  return 0;
}



/* Command "status gen2" */
static int status_cmd_gen2(client_t *client, status_t *status){
  int ret = 0;
  struct gain_stat *gstat = &(status->gain->stat);
  struct status_fast *fstat = &(status->stat_fast);


  /******* LOOP ********/
  if(status->loop->stat.onoff == 0) sendres(client, "LOOP : State = OFF\n");
  else sendres(client, "LOOP : State = ON\n");

  /******* GAIN ********/
  sendres(client, "GAIN : DMG = %.4f", gstat->dmg);
  sendres(client, " , TTG = %.4f\n", gstat->ttg);
  sendres(client, "     : HTT = %.4f", gstat->htt);
  sendres(client, " , HDF = %.4f\n", gstat->hdf);
  sendres(client, "     : LTT = %.4f", gstat->ltt[0]);
  sendres(client, " , LDF = %.4f\n", gstat->ldf);
  sendres(client, "     : WTT = %.4f", gstat->wtt);
  sendres(client, " , ADF = %.4f\n", gstat->adf);

  /******* TT ********/
  /* TTM */
  sendres(client, "TT   : TT_tip = %.4f [V] , TT_tilt = %.4f [V]\n", fstat->ave_dmtt[0], fstat->ave_dmtt[1]);
  /* WTT */
  sendres(client, "     : WTT_CH1 = %.4f [V] , WTT_CH2 = %.4f [V]\n", fstat->ave_wtt[0], fstat->ave_wtt[1]);

  /******* APD ********/
  sendres(client, "APD  : HOWFS-Ave. = %.2f [kcnt/sec/elem] , ( Rmag = %.2f )\n", fstat->ave_hapdstat.ave, fstat->ave_hmag);
  sendres(client, "     : LOWFS-Ave. = %.2f [kcnt/sec/elem] , ( Rmag = %.2f )", fstat->ave_lapdstat.ave, fstat->ave_hmag);

  return ret;
}

/* Command "status st" */
static int status_cmd_st(client_t *client, status_t *status){
  int nFrame;
  int log_telemetry;

  pthread_rwlock_rdlock(&(status->cache_lock));
  nFrame = status->nFrame;
  log_telemetry = status->log_telemetry;
  pthread_rwlock_unlock(&(status->cache_lock));

  /* check if the fast poll is running */
  if (poll_isrunning(&(status->poll_fast)) == 1) sendres(client, "Fast Status =  Running\n");
  else sendres(client, "Fast Status = Stop\n");

  /* check if the slow poll is running */
  if (poll_isrunning(&(status->poll_slow)) == 1) sendres(client, "Slow Status =  Running\n");
  else sendres(client, "Slow Status = Stop\n");

  /* check frame */
  sendres(client, "Averaged frame = %d\n", nFrame);

  if(log_telemetry==1) sendres(client, "Telemetry log = ON");
  else sendres(client, "Telemetry log = OFF");

  return 0;
}


/*
 * Process cntmonst commands
 */
int status_proccmd(client_t *client, status_t *status){
  char *cmd = getargv(client, 1);
  char *arg = getargv(client, 2);
  
  if (cmd != NULL) {
    strtolower(cmd);
  }
  
  if (cmd == NULL) { /* help */
    return status_cmd_help(client, status);
  }
  
  if (arg == NULL) {
    arg = "";
  }
  
  switch(cmd[0]) {
  case 'g':
    if (strcmp(cmd, "gen2") == 0) { /* status for gen2 */
      return status_cmd_gen2(client, status);
    }
    break;
  case 'h':
    if (strcmp(cmd, "help") == 0) { /* help */
      return status_cmd_help(client, status);
    }
    break;
  case 'l':
    if (strcmp(cmd,"log") == 0) { /* log */
      return status_cmd_log(client, status);
    }
    break;  
  case 'n':
    if (strcmp(cmd,"nframe") == 0) { /* number of frame for averaging */
      return status_cmd_nframe(client, status);
    }
    break;  
  case 'p':
    if (strcmp(cmd, "pollfast") == 0) { /* fast poll on/off */
      if (poll_cmd_poll(client, &(status->poll_fast)) != 0)
	return -1;
      return 0; 
    }
    if (strcmp(cmd, "pollslow") == 0) { /* fast poll on/off */
      if (poll_cmd_poll(client, &(status->poll_slow)) != 0)
	return -1;
      return 0; 
    }
    break;
  case 's':
    if (strcmp(cmd,"st") == 0) { /* st */
      return status_cmd_st(client, status);
    }
    break; 
  }
  sendres_unknown_cmd(client, cmd);
  
  return 0;
}
