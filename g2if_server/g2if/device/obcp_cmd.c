/* -------------------------------------------------------------------------
 * obcp_cmd.c -- Functions to parse and process user commands 
 *               for OBCP server handler
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/18   Y. Ono        Initial version
 *
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
#include "obcp.h"				/* for obcp_t and its functions */

/*
 * Send error message to client if error exists
 */
int obcp_sendres(client_t *client, obcp_t *obcp, int ret, const char *retstr){
  char buf[RESSTR_MAX + 1];

  if (ret != 0) {
    retstr = strerror_r(errno, buf, sizeof(buf));
    sendres(client, RES_HEAD_ERR"%s: %s\n", obcp->header, retstr);
    return -1;
  }else if(strstr(retstr,"ERR") != NULL || strstr(retstr,"Error:") != NULL){
    sendres(client, RES_HEAD_ERR"%s: %s", obcp->header, retstr);
    return -1;
  }
  return 0;
}

/*
 * Process obcp communication "connect" command
 */
static int obcp_cmd_connect(client_t *client, obcp_t *obcp){
  int ret;
  char errstr[OBCP_ERRSTR_MAX + 1];
    
  info("%s: connect", obcp->header);

  /* Check connection */
  if (comm_isconn(&(obcp->comm))) {
    sendres(client, "obcp (%s) is already connected", obcp->comm.addr);
    return 0;
  }

  ret = obcp_connect(obcp);

  return obcp_sendres(client, obcp, ret, errstr);
}

/*
 * Process obcp communication "disconnect" command
 */
static int obcp_cmd_disconnect(client_t *client, obcp_t *obcp){
  int ret;
  char errstr[OBCP_ERRSTR_MAX + 1];
    
  info("%s: disconnect", obcp->header);
    
  /* Check connection */
  if (!comm_isconn(&(obcp->comm))) {
    sendres(client, "obcp (%s) is already disconnected", obcp->comm.addr);
    return 0;
  }

  errstr[0]='\0';

  ret = obcp_disconnect(obcp);
  return obcp_sendres(client, obcp, ret, errstr);
}


/*
 * Send a command to OBCP server to control shutter
 */
static int obcp_shuttercmd_send(client_t *client, obcp_t *obcp){
  int ret = 1;
  char errstr[OBCP_ERRSTR_MAX + 1];
  char retstr[RESSTR_MAX + 1];
  comm_t *comm = &(obcp->comm);
  char *dev = getargv(client, 1);
  char *cmd = getargv(client, 2);
  char allcmd[OBCP_ERRSTR_MAX + 1];
    
  info("%s: %s %s", obcp->header, dev, cmd);
    
  errstr[0]='\0';

  if((ret = obcp_connect(obcp))<0){
    sendres(client, "cannot connect to obcp relay server (%s:%d)", comm->addr, comm->port);
    return -1;
  }

  /* Exclude other threads until end of communication */
  comm_lock(comm);
  pthread_cleanup_push((void *)comm_unlock, comm);

  /* Check connection */
  if (comm_chkconn(comm) >= 0){
    if (strcmp(dev, "esh") == 0 || strcmp(dev, "allsh") == 0){
      sprintf(allcmd, "calsci entshut %s", cmd);
      ret = comm_sendrecv(comm, allcmd, retstr, sizeof(retstr));
      sendres(client, "%s", retstr);
    }
    if (strcmp(dev, "hsh") == 0 || strcmp(dev, "allsh") == 0){
      sprintf(allcmd, "howfs lash %s", cmd);
      ret = comm_sendrecv(comm, allcmd, retstr, sizeof(retstr));
      sendres(client, "%s", retstr);
    }
    if (strcmp(dev, "lsh") == 0 || strcmp(dev, "allsh") == 0){
      sprintf(allcmd, "lowfs lash %s", cmd);
      ret = comm_sendrecv(comm, allcmd, retstr, sizeof(retstr));
      sendres(client, "%s", retstr);
    }
  }
  pthread_cleanup_pop(1);

  if((ret = obcp_disconnect(obcp))<0){
    sendres(client, "cannot disconnect from obcp relay server (%s:%d)", comm->addr, comm->port);
    return -1;
  }
  return obcp_sendres(client, obcp, ret, errstr);
}


/*
 * Process "help" command
 */
