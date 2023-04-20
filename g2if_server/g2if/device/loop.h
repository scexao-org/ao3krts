/* -------------------------------------------------------------------------
 * loop.h -- Function for LOOP control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/18   Y. Ono        Initial version (tested with dummy shm)
 *    2019/09/20   Y. Ono        Add cashe
 *    2019/09/26   Y. Ono        Add fifo for LOOP status
 * -------------------------------------------------------------------------
 */

#ifndef _LOOP_H
#define _LOOP_H

#include <sys/time.h>		/* for struct timeval */
#include <pthread.h>		/* for pthread_* */
#include "comm.h"		/* for comm_t */
#include "device.h"		/* for struct device_ops */
#include "poll.h"               /* for poll_t */
#include "server.h"		/* for client_t */
#include "conf.h"
#include "fifo_func.h"		/* for fifo_t */

/* Buffer size or maximum length of string from/to loopler */
enum {
    LOOP_COMM_BUFSIZ = 1024,	/* buffer size for communication */
    LOOP_CMDSTR_MAX = 256,	/* for sending command */
    LOOP_ERRSTR_MAX = 256,	/* for error message */
};

/* Default header string for logging messages */
#define LOOP_HEADER_DEFAULT	"loop"

/* timeout period for loop on/off commands */
#define LOOP_TIMEOUT      2

/* FIFO INFO for LOOP */
#define LOOP_FIFO_NAME      "/milk/shm/g2if_loop.fifo"
#define LOOP_FIFO_ONOFF     "mfilt-3.loopON" // 1 = hardware
#define LOOP_STATARG_MAX    100

/* structure to store info */
struct loop_stat{
  int onoff;
};

typedef struct loop{

  /* header string for logging message */
  char *header;

  /* cashe */
  struct loop_stat stat;
  pthread_rwlock_t cache_lock;       /* lock of cache */

  /* fifo */
  struct fifo_t fifo;

  /* mutex lock for loop control */
  pthread_mutex_t lock;

} loop_t;

/* Device handler operation functions */
extern const struct device_operations loop_ops;

/* Function prototypes */
int loop_init(loop_t *loop, const char *header);
int loop_free(loop_t *loop);
int loop_open(loop_t *loop);
int loop_close(loop_t *loop);
int loop_procconf(loop_t *loop, const char *subsec, int argc, const char **argv);
int loop_postconf(loop_t *loop);    
int loop_proccmd(client_t *client, loop_t *loop);
int loop_getstat(loop_t *loop, struct loop_stat *stat);
int loop_savestat(loop_t *loop, struct loop_stat *stat);

#endif /* _LOOP_H */
