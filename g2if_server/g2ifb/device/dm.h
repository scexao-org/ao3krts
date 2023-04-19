/* -------------------------------------------------------------------------
 * dm.h -- Function for DM control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/06/17   Y. Ono        Initial version
 *    2019/09/20   Y. Ono        Add saveflat
 *    2019/09/26   Y. Ono        Add cashe for updating DM flat
 * -------------------------------------------------------------------------
 */

#ifndef _DM_H
#define _DM_H

#include <sys/time.h>		/* for struct timeval */
#include <pthread.h>		/* for pthread_* */
#include "comm.h"		/* for comm_t */
#include "device.h"		/* for struct device_ops */
#include "poll.h"               /* for poll_t */
#include "server.h"		/* for client_t */
#include "conf.h"
#include "shms.h"               /* for shms_t */
#include "tool.h"		/* for timer */

/* Buffer size or maximum length of string from/to dmler */
enum {
    DM_COMM_BUFSIZ = 1024,	/* buffer size for communication */
    DM_CMDSTR_MAX = 256,	/* for sending command */
    DM_ERRSTR_MAX = 256,	/* for error message */
};

/* Default header string for logging messages */
#define DM_HEADER_DEFAULT	"dm"

#define DM_MIN_MAKEFLAT_SEC       1
#define DM_MAX_MAKEFLAT_SEC     300       
#define DM_FLATFILE_NAME        "!/home/rts/RTS_2019/conf/saved_dmflats/dm_flat_temp.fits"


typedef struct dm{

  shms_t *shms;
  IMAGE *shm_dmvolt;
  float *dmvolt;

  /* header string for logging message */
  char *header;

  /* script to communicate with cacao */
  char *flat;
  char *zero;
  char *saveflat;
  char *updateflat;

} dm_t;


/* Device handler operation functions */
extern const struct device_operations dm_ops;

/* Function prototypes */
int dm_init(dm_t *dm, const char *header);
int dm_free(dm_t *dm);
int dm_open(dm_t *dm);
int dm_close(dm_t *dm);
int dm_procconf(dm_t *dm, const char *subsec, int argc, const char **argv);
int dm_postconf(dm_t *dm);    
int dm_proccmd(client_t *client, dm_t *dm);
int dm_make_flat(dm_t *dm, int timersec, char *errstr);

#endif /* _DM_H */
