/* -------------------------------------------------------------------------
 * status.h -- Function for STATUS control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/18   Y. Ono        Initial version (tested with dummy shm)
 *
 * -------------------------------------------------------------------------
 */

#ifndef _STATUS_H
#define _STATUS_H

#include <sys/time.h>		/* for struct timeval */
#include <pthread.h>		/* for pthread_* */
#include "comm.h"		/* for comm_t */
#include "device.h"		/* for struct device_ops */
#include "poll.h"               /* for poll_t */
#include "server.h"		/* for client_t */
#include "conf.h"
#include "shms.h"               /* for shms_t */
#include "gain.h"
#include "loop.h"
#include "howfs.h"
#include "lowfs.h"
#include "apdsafe.h"

/* Buffer size or maximum length of string from/to statusler */
enum {
    STATUS_COMM_BUFSIZ = 1024,	/* buffer size for communication */
    STATUS_CMDSTR_MAX = 256,	/* for sending command */
    STATUS_ERRSTR_MAX = 256,	/* for error message */
};

/* Default header string for logging messages */
#define STATUS_HEADER_DEFAULT	"status"

/* Default Parameters */
#define APD_NUM                216
#define HOAPD_NUM              188
#define CURV_NUM               188
#define DMACT_NUM              188
#define LOAPD_NUM               16
#define STATUS_DEF_NFRAME             200
#define STATUS_MIN_NFRAME               0
#define STATUS_MAX_NFRAME            5000
#define STATUS_POLL_INTERVAL_FAST       0
#define STATUS_POLL_INTERVAL_SLOW       1
#define FUNC_APD_HMAG(cnt)       (14.8873-2.5*log10(cnt))
#define FUNC_APD_LMAG(cnt)       (17.2781-2.5*log10(cnt))

struct statistics{
  float std;
  float ave;
  float min;
  float max;
};

struct status_fast{
  /* HOWFS APD count */
  float ave_hapdcnt[HOAPD_NUM];
  struct statistics ave_hapdstat;
  float ave_hmag;
  /* LOWFS APD count */
  float ave_lapdcnt[LOAPD_NUM];
  struct statistics ave_lapdstat;
  float ave_lmag;
  /* HOWFS Curvature */
  float ave_curv[CURV_NUM];
  struct statistics ave_curvstat;
  /* DM voltage */
  float ave_dmvolt[DMACT_NUM];
  struct statistics ave_dmvoltstat;
  /* TTM voltage */
  float ave_dmtt[2];
  /* WTT voltage */
  float ave_wtt[2];
  /* LOWFS slope */
  float ave_lslope[8];
  /* LOWFS TT */
  float ave_lott[2];
  /* LOWFS DF */
  float ave_lodf;
};

typedef struct status{

  /* shm */
  shms_t *shms;
  IMAGE *shm_apdcnt;
  float *apdcnt; // shortcut for APD shm
  float *curv;   // shortcut for Curv shm
  float *dmvolt; // shortcut for DM shm
  float *dmtt;   // shortcut for DM shm
  float *wtt;    // shortcut for DM shm
  float *lott;   // shortcut for LOWFS TT
  float *lodf;   // shortcut for LOWFS defocus

  /* config */
  char *hapdconf; // apd mapping config for HOWFS
  char *lapdconf; // apd mapping config for LOWFS
  char *foldtele; // folder root for telemetry log file.
  int *hapdmap; // apd mapping for HOWFS
  int *lapdmap; // apd mapping for LOWFS

  /* header string for logging message */
  char *header;

  /* poll */
  poll_t poll_fast;	/* data for fast polling thread */
  poll_t poll_slow;	/* data for slow polling thread */

  /* cache */
  int nFrame;
  struct status_fast stat_fast;
  pthread_rwlock_t cache_lock;       /* lock of cache */
  FILE *fp_telemetry; /* for telemetry log */
  int log_telemetry; /* on/off telemetry log */

  gain_t     *gain;
  howfs_t    *howfs;
  lowfs_t    *lowfs;
  loop_t     *loop;
  apdsafe_t  *apdsafe;

} status_t;

/* Device handler operation functions */
extern const struct device_operations status_ops;

/* Function prototypes */
int status_init(status_t *status, const char *header);
int status_free(status_t *status);
int status_open(status_t *status);
int status_close(status_t *status);
int status_procconf(status_t *status, const char *subsec, int argc, const char **argv);
int status_postconf(status_t *status);    
int status_proccmd(client_t *client, status_t *status);

#endif /* _STATUS_H */
