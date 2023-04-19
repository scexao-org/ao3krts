/* -------------------------------------------------------------------------
 * gain_conf.h -- Functions to parse and process commands for GAIN gain
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
#include "gain.h"			/* for gain_t and its functions */
#include "status.h"			/* for CURV_NNUM */
#include "tool.h"			/* for CURV_NNUM */


/* Command "gain help" */
static int gain_cmd_help(client_t *client, gain_t *gain){

  sendres(client, "Usage: gain <command> [<argument>]\n");
  sendres(client, "  commands and arguments:\n");
  sendres(client, "    dmg [X]          : set high-order DM gain to X\n");
  sendres(client, "    ttg [X]          : set DM tip/tilt offload gain to X\n");
  sendres(client, "    htt [X]          : set high-order tip/tilt gain to X\n");
  sendres(client, "    hdf [X]          : set high-order defocus gain to X\n");
  sendres(client, "    ltt [X]          : set low-order tip/tilt gain to X\n");
  sendres(client, "    ldf [X]          : set low-order defocus gain to X\n");
  sendres(client, "    wtt [X]          : set high-order wfs tip/tilt offload gain to X\n");
  sendres(client, "    adf [X]          : set ADF loop gain to X\n");
  sendres(client, "    clear            : initialize gain values\n");
  sendres(client, "    scan [X]         : scanning dmg from current to X using curvature rms\n");
  sendres(client, "    scanstep [X]     : set gain scan step\n");
  sendres(client, "    scaninterval [X] : set gain scan interval [s]\n");
  sendres(client, "    st               : show all gains\n");
  sendres(client, "    stc              : show all gains (cashe)\n");
  sendres(client, "    help             : show this message\n");

  return 0;
}

/* Command to set a gain */
static int gain_cmd_set(client_t *client, gain_t *gain){
  char *cmd = getargv(client, 1);
  float val = 0.0, min = 0.0, max = 0.0;
  int ret = 0;
  char key[KEY_STR_MAX+1];
  char msg[100];
  struct gain_stat *ming = &(gain->ming);
  struct gain_stat *maxg = &(gain->maxg);

  if (strcmp(cmd, "dmg") == 0) {
    min = ming->dmg;
    max = maxg->dmg;
  } else if (strcmp(cmd, "ttg") == 0) {
    min = ming->ttg;
    max = maxg->ttg;
    strcpy(key, KEY_TTG_GAIN);
  } else if (strcmp(cmd, "htt") == 0) {
    min = ming->htt;
    max = maxg->htt;
    strcpy(key, KEY_HTT_GAIN);
  } else if (strcmp(cmd, "hdf") == 0) {
    min = ming->hdf;
    max = maxg->hdf;
    strcpy(key, KEY_HDF_GAIN);
  } else if (strcmp(cmd, "ltt") == 0) {
    min = ming->ltt[0];
    max = maxg->ltt[0];
    strcpy(key, KEY_LTT_GAIN);
  } else if (strcmp(cmd, "ldf") == 0) {
    min = ming->ldf;
    max = maxg->ldf;
    strcpy(key, KEY_LDF_GAIN);
  } else if (strcmp(cmd, "wtt") == 0) {
    min = ming->wtt;
    max = maxg->wtt;
    strcpy(key, KEY_WTT_GAIN);
  } else if (strcmp(cmd, "adf") == 0) {
    min = ming->adf;
    max = maxg->adf;
    strcpy(key, KEY_ADF_GAIN);
  } else{
    return -1;
  }

  /* check number of argument */
  if (getargc(client) < 3) {
    sendres_missing_arg(client);
    return -1;
  }

  /* check argument */
  if(getargv_flt(client, 2, &val, min, max) < 0){
    return -1;
  }

 /* Log command */
  info("> %s: %s %f", gain->header, cmd, val);

  /* set gain */
  if((strcmp(cmd,"ltt")==0 || strcmp(cmd,"wtt")==0) && val != 0.0){
    sprintf(msg, "%s %s 0 0", gain->change, KEY_HTT_GAIN);
    system(msg);
  } else if((strcmp(cmd,"adf")==0 || strcmp(cmd,"ldf")==0) && val != 0.0){
    sprintf(msg, "%s %s 0 0", gain->change, KEY_HDF_GAIN);
    system(msg);
  } else if(strcmp(cmd,"htt")==0 && val == 1.0){
    sprintf(msg, "%s %s 0 0", gain->change, KEY_LTT_GAIN);
    system(msg);
    sprintf(msg, "%s %s 0 1", gain->change, KEY_LTT_GAIN);
    system(msg);
    sprintf(msg, "%s %s 0 0", gain->change, KEY_WTT_GAIN);
    system(msg);
  } else if(strcmp(cmd,"hdf")==0 && val == 1.0){
    sprintf(msg, "%s %s 0 0", gain->change, KEY_LDF_GAIN);
    system(msg);
    //sprintf(msg, "%s %s 0 0", gain->change, KEY_ADF_GAIN);
    //system(msg);
  }

  if(strcmp(cmd,"dmg")==0){
    gain_setdmg(gain, val);
  } else if(strcmp(cmd, "ltt") == 0) {
    sprintf(msg, "%s %s %.4f 0", gain->change, key, val);
    system(msg);
    sprintf(msg, "%s %s %.4f 1", gain->change, key, val);
    system(msg);
  }
  else if(strcmp(cmd, "adf") == 0) {
    sprintf(msg, "%s %s %.4f 0", gain->change, key, val);
    system(msg);
  }
  else{
    sprintf(msg, "%s %s %.4f 0", gain->change, key, val);
    system(msg);
  }


  return ret;
}

