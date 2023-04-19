/* -------------------------------------------------------------------------
 * adf_conf.h -- Functions to parse and process commands for ADF control
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
#include "adf.h"			/* for adf_t and its functions */


/* Command "adf help" */
static int adf_cmd_help(client_t *client, adf_t *adf){

  sendres(client, "Usage: adf <command> [<argument>]\n");
  sendres(client, "  commands and arguments:\n");
  sendres(client, "    st             : show current status\n");
  sendres(client, "    help           : show this message\n");

  return 0;
}

/* Command "adf st" */
static int adf_cmd_st(client_t *client, adf_t *adf){
  int ret = 0;
  float gain = 0.0;
  float adf_defocus = 0.0;
  shms_t *shms = adf->shms;
  char errstr[ADF_ERRSTR_MAX + 1];

  /* read DMG */
  ret = gain_getdmg(adf->gain, &gain);
  if(ret >= 0) sendres(client, "DMG = %.4f\n", gain);

  /* read ADF gain */
  if((ret = shms_read_float(shms, KEY_ADF_GAIN, &gain, 1, errstr)) < 0){
    sendres(client, "%s", errstr);
    return ret;
  }
  sendres(client, "ADF_GAIN = %.4f\n", gain);

  /* read defocus */
  if((ret = shms_read_float(shms, KEY_ADFGAIN_X_DF, &adf_defocus, 1, errstr)) < 0){
    sendres(client, "%s", errstr);
    return ret;
  }
  sendres(client, "ADF_DEFOCUS = %f\n", adf_defocus);

  /* set 0 for ADF defocus for safety */
  adf_defocus = 0;
  if((ret = shms_write_float(shms, KEY_ADFGAIN_X_DF, &adf_defocus, 1, errstr)) < 0){
    sendres(client, "%s", errstr);
    return ret;
  }

  return 0;
}



/*
 * Process adf commands
 */
int adf_proccmd(client_t *client, adf_t *adf){
  char *cmd = getargv(client, 1);
  
  if (cmd != NULL) {
    strtolower(cmd);
  }
  
  if (cmd == NULL) { /* help */
    return adf_cmd_help(client, adf);
  }
  
  switch(cmd[0]) {
  case 'h':
    if (strcmp(cmd, "help") == 0) { /* help */
      return adf_cmd_help(client, adf);
    }
    break;
  case 's':
    if (strcmp(cmd, "st") == 0) { /* status */
      return adf_cmd_st(client, adf);
    }
    break;
  }

  sendres_unknown_cmd(client, cmd);
  return 0;
}
