/* -------------------------------------------------------------------------
 * howfs.h -- Definitions for handling HOWFS server
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/05/13   Y. Ono        Initial version
 *    2019/09/20   Y. Ono        Add cashe
 * -------------------------------------------------------------------------
 */

#ifndef _HOWFS_H
#define _HOWFS_H

#include <sys/time.h>			/* for struct timeval */
#include <pthread.h>			/* for pthread_* */
#include "comm.h"			/* for comm_t */
#include "device.h"			/* for struct device_ops */
#include "server.h"			/* for client_t */

/* Buffer size or maximum length of string from/to controller */

enum {
  HOWFS_COMM_BUFSIZ = 1024,	/* buffer size for communication */
  HOWFS_CMDSTR_MAX = 256,	/* for sending command */
  HOWFS_ERRSTR_MAX = 256,	/* for error message */
};

/* Maximum number of status arguments */
#define HOWFS_STATARG_MAX	10000

/* Delimiter indicating end of command and response strings */
#define HOWFS_DELIM_IN	"\r"
#define HOWFS_DELIM_OUT	"\r\n"

/* Default header string for logging messages */
#define HOWFS_HEADER_DEFAULT	"howfs"

/* HOWFS server command */
#define HOWFS_CMD_LASH_CLOSE    "howfs lash close"
#define HOWFS_CMD_LASH_ST       "howfs lash st"
#define HOWFS_CMD_LAFW_ST       "howfs lafw st"
#define HOWFS_CMD_VMST          "vm st"

/* structure to store HOWFS info */
struct howfs_stat{
  int lash;
  char lafw[20];
  int vm;
  float freq;
  float volt;
  float phase;
};

/* Structure for handling controller and its devices */
typedef struct howfs {
    
  /* for communication with controller */
  comm_t comm;	/* data for communication */
    
  /* for message logging */
  char *header;	/* header string for logging message */
    
  /* cache */
  struct howfs_stat stat;
  pthread_rwlock_t cache_lock;       /* lock of cache */

} howfs_t;


/* Device handler operation functions */

extern const struct device_operations howfs_ops;

#ifdef __cplusplus
extern "C" {
#endif
    
  /* Function prototypes */
  int howfs_init(howfs_t *howfs, const char *header);
  int howfs_free(howfs_t *howfs);
  int howfs_connect(howfs_t *howfs);
  int howfs_disconnect(howfs_t *howfs);
  int howfs_connboot(howfs_t *howfs);
  int howfs_open(howfs_t *howfs);
  int howfs_close(howfs_t *howfs);
    
  int howfs_procconf(howfs_t *howfs, const char *subsec, int argc, const char **argv);
  int howfs_postconf(howfs_t *howfs);    
  int howfs_sendres(client_t *client, howfs_t *howfs, int ret, const char *errstr);
  int howfs_proccmd(client_t *client, howfs_t *howfs);
  int howfs_sendcmd_lock(howfs_t *howfs, const char *cmdstr, char *retstr, size_t size);
  int howfs_sendcmd(howfs_t *howfs, const char *cmdstr, char *retstr, size_t size);
  int howfs_getstat(howfs_t *howfs, struct howfs_stat *stat, char *errstr);
  int howfs_savestat(howfs_t *howfs, struct howfs_stat *stat);
  int howfs_lash_close(howfs_t *howfs, char *errstr);

#ifdef __cplusplus
}
#endif

#endif /* _HOWFS_H */