/* Command to clear gain values */
static int gain_cmd_clear(client_t *client, gain_t *gain){
  char *cmd = getargv(client, 1);
  char msg[100];


  info("> %s: %s", gain->header, cmd);

  /* TTG */
  //sprintf(msg, "%s %s 0 0", gain->change, KEY_TTG_GAIN);
  //system(msg);

  /* HTT */
  sprintf(msg, "%s %s 1 0", gain->change, KEY_HTT_GAIN);
  system(msg);

  /* HDF */
  sprintf(msg, "%s %s 1 0", gain->change, KEY_HDF_GAIN);
  system(msg);

  /* LTT */
  sprintf(msg, "%s %s 0 0", gain->change, KEY_LTT_GAIN);
  system(msg);
  sprintf(msg, "%s %s 0 1", gain->change, KEY_LTT_GAIN);
  system(msg);

  /* LDF */
  sprintf(msg, "%s %s 0 0", gain->change, KEY_LDF_GAIN);
  system(msg);

  /* WTT */
  sprintf(msg, "%s %s 0 0", gain->change, KEY_WTT_GAIN);
  system(msg);

  /* ADF */
  sprintf(msg, "%s %s 0 0", gain->change, KEY_ADF_GAIN);
  system(msg);

  return 0;
}


/* Command to scan gain values */
static int gain_cmd_scan(client_t *client, gain_t *gain){
  char *cmd = getargv(client, 1);
  loop_t *loop = gain->loop;
  struct loop_stat lstat;
  float val;
  float dmg0, dmg, ave, rms, tmp, ans, bestdmg, minrms;
  float curv[CURV_NUM];
  int i, cnt = 0;
  struct timespec ts1, ts2;
  int stat_timeout = 0;

  info("> %s: starting gain scanning", gain->header, cmd);

  /* check number of argument */
  if (getargc(client) < 3) {
    sendres_missing_arg(client);
    return -1;
  }

  /* check argument */
  if(getargv_flt(client, 2, &val, 0, gain->maxg.dmg) < 0){
    return -1;
  }

  /* check if loop is on */
  loop_getstat(loop, &lstat);
  if(lstat.onoff == 0){
    sendres(client, RES_HEAD_ERR"%s: AO loop should be on before starting gain scan.", gain->header);
    return -1;
  }

  /* get current dmg value */
  if(gain_getdmg(gain, &dmg0)<0){
    sendres(client, RES_HEAD_ERR"%s: Failed to read current dmg value.", gain->header);
    return -1;
  }
  
  /* scanning gain */
  minrms = 1000;
  bestdmg = dmg0;
  for(dmg = dmg0; dmg<=val && dmg<gain->maxg.dmg; dmg+=gain->scanstep){

    /* set gain */
    gain_setdmg(gain, dmg);

    /* wait */
    sleep(1);

    /* get current time */
    clock_gettime(CLOCK_REALTIME, &ts1);
    clock_gettime(CLOCK_REALTIME, &ts2);
    ts1.tv_sec += (int)gain->scaninterval;

    /* check curv rms */
    cnt = 0;
    ans = 0;
    for(;;){
      /* sem_wait for dmapply */
      ts2.tv_sec += 2;
      ImageStreamIO_semtimedwait(gain->shm_curv, 5, &ts2);
      if(errno == ETIMEDOUT){
	stat_timeout = -1;
	break;
      }
      
      /* count frame */
      cnt ++;

      /* get curvature from shm and compute rms*/
      ave = 0;
      for(i=0; i<CURV_NUM; i++){
	curv[i] = gain->curv[i];
	ave+= curv[i];
      }
      ave /= CURV_NUM;
      rms = 0;
      for(i=0; i<CURV_NUM; i++){
	tmp = curv[i] - ave;
	rms += tmp*tmp;
      }
      ans += sqrt(rms/CURV_NUM);

      /* check timeout */
      clock_gettime(CLOCK_REALTIME, &ts2);
      if(cmp_timespec(&ts1, &ts2) <= 0){
	stat_timeout = 1;
	break;
      }
    }

    if( stat_timeout == -1 ){
      sendres(client, RES_HEAD_ERR"%s: ImageStreamIO_semtimedwait (%s) was failed because of timeout.", gain->header, KEY_CURV);
      return -1;
    }

    ans = ans /cnt;
    sendres(client, "dmg = %.3f  rms = %.4f\n", dmg, ans);
    if(minrms > ans){
      minrms = ans;
      bestdmg = dmg;
    }

  }

  /* set gain */
  gain_setdmg(gain, bestdmg);
  sendres(client, "DMG is set to the best one : %.3f\n", bestdmg);

  return 0;
}


