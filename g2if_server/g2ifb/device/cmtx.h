/* -------------------------------------------------------------------------
 * cmtx.h -- Function for CMTX control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/09/24   Y. Ono        Initial version
 *
 * -------------------------------------------------------------------------
 */

#ifndef _CMTX_H
#define _CMTX_H

#include <sys/time.h>		/* for struct timeval */
#include <pthread.h>		/* for pthread_* */
#include "comm.h"		/* for comm_t */
#include "device.h"		/* for struct device_ops */
#include "poll.h"               /* for poll_t */
#include "server.h"		/* for client_t */
#include "conf.h"
#include "gain.h"

/* Buffer size or maximum length of string from/to cmtxler */
enum {
    CMTX_COMM_BUFSIZ = 1024,	/* buffer size for communication */
    CMTX_CMDSTR_MAX = 256,	/* for sending command */
    CMTX_ERRSTR_MAX = 256,	/* for error message */
};

/* Default header string for logging messages */
#define CMTX_HEADER_DEFAULT	"cmtx"

typedef struct cmtx{

  /* header string for logging message */
  char *header;

  /* script to communicate with cacao */
  char *ngs;
  char *lgs;

  gain_t *gain;

} cmtx_t;


/* Device handler operation functions */
extern const struct device_operations cmtx_ops;

/* Function prototypes */
int cmtx_init(cmtx_t *cmtx, const char *header);
int cmtx_free(cmtx_t *cmtx);
int cmtx_open(cmtx_t *cmtx);
int cmtx_close(cmtx_t *cmtx);
int cmtx_procconf(cmtx_t *cmtx, const char *subsec, int argc, const char **argv);
int cmtx_postconf(cmtx_t *cmtx);    
int cmtx_proccmd(client_t *client, cmtx_t *cmtx);

#endif /* _CMTX_H */