static int obcp_cmd_help(client_t *client, obcp_t *obcp){
    
  char *grp = getargv(client, 0);

  if (strcmp(grp, "obcp") == 0){
    sendres(client, "Usage: obcp <device> <device command> [<argument>]\n");
    sendres(client, "    or obcp <control comand> [<argument>]\n");
    sendres(client, "  devices:\n");
    sendres(client, "    esh            : AO188 entrance shutter\n");
    sendres(client, "    hsh            : HOWFS lenslet array shutter\n");
    sendres(client, "    lsh            : LOWFS lenslet array shutter\n");
    sendres(client, "    allsh          : all shutters\n");
    sendres(client, "  control command and arguments:\n");
    sendres(client, "    connect        : connect to OBCP server\n");
    sendres(client, "    disconnect     : dissconnect from OBCP server\n");
    sendres(client, "    dump {on|off}  : turn on/off dump of communication\n");
    sendres(client, "    help           : show this message\n");
  } else if (strcmp(grp, "shutter") == 0){
    sendres(client, "Usage: shutter <device> <device command> [<argument>]\n");
    sendres(client, "    or shutter <control comand> [<argument>]\n");
    sendres(client, "  devices:\n");
    sendres(client, "    esh            : AO188 entrance shutter\n");
    sendres(client, "    hsh            : HOWFS lenslet array shutter\n");
    sendres(client, "    lsh            : LOWFS lenslet array shutter\n");
    sendres(client, "    allsh          : all shutters\n");
    sendres(client, "  control command and arguments:\n");
    sendres(client, "    help           : show this message\n");
  }
  return 0;
}


/*
 * Process "shutter help" command
 */
static int obcp_shuttercmd_help(client_t *client, obcp_t *obcp){
  char *grp = getargv(client, 0);
  char *dev = getargv(client, 1);

  sendres(client, "Usage: %s %s <command>\n", grp, dev);
  sendres(client, "  command:\n");
  sendres(client, "    open          : open shutter\n");
  sendres(client, "    close         : close shutter\n");
  sendres(client, "    st            : show status (using cashe)\n");
  sendres(client, "    stu           : show status (not using cashe)\n");
  sendres(client, "    help          : show this message\n");

  return 0;
}

/*
 * Process obcp lash commands
 */
static int obcp_shutter_proccmd(client_t *client, obcp_t *obcp){
  char *cmd = getargv(client, 2);

  if (cmd != NULL) {
    strtolower(cmd);
  }
    
  if (cmd == NULL) { /* help */
    return obcp_shuttercmd_help(client, obcp);
  }

  switch(cmd[0]) {
  case 'c':
    if (strcmp(cmd, "close") == 0) { /* close shutter */
      return obcp_shuttercmd_send(client, obcp);
    }
  case 'h':
    if (strcmp(cmd, "help") == 0) { /* help */
      return obcp_shuttercmd_help(client, obcp);
    }
    break;
  case 'o':
    if (strcmp(cmd, "open") == 0) { /* open shutter */
      return obcp_shuttercmd_send(client, obcp);
    }
    break;
  case 's':
    if (strcmp(cmd, "st") == 0) { /* show status using cashe */
      return obcp_shuttercmd_send(client, obcp);
    }
    if (strcmp(cmd, "stu") == 0) { /* show status not using cashe */
      return obcp_shuttercmd_send(client, obcp);
    }
    break;
  }
  sendres_unknown_cmd(client, cmd);
  return 0;
}
   
/*
 * Process obcp commands
 */
int obcp_proccmd(client_t *client, obcp_t *obcp){
  char *cmd = getargv(client, 1);
  char *arg = getargv(client, 2);
    
  if (cmd != NULL) {
    strtolower(cmd);
  }
    
  if (cmd == NULL) { /* help */
    return obcp_cmd_help(client, obcp);
  }
    
  if (arg == NULL) {
    arg = "";
  }
    
  switch(cmd[0]) {
  case 'a':
    if (strcmp(cmd, "allsh") == 0) { /* all shutter */
      return obcp_shutter_proccmd(client, obcp);
    }
    break;
  case 'c':
    if (strcmp(cmd, "connect") == 0) { /* connect */
      return obcp_cmd_connect(client, obcp);
    }
    break;
  case 'd':
    if (strcmp(cmd, "disconnect") == 0) { /* disconnect */
      return obcp_cmd_disconnect(client, obcp);
    }else if (strcmp(cmd, "dump") == 0) { /* dump */
      return comm_cmd_dump(client, &(obcp->comm));
    }
    break;
  case 'e':
    if (strcmp(cmd, "esh") == 0) { /* entranc shutter */
      return obcp_shutter_proccmd(client, obcp);
    }
    break;
  case 'h':
    if (strcmp(cmd, "help") == 0) { /* help */
      return obcp_cmd_help(client, obcp);
    }
    if (strcmp(cmd, "hsh") == 0) { /* howfs lash */
      return obcp_shutter_proccmd(client, obcp);
    }
    break;
  case 'l':
    if (strcmp(cmd, "lsh") == 0) { /* lowfs lash */
      return obcp_shutter_proccmd(client, obcp);
    }
    break;
  }
  sendres_unknown_cmd(client, cmd);
    
  return 0;
}
