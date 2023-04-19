/* -------------------------------------------------------------------------
 * apdsafe.h -- Function for APDSAFE control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/06/20   Y. Ono        Initial version 
 *
 * -------------------------------------------------------------------------
 */

#ifndef _APDSAFE_H
#define _APDSAFE_H

#include <sys/time.h>		/* for struct timeval */
#include <pthread.h>		/* for pthread_* */
#include "comm.h"		/* for comm_t */
#include "device.h"		/* for struct device_ops */
#include "poll.h"               /* for poll_t */
#include "server.h"		/* for client_t */
#include "conf.h"
#include "shms.h"               /* for shms_t */
#include "howfs.h"              /* for howfs_t */
#include "lowfs.h"              /* for lowfs_t */

/* Buffer size or maximum length of string from/to apdsafeler */
enum {
    APDSAFE_COMM_BUFSIZ = 1024,	/* buffer size for communication */
    APDSAFE_CMDSTR_MAX = 256,	/* for sending command */
    APDSAFE_ERRSTR_MAX = 256,	/* for error message */
};

/* Default header string for logging messages */
#define APDSAFE_HEADER_DEFAULT  "apdsafe"

/* Muximum and minimum */
#define APDSAFE_POLL_INTERVAL_FAST       0
#define APDSAFE_MIN_LIMIT                0.
#define APDSAFE_MAX_LIMIT            10000.
#define APDSAFE_DEF_NFRAME              10
#define APDSAFE_DEF_LIMIT             2000.
#define APDSAFE_POLL_INTERVAL            0
#define APDSAFE_MIN_NFRAME               1
#define APDSAFE_MAX_NFRAME             100


typedef struct apdsafe{

  shms_t *shms;
  IMAGE *shm_apdcnt;
  float *apdcnt;

  /* header string for logging message */
  char *header;

  /* config given in status.c */
  int *hapdmap; // apd mapping for HOWFS
  int *lapdmap; // apd mapping for LOWFS

  /* poll */
  poll_t poll;	/* data for polling thread */

  /* parameter */
  int cnt;
  int nframe;
  float max_limit;
  int emergency; // on|off
  pthread_rwlock_t cache_lock;       /* lock of cache */

  howfs_t *howfs;
  lowfs_t *lowfs;

} apdsafe_t;

/* bash script for CACAO control */
#define CMD_APDSAFE_CHECK  "check_prog_run apdsafe"

/* Device handler operation functions */
extern const struct device_operations apdsafe_ops;

/* Function prototypes */
int apdsafe_init(apdsafe_t *apdsafe, const char *header);
int apdsafe_free(apdsafe_t *apdsafe);
int apdsafe_open(apdsafe_t *apdsafe);
int apdsafe_close(apdsafe_t *apdsafe);
int apdsafe_procconf(apdsafe_t *apdsafe, const char *subsec, int argc, const char **argv);
int apdsafe_postconf(apdsafe_t *apdsafe);    
int apdsafe_proccmd(client_t *client, apdsafe_t *apdsafe);

#endif /* _APDSAFE_H */
