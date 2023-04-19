/* -------------------------------------------------------------------------
 * entshut.h -- Definitions for handling ENTSHUT server
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/05/13   Y. Ono        Initial version
 *
 * -------------------------------------------------------------------------
 */

#ifndef _ENTSHUT_H
#define _ENTSHUT_H

#include <sys/time.h>			/* for struct timeval */
#include <pthread.h>			/* for pthread_* */
#include "comm.h"			/* for comm_t */
#include "device.h"			/* for struct device_ops */
#include "server.h"			/* for client_t */

/* Buffer size or maximum length of string from/to controller */

enum {
  ENTSHUT_COMM_BUFSIZ = 1024,	/* buffer size for communication */
  ENTSHUT_CMDSTR_MAX = 256,	/* for sending command */
  ENTSHUT_ERRSTR_MAX = 256,	/* for error message */
};

/* Delimiter indicating end of command and response strings */

#define ENTSHUT_DELIM_IN	"\r"
#define ENTSHUT_DELIM_OUT	"\r\n"

/* Default header string for logging messages */
#define ENTSHUT_HEADER_DEFAULT	"entshut"

/* ENTSHUT server command */
#define ENTSHUT_CMD_ENTSHUT_CLOSE    "entshut close"
#define ENTSHUT_CMD_ENTSHUT_ST       "entshut st"

/* Structure for handling controller and its devices */
typedef struct entshut {
    
  /* for communication with controller */
  comm_t comm;	/* data for communication */
    
  /* for message logging */
  char *header;	/* header string for logging message */
    
} entshut_t;

/* Device handler operation functions */

extern const struct device_operations entshut_ops;

#ifdef __cplusplus
extern "C" {
#endif
    
  /* Function prototypes */
    
  int entshut_init(entshut_t *entshut, const char *header);
  int entshut_free(entshut_t *entshut);
  int entshut_connect(entshut_t *entshut);
  int entshut_disconnect(entshut_t *entshut);
  int entshut_connboot(entshut_t *entshut);
  int entshut_open(entshut_t *entshut);
  int entshut_close(entshut_t *entshut);
    
  int entshut_procconf(entshut_t *entshut, const char *subsec, int argc, const char **argv);
  int entshut_postconf(entshut_t *entshut);    
  int entshut_sendres(client_t *client, entshut_t *entshut, int ret, const char *errstr);
  int entshut_proccmd(client_t *client, entshut_t *entshut);
  int entshut_sendcmd_lock(entshut_t *entshut, const char *cmdstr, char *retstr, size_t size);
  int entshut_sendcmd(entshut_t *entshut, const char *cmdstr, char *retstr, size_t size);

#ifdef __cplusplus
}
#endif

#endif /* _ENTSHUT_H */
