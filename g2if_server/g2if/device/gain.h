/* -------------------------------------------------------------------------
 * gain.h -- Function for GAIN control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/18   Y. Ono        Initial version (tested with dummy shm)
 *    2019/09/20   Y. Ono        Add cashe
 *    2019/09/26   Y. Ono        Add fifo for DMG
 * -------------------------------------------------------------------------
 */

#ifndef _GAIN_H
#define _GAIN_H

#include <sys/time.h>		/* for struct timeval */
#include <pthread.h>		/* for pthread_* */
#include "comm.h"		/* for comm_t */
#include "device.h"		/* for struct device_ops */
#include "poll.h"               /* for poll_t */
#include "server.h"		/* for client_t */
#include "conf.h"
#include "shms.h"               /* for shms_t */
#include "fifo_func.h"		/* for fifo_t */
#include "loop.h"               /* for loop_t */

/* Buffer size or maximum length of string from/to gainler */
enum {
    GAIN_COMM_BUFSIZ = 1024,	/* buffer size for communication */
    GAIN_CMDSTR_MAX = 256,	/* for sending command */
    GAIN_ERRSTR_MAX = 256,	/* for error message */
};

/* Maximum number of status arguments */
#define GAIN_STATARG_MAX	10000

/* Delimiter indicating end of command and response strings */
#define GAIN_DELIM_IN	"\r"
#define GAIN_DELIM_OUT	"\r\n"

/* Default header string for logging messages */
#define GAIN_HEADER_DEFAULT  "gain"

/* FIFO INFO for GAIN */
#define GAIN_FIFO_NAME      "/milk/shm/g2if_gain.fifo"
#define GAIN_FIFO_DMG       "loopRUN-1.loopgain" // 1 = hardware, 2 = cacao simulator

/* Structure to store gain values */
struct gain_stat {
  float dmg;
  float ttg;
  float htt;
  float hdf;
  float ltt[2];
  float ldf;
  float wtt;
  float adf;
};

typedef struct gain{

  /* for communication with controller */
  comm_t comm;	/* data for communication */

  shms_t *shms;
  IMAGE *shm_curv;
  float *curv;

  /* header string for logging message */
  char *header;

  /* script to change gain (except for dmg) */
  char *change;

  /* min and max */
  struct gain_stat ming;
  struct gain_stat maxg;

  /* cache */
  struct gain_stat stat;
  float scanstep;
  float scaninterval;
  pthread_rwlock_t cache_lock;       /* lock of cache */

  /* fifo */
  struct fifo_t fifo;
    
  /* loop */
  loop_t *loop;

} gain_t;



/* Device handler operation functions */
extern const struct device_operations gain_ops;

/* Function prototypes */
int gain_init(gain_t *gain, const char *header);
int gain_free(gain_t *gain);
int gain_open(gain_t *gain);
int gain_close(gain_t *gain);
int gain_procconf(gain_t *gain, const char *subsec, int argc, const char **argv);
int gain_postconf(gain_t *gain);    
int gain_proccmd(client_t *client, gain_t *gain);
int gain_getdmg(gain_t *gain, float *dmg);
int gain_setdmg(gain_t *gain, float dmg);
int gain_getstat(gain_t *gain, struct gain_stat *stat);
int gain_savestat(gain_t *gain, struct gain_stat *stat);

#endif /* _GAIN_H */