/* Command "gain st" */
static int gain_cmd_st(client_t *client, gain_t *gain, const int cashe){
  struct gain_stat *ming = &(gain->ming);
  struct gain_stat *maxg = &(gain->maxg);
  struct gain_stat stat;

  /* get status from shared memories */
  if(cashe == 1)
    stat = gain->stat;
  else{
    gain_getstat(gain, &stat);
    gain_savestat(gain, &stat);
  }

  /* print gain values [min/max] */
  sendres(client, "DMG = %.4f [ %.4f / %.4f ]\n", stat.dmg, ming->dmg, maxg->dmg);
  sendres(client, "TTG = %.4f [ %.4f / %.4f ]\n", stat.ttg, ming->ttg, maxg->ttg);  
  sendres(client, "HTT = %.0f [ %.0f / %.0f ]\n", stat.htt, ming->htt, maxg->htt);  
  sendres(client, "HDF = %.0f [ %.0f / %.0f ]\n", stat.hdf, ming->hdf, maxg->hdf);  
  sendres(client, "LTT = %.4f [ %.4f / %.4f ]\n", stat.ltt[0], ming->ltt[0], maxg->ltt[0]);  
  sendres(client, "LDF = %.4f [ %.4f / %.4f ]\n", stat.ldf, ming->ldf, maxg->ldf);  
  sendres(client, "WTT = %.4f [ %.4f / %.4f ]\n", stat.wtt, ming->wtt, maxg->wtt);  
  sendres(client, "ADF = %.4f [ %.4f / %.4f ]\n", stat.adf, ming->adf, maxg->adf);  
  sendres(client, "SCAN : step = %.4f,  interval = %.2f sec\n", gain->scanstep, gain->scaninterval);  

  return 0;
}

