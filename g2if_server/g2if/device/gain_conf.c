/* -------------------------------------------------------------------------
 * gain_conf.c -- Functions for reading configuration file
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/01/19   Y. Ono        Initial version
 * -------------------------------------------------------------------------
 */
#include <stdio.h>			/* for snprintf() */
#include <string.h>			/* for strcmp(), strncpy() */
#include <limits.h>			/* for USHRT_MAX */
#include <values.h>                     /* for DBL_MAX */
#include <errno.h>			/* for errno */
#include "log.h"			/* for error(), info(), debug() */
#include "conf.h"			/* for setpar_int() and etc */
#include "stringx.h"			/* for strjoin() */
#include "gain.h"			/* for gain_t */


/*
 * Process a configuration parameter for gainler
 */
int gain_procconf(gain_t *gain, const char *sect, int argc, const char **argv){
  const char *key = argv[0];
  char subsect[32];
  
  if (getsubsect(sect, 1, subsect, sizeof(subsect))) {
    setpar_unknown_sect(sect);
    return 0;
  } else if (strcmp(key, "change") == 0){  /* keyword for script to change gain */
    return setpar_strdup(argc, argv, 1, &(gain->change));
  } else if (strcmp(key, "dmg_min") == 0){  /* keyword for dmg min */
    return setpar_flt(argc, argv, 1, &(gain->ming.dmg), 0, 0);
  } else if (strcmp(key, "dmg_max") == 0){  /* keyword for dmg max */
    return setpar_flt(argc, argv, 1, &(gain->maxg.dmg), 0, 0);
  } else if (strcmp(key, "ttg_min") == 0){  /* keyword for ttg min */
    return setpar_flt(argc, argv, 1, &(gain->ming.ttg), 0, 0);
  } else if (strcmp(key, "ttg_max") == 0){  /* keyword for ttg max */
    return setpar_flt(argc, argv, 1, &(gain->maxg.ttg), 0, 0);
  } else if (strcmp(key, "htt_min") == 0){  /* keyword for htt min */
    return setpar_flt(argc, argv, 1, &(gain->ming.htt), 0, 0);
  } else if (strcmp(key, "htt_max") == 0){  /* keyword for htt max */
    return setpar_flt(argc, argv, 1, &(gain->maxg.htt), 0, 0);
  } else if (strcmp(key, "hdf_min") == 0){  /* keyword for hdf min */
    return setpar_flt(argc, argv, 1, &(gain->ming.hdf), 0, 0);
  } else if (strcmp(key, "hdf_max") == 0){  /* keyword for hdf max */
    return setpar_flt(argc, argv, 1, &(gain->maxg.hdf), 0, 0);
  } else if (strcmp(key, "ltt_min") == 0){  /* keyword for ltt min */
    return setpar_flt(argc, argv, 1, &(gain->ming.ltt[0]), 0, 0);
  } else if (strcmp(key, "ltt_max") == 0){  /* keyword for ltt max */
    return setpar_flt(argc, argv, 1, &(gain->maxg.ltt[0]), 0, 0);
  } else if (strcmp(key, "ldf_min") == 0){  /* keyword for ldf min */
    return setpar_flt(argc, argv, 1, &(gain->ming.ldf), 0, 0);
  } else if (strcmp(key, "ldf_max") == 0){  /* keyword for ldf max */
    return setpar_flt(argc, argv, 1, &(gain->maxg.ldf), 0, 0);
  } else if (strcmp(key, "wtt_min") == 0){  /* keyword for wtt min */
    return setpar_flt(argc, argv, 1, &(gain->ming.wtt), 0, 0);
  } else if (strcmp(key, "wtt_max") == 0){  /* keyword for wtt max */
    return setpar_flt(argc, argv, 1, &(gain->maxg.wtt), 0, 0);
  } else if (strcmp(key, "adf_min") == 0){  /* keyword for ldf min */
    return setpar_flt(argc, argv, 1, &(gain->ming.adf), 0, 0);
  } else if (strcmp(key, "adf_max") == 0){  /* keyword for adf max */
    return setpar_flt(argc, argv, 1, &(gain->maxg.adf), 0, 0);
  }


  setpar_unknown_par(key);
  return 0;
}

/*
 * Print all configuration parameters
 */
int gain_postconf(gain_t *gain){
  const char *header = gain->header;

  info("%s: gain change script = \"%s\"", header, gain->change);
  info("%s: dmg range [ %.4f : %.4f ]", header, gain->ming.dmg, gain->maxg.dmg);
  info("%s: ttg range [ %.4f : %.4f ]", header, gain->ming.ttg, gain->maxg.ttg);
  info("%s: htt range [ %.4f : %.4f ]", header, gain->ming.htt, gain->maxg.htt);
  info("%s: hdf range [ %.4f : %.4f ]", header, gain->ming.hdf, gain->maxg.hdf);
  info("%s: ltt range [ %.4f : %.4f ]", header, gain->ming.ltt[0], gain->maxg.ltt[0]);
  info("%s: ldf range [ %.4f : %.4f ]", header, gain->ming.ldf, gain->maxg.ldf);
  info("%s: wtt range [ %.4f : %.4f ]", header, gain->ming.wtt, gain->maxg.wtt);
  info("%s: adf range [ %.4f : %.4f ]", header, gain->ming.adf, gain->maxg.adf);

  return 0;
}
