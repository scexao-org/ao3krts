/* -------------------------------------------------------------------------
 * obcp.h -- Definitions for handling OBCP server
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/18   Y. Ono        Initial version
 *
 * -------------------------------------------------------------------------
 */

#ifndef _OBCP_H
#define _OBCP_H

#include <sys/time.h>			/* for struct timeval */
#include <pthread.h>			/* for pthread_* */
#include "comm.h"			/* for comm_t */
#include "device.h"			/* for struct device_ops */
#include "server.h"			/* for client_t */

/* Buffer size or maximum length of string from/to controller */

enum {
  OBCP_COMM_BUFSIZ = 1024,	/* buffer size for communication */
  OBCP_CMDSTR_MAX = 256,	/* for sending command */
  OBCP_ERRSTR_MAX = 256,	/* for error message */
};

/* Delimiter indicating end of command and response strings */

#define OBCP_DELIM_IN	"\r"
#define OBCP_DELIM_OUT	"\r\n"

/* Default header string for logging messages */

#define OBCP_HEADER_DEFAULT	"obcp"

/* Structure for handling controller and its devices */
typedef struct obcp {
    
  /* for communication with controller */
  comm_t comm;	/* data for communication */
    
  /* for message logging */
  char *header;	/* header string for logging message */
    
} obcp_t;

/* Device handler operation functions */

extern const struct device_operations obcp_ops;

#ifdef __cplusplus
extern "C" {
#endif
    
  /* Function prototypes */
    
  int obcp_init(obcp_t *obcp, const char *header);
  int obcp_free(obcp_t *obcp);
  int obcp_connect(obcp_t *obcp);
  int obcp_disconnect(obcp_t *obcp);
  int obcp_connboot(obcp_t *obcp);
  int obcp_open(obcp_t *obcp);
  int obcp_close(obcp_t *obcp);
    
  int obcp_procconf(obcp_t *obcp, const char *subsec, int argc, const char **argv);
  int obcp_postconf(obcp_t *obcp);    
  int obcp_sendres(client_t *client, obcp_t *obcp, int ret, const char *errstr);
  int obcp_proccmd(client_t *client, obcp_t *obcp);
  int obcp_sendcmd_lock(obcp_t *obcp, const char *cmdstr, char *retstr, size_t size);
  int obcp_sendcmd(obcp_t *obcp, const char *cmdstr, char *retstr, size_t size);

#ifdef __cplusplus
}
#endif

#endif /* _OBCP_H */
