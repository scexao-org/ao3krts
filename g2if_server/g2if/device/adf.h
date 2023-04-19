/* -------------------------------------------------------------------------
 * adf.h -- Function for ADF control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/18   Y. Ono        Initial version (tested with dummy shm)
 *
 * -------------------------------------------------------------------------
 */

#ifndef _ADF_H
#define _ADF_H

#include <sys/time.h>		/* for struct timeval */
#include <pthread.h>		/* for pthread_* */
#include "comm.h"		/* for comm_t */
#include "device.h"		/* for struct device_ops */
#include "poll.h"               /* for poll_t */
#include "server.h"		/* for client_t */
#include "conf.h"
#include "shms.h"               /* for shms_t */
#include "gain.h"               /* for shms_t */

/* Buffer size or maximum length of string from/to adfler */
enum {
    ADF_COMM_BUFSIZ = 1024,	/* buffer size for communication */
    ADF_CMDSTR_MAX = 256,	/* for sending command */
    ADF_ERRSTR_MAX = 256,	/* for error message */
};

/* Default header string for logging messages */
#define ADF_HEADER_DEFAULT	"adf"

typedef struct adf{

  /* shared memory */
  shms_t *shms;

  /* header string for logging message */
  char *header;

  gain_t *gain;

} adf_t;


/* Device handler operation functions */
extern const struct device_operations adf_ops;

/* Function prototypes */
int adf_init(adf_t *adf, const char *header);
int adf_free(adf_t *adf);
int adf_open(adf_t *adf);
int adf_close(adf_t *adf);
int adf_procconf(adf_t *adf, const char *subsec, int argc, const char **argv);
int adf_postconf(adf_t *adf);    
int adf_proccmd(client_t *client, adf_t *adf);


#endif /* _ADF_H */
