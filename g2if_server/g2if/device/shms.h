/* -------------------------------------------------------------------------
 * shms.h -- Function for cacao SHM
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>
 *    2019/04/18   Y. Ono        Initial version (tested with dummy shm)
 *
 * -------------------------------------------------------------------------
 */

#ifndef _SHMS_H
#define _SHMS_H

#include <sys/time.h>		/* for struct timeval */
#include <pthread.h>		/* for pthread_* */
#include "comm.h"		/* for comm_t */
#include "device.h"		/* for struct device_ops */
#include "poll.h"               /* for poll_t */
#include "server.h"		/* for client_t */
#include "conf.h"
#include "ImageStreamIO/ImageStruct.h"
#include "ImageStreamIO/ImageStreamIO.h"

/* Buffer size or maximum length of string from/to shmler */
enum {
    SHMS_COMM_BUFSIZ = 1024,	/* buffer size for communication */
    SHMS_CMDSTR_MAX = 256,	/* for sending command */
    SHMS_ERRSTR_MAX = 256,	/* for error message */
};


/* String length for SHM name */
#define KEY_STR_MAX	100


/* Default header string for logging messages */
#define SHMS_HEADER_DEFAULT	"shms"

/* The number of shared memries for SHM */
#define SHMS_NUM_MAX 1000


/* cacao image structure */
struct cacao_shm {
  IMAGE image; /* Structure to hold the shared memory related variables */
  char key[KEY_STR_MAX];
};


typedef struct shms{

  /* image stream io to access cacao shm */
  struct cacao_shm shm[SHMS_NUM_MAX];
  int shm_num;

  /* header string for logging message */
  char *header;

} shms_t;


/* Device handler operation functions */
extern const struct device_operations shms_ops;

/* Function prototypes */
int shms_init(shms_t *shms, const char *header);
int shms_free(shms_t *shms);
int shms_open(shms_t *shms);
int shms_close(shms_t *shms);
int shms_procconf(shms_t *shms, const char *subsec, int argc, const char **argv);
int shms_postconf(shms_t *shms);
int shms_proccmd(client_t *client, shms_t *shms);

int shms_search_comp(const void *key, const void *shm);
int shms_write_float(shms_t *shms, const char *key, const float *value, const int num, char *errstr);
int shms_read_float(shms_t *shms, const char *key, float *value, const int num, char *errstr);
int shms_write_uint32(shms_t *shms, const char *key, const uint32_t *value, const int num, char *errstr);
int shms_read_uint32(shms_t *shms, const char *key, uint32_t *value, const int num, char *errstr);

/* Keyword to access sheard memories */
// #define KEY_TTG_GAIN        "ttg"                // SHM Keyword for TTG gain                     // USED in gain_cmd.c, gain.c
#define KEY_HTT_GAIN        "Httg"               // SHM Keyword for HTT gain                     // USED in cmtx_cmd.c, gain_cmd.c, gain.c
#define KEY_HDF_GAIN        "Hdfg"               // SHM Keyword for HDF gain                     // USED in cmtx_cmd.c, gain_cmd.c, gain.c
#define KEY_LTT_GAIN        "LO_tt_gain"         // SHM Keyword for LTT gain                     // USED in gain_cmd.c, gain.c
#define KEY_LDF_GAIN        "LO_defocus_gain"    // SHM Keyword for LDF gain                     // USED in gain_cmd.c, gain.c
#define KEY_WTT_GAIN        "wttg"               // SHM Keyword for WTT gain                     // USED in gain_cmd.c, gain.c
#define KEY_ADF_GAIN        "ADF_gain"           // SHM Keyword for ADF gain                     // USED in gain_cmd.c, gain.c, adf_cmd.c
#define KEY_TTM_TT          "tt_value_float"     // SHM Keyword for Tip/Tilt of TTM              // USED in tt.c, status.c
#define KEY_WTT_TT          "wtt_value_float"    // SHM Keyword for Tip/Tilt of WTTM             // USED in status.c
#define KEY_APD_COUNT       "apd"                // SHM Keyword for APD count                    // USED in status.c
#define KEY_APD_COUNT2      "apd"                 // SHM Keyword for APD count (for APD safety)   // USED in apdsafe.c
#define KEY_ADFGAIN_X_DF    "ADFg"               // SHM Keyword for ADF_gain x defocus           // USED in adf_cmd.c
#define KEY_DM_VOLT         "bim188_tele"        // SHM Keyword for dm voltage                   // USED in dm.c, status.c
#define KEY_CURV            "curv_1kdouble"      // SHM Keyword for curvature                    // USED in status.c, gain.c, gain_cmd.c+292?
#define KEY_LO_TT           "LO_tt"              // SHM Keyword for LOWFS tip/tilt               // USED in status.c
#define KEY_LO_DF           "LO_defocus"         // SHM Keyword for LOWFS defocus                // USED in status.c
#define KEY_BIMWRITE        "bim188_float"       // SHM Keyword for dm01disp                     // USED in dm.c


#endif /* _SHM_H */