/* Command to change scan step */
static int gain_cmd_scanstep(client_t *client, gain_t *gain){
  char *cmd = getargv(client, 1);
  float val;

  /* check number of argument */
  if (getargc(client) < 3) {
    sendres_missing_arg(client);
    return -1;
  }

  /* check argument */
  if(getargv_flt(client, 2, &val, 0, 0.5) < 0){
    return -1;
  }

  /* log */
  info("> %s: %s %f", gain->header, cmd, val);

  /* */
  pthread_rwlock_wrlock(&(gain->cache_lock));
  gain->scanstep = val;
  pthread_rwlock_unlock(&(gain->cache_lock));


  return 0;
}


/* Command to change scan interval */
static int gain_cmd_scaninterval(client_t *client, gain_t *gain){
  char *cmd = getargv(client, 1);
  float val;

  /* check number of argument */
  if (getargc(client) < 3) {
    sendres_missing_arg(client);
    return -1;
  }

  /* check argument */
  if(getargv_flt(client, 2, &val, 0, 20) < 0){
    return -1;
  }

  /* log */
  info("> %s: %s %f", gain->header, cmd, val);

  /* */
  pthread_rwlock_wrlock(&(gain->cache_lock));
  gain->scaninterval = val;
  pthread_rwlock_unlock(&(gain->cache_lock));


  return 0;
}


/*
 * Process gain commands
 */
int gain_proccmd(client_t *client, gain_t *gain){
  char *cmd = getargv(client, 1);
  
  if (cmd != NULL) {
    strtolower(cmd);
  }
  
  if (cmd == NULL) { /* help */
    return gain_cmd_help(client, gain);
  }
  
  switch(cmd[0]) {
  case 'a':
    if (strcmp(cmd, "adf") == 0) { /* ADF */
      return gain_cmd_set(client, gain);
    }
    break;
  case 'c':
    if (strcmp(cmd, "clear") == 0) { /* ADF */
      return gain_cmd_clear(client, gain);
    }
    break;
  case 'd':
    if (strcmp(cmd, "dmg") == 0) { /* DMG */
      return gain_cmd_set(client, gain);
    }
    break;
  case 'h':
    if (strcmp(cmd, "htt") == 0) { /* HTT */
      return gain_cmd_set(client, gain);
    }
    if (strcmp(cmd, "hdf") == 0) { /* HDF */
      return gain_cmd_set(client, gain);
    }
    if (strcmp(cmd, "help") == 0) { /* help */
      return gain_cmd_help(client, gain);
    }
    break;
  case 'l':
    if (strcmp(cmd, "ltt") == 0) { /* LTT */
      return gain_cmd_set(client, gain);
    }
    if (strcmp(cmd, "ldf") == 0) { /* LDF */
      return gain_cmd_set(client, gain);
    }
    break;
  case 's':
    if (strcmp(cmd, "scan") == 0) { /* scan */
      return gain_cmd_scan(client, gain);
    }
    if (strcmp(cmd, "scanstep") == 0) { /* scanstep */
      return gain_cmd_scanstep(client, gain);
    }
    if (strcmp(cmd, "scaninterval") == 0) { /* scaninterval */
      return gain_cmd_scaninterval(client, gain);
    }
    if (strcmp(cmd, "st") == 0) { /* st */
      return gain_cmd_st(client, gain, 0);
    }
    if (strcmp(cmd, "stc") == 0) { /* stc */
      return gain_cmd_st(client, gain, 1);
    }
    break;
  case 't':
    if (strcmp(cmd, "ttg") == 0) { /* TTG */
      return gain_cmd_set(client, gain);
    }
    break;
  case 'w':
    if (strcmp(cmd, "wtt") == 0) { /* WTT */
      return gain_cmd_set(client, gain);
    }
    break;
  }

  sendres_unknown_cmd(client, cmd);
  return 0;
}
