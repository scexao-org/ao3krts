/* -------------------------------------------------------------------------
 * tt.h -- Function for TT control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/06/17   Y. Ono        Initial version
 *    2019/09/20   Y. Ono        Add saveflat
 * -------------------------------------------------------------------------
 */

#ifndef _TT_H
#define _TT_H

#include <sys/time.h>		/* for struct timeval */
#include <pthread.h>		/* for pthread_* */
#include "comm.h"		/* for comm_t */
#include "device.h"		/* for struct device_ops */
#include "poll.h"               /* for poll_t */
#include "server.h"		/* for client_t */
#include "conf.h"
#include "shms.h"               /* for shms_t */
#include "tool.h"		/* for timer */

/* Buffer size or maximum length of string from/to ttler */
enum {
    TT_COMM_BUFSIZ = 1024,	/* buffer size for communication */
    TT_CMDSTR_MAX = 256,	/* for sending command */
    TT_ERRSTR_MAX = 256,	/* for error message */
};

/* Default header string for logging messages */
#define TT_HEADER_DEFAULT	"tt"
#define VOLT_TO_DAC             819.1
#define TT_MIN_MAKEFLAT_SEC       1
#define TT_MAX_MAKEFLAT_SEC     300       
#define TT_FLATFILE_NAME        "!/home/rts/RTS_2019/conf/saved_dmTT_flats/dm_TT_flat_temp.fits"

typedef struct tt{

  shms_t *shms;
  IMAGE *shm_dmtt;
  float *dmtt;

  /* header string for logging message */
  char *header;

  /* script to communicate with cacao */
  char *flat;
  char *zero;
  char *saveflat;
  char *updateflat;
  char *set;

} tt_t;


/* Device handler operation functions */
extern const struct device_operations tt_ops;

/* Function prototypes */
int tt_init(tt_t *tt, const char *header);
int tt_free(tt_t *tt);
int tt_open(tt_t *tt);
int tt_close(tt_t *tt);
int tt_procconf(tt_t *tt, const char *subsec, int argc, const char **argv);
int tt_postconf(tt_t *tt);    
int tt_proccmd(client_t *client, tt_t *tt);
int tt_make_flat(tt_t *tt, int timersec, char *errstr);

#endif /* _TT_H */
