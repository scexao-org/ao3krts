/* -------------------------------------------------------------------------
 * wtt.h -- Function for WTT control
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/06/17   Y. Ono        Initial version
 *    2019/09/20   Y. Ono        Add saveflat
 * -------------------------------------------------------------------------
 */

#ifndef _WTT_H
#define _WTT_H

#include <sys/time.h>		/* for struct timeval */
#include <pthread.h>		/* for pthread_* */
#include "comm.h"		/* for comm_t */
#include "device.h"		/* for struct device_ops */
#include "poll.h"               /* for poll_t */
#include "server.h"		/* for client_t */
#include "conf.h"

/* Buffer size or maximum length of string from/to wttler */
enum {
    WTT_COMM_BUFSIZ = 1024,	/* buffer size for communication */
    WTT_CMDSTR_MAX = 256,	/* for sending command */
    WTT_ERRSTR_MAX = 256,	/* for error message */
};

/* Default header string for logging messages */
#define WTT_HEADER_DEFAULT	"wtt"
#define VOLT_TO_DAC             819.1

typedef struct wtt{

  /* header string for logging message */
  char *header;

  /* script to communicate with cacao */
  char *flat;
  char *zero;
  char *saveflat;
  char *set;

} wtt_t;


/* Device handler operation functions */
extern const struct device_operations wtt_ops;

/* Function prototypes */
int wtt_init(wtt_t *wtt, const char *header);
int wtt_free(wtt_t *wtt);
int wtt_open(wtt_t *wtt);
int wtt_close(wtt_t *wtt);
int wtt_procconf(wtt_t *wtt, const char *subsec, int argc, const char **argv);
int wtt_postconf(wtt_t *wtt);    
int wtt_proccmd(client_t *client, wtt_t *wtt);

#endif /* _WTT_H */
