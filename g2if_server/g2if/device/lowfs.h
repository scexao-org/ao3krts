/* -------------------------------------------------------------------------
 * lowfs.h -- Definitions for handling LOWFS server
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/05/13   Y. Ono        Initial version
 *    2019/09/20   Y. Ono        Add cashe
 * -------------------------------------------------------------------------
 */

#ifndef _LOWFS_H
#define _LOWFS_H

#include <sys/time.h>			/* for struct timeval */
#include <pthread.h>			/* for pthread_* */
#include "comm.h"			/* for comm_t */
#include "device.h"			/* for struct device_ops */
#include "server.h"			/* for client_t */

/* Buffer size or maximum length of string from/to controller */

enum {
  LOWFS_COMM_BUFSIZ = 1024,	/* buffer size for communication */
  LOWFS_CMDSTR_MAX = 256,	/* for sending command */
  LOWFS_ERRSTR_MAX = 256,	/* for error message */
};

/* Maximum number of status arguments */
#define LOWFS_STATARG_MAX	10000

/* Delimiter indicating end of command and response strings */
#define LOWFS_DELIM_IN	"\r"
#define LOWFS_DELIM_OUT	"\r\n"

/* Default header string for logging messages */
#define LOWFS_HEADER_DEFAULT	"lowfs"

/* LOWFS server command */
#define LOWFS_CMD_LASH_CLOSE    "lowfs lash close"
#define LOWFS_CMD_LASH_ST       "lowfs lash st"
#define LOWFS_CMD_LAFW_ST       "lowfs lafw st"

/* structure to store LOWFS info */
struct lowfs_stat{
  int lash;
  char lafw[20];
};

/* Structure for handling controller and its devices */
typedef struct lowfs {
    
  /* for communication with controller */
  comm_t comm;	/* data for communication */
    
  /* for message logging */
  char *header;	/* header string for logging message */
    
  /* cache */
  struct lowfs_stat stat;
  pthread_rwlock_t cache_lock;       /* lock of cache */

} lowfs_t;


/* Device handler operation functions */

extern const struct device_operations lowfs_ops;

#ifdef __cplusplus
extern "C" {
#endif
    
  /* Function prototypes */
    
  int lowfs_init(lowfs_t *lowfs, const char *header);
  int lowfs_free(lowfs_t *lowfs);
  int lowfs_connect(lowfs_t *lowfs);
  int lowfs_disconnect(lowfs_t *lowfs);
  int lowfs_connboot(lowfs_t *lowfs);
  int lowfs_open(lowfs_t *lowfs);
  int lowfs_close(lowfs_t *lowfs);
    
  int lowfs_procconf(lowfs_t *lowfs, const char *subsec, int argc, const char **argv);
  int lowfs_postconf(lowfs_t *lowfs);    
  int lowfs_sendres(client_t *client, lowfs_t *lowfs, int ret, const char *errstr);
  int lowfs_proccmd(client_t *client, lowfs_t *lowfs);
  int lowfs_sendcmd_lock(lowfs_t *lowfs, const char *cmdstr, char *retstr, size_t size);
  int lowfs_sendcmd(lowfs_t *lowfs, const char *cmdstr, char *retstr, size_t size);
  int lowfs_getstat(lowfs_t *lowfs, struct lowfs_stat *stat, char *errstr);
  int lowfs_savestat(lowfs_t *lowfs, struct lowfs_stat *stat);
  int lowfs_lash_close(lowfs_t *lowfs, char *errstr);

#ifdef __cplusplus
}
#endif

#endif /* _LOWFS_H */
