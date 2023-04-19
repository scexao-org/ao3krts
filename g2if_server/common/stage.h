/*
 * stage.h -- Definitions for functions to handle linear and roation stages
 *            and shutters on stepper motor controllers
 *
 * 2008/11/19 Makoto WATANABE -- Initial version
 */

#ifndef _STAGE_H
#define _STAGE_H

#include <stdint.h>				/* for int32_t */
#include "server.h"				/* for client_t */
#include "alias.h"				/* for alias_t */

/* Maximum string lengths for device name etc. */

enum {
	STAGE_DEVID_MAX 	= 8,	/* id name */
	STAGE_DEVNAME_MAX	= 15,	/* label for st command */
	STAGE_DEVDESC_MAX	= 60,	/* description for help command */
	STAGE_POSNAME_MAX	= 12,	/* key string of position */
	STAGE_UNITNAME_MAX	= 5,	/* name of unit of movement */
	STAGE_UNITFMT_MAX	= 8,	/* format string for position */
};

/* Type of stages */

enum {
	STAGE_TYPE_LINEAR		= 1,	/* linear stage */
	STAGE_TYPE_ROTATION		= 2,	/* rotation stage */
	STAGE_TYPE_SHUTTER		= 3,	/* solenoid shutter */
};

enum {
	STAGE_TYPE_MIN = STAGE_TYPE_LINEAR,
	STAGE_TYPE_MAX = STAGE_TYPE_SHUTTER,
};

/* Default format string */

#define STAGE_UNITFMT_DEFAULT	"%.3f"		/* stage position */

/* Structure for handling named positions */

typedef struct stage_posname {
	char key[STAGE_POSNAME_MAX + 1];	/* key string of position */
	int32_t val;						/* position value in stage unit */
} stage_posname_t;

/* Structure to store parameters of a device */

typedef struct stage {
	char id[STAGE_DEVID_MAX + 1];
	char name[STAGE_DEVNAME_MAX + 1];	/* short description for labeling */
	char desc[STAGE_DEVDESC_MAX + 1];	/* long description for help cmd */
	int axis;							/* axis number on controller */
	int type;							/* type of device */
	char unitname[STAGE_UNITNAME_MAX + 1];	/* name of unit of movement */
	char unitfmt[STAGE_UNITFMT_MAX + 1];	/* format string for printf() */
	double convfac;						/* factor of conversion for step to stage unit */
	double convoff;						/* offset of conversion for step to stage unit */
	int homeseq;						/* sequence program number for homeing */
	int32_t posbase;					/* base position in step */
	int num_posnames;					/* number of named positions */
	stage_posname_t *posnames;			/* pointer to named positions */
	int32_t posmax;						/* maximum position in stage unit */
	int32_t posmin;						/* minimum position in stage unit */
	int32_t posrot;						/* microstep for one turn */
	int32_t velmin;						/* minimum speed in microstep/s */
	int32_t velmax;						/* maximum speed in microstep/s */
	int32_t backlash;	/* backward motion length for basklash compensation */
	int lmtuse;							/* flag for use of limit sensors */
	int lmtpol;							/* polarity of limit sensors */
} stage_t;

#define DIR(x)		((x) ? "+" : "-")

#ifdef __cplusplus
extern "C" {
#endif

/* Function prototypes */

int stage_setpar_posname(int argc, const char **argv, stage_t *dev,
	int32_t min, int32_t max);
int stage_procconf(stage_t *dev, int argc, const char **argv, int axis_min,
	int axis_max, int type_min, int type_max, int seq_min, int seq_max,
	int32_t pos_min, int32_t pos_max, int32_t vel_min, int32_t vel_max);
int stage_procconf_post(stage_t *devs, int num_devs);
int stage_printconf(stage_t *devs, int num_devs, const char *header);

stage_posname_t *stage_getposnamebyname(stage_t *dev, const char *name);
stage_posname_t *stage_getposnamebypos(stage_t *dev, int32_t pos);
double stage_step2unit(const stage_t *dev, int32_t step);
int32_t stage_unit2step(const stage_t *dev, double unit);

int stage_chkrangepos(client_t *client, stage_t *dev, int32_t pos,
	int report_in_unit);
int stage_chkrangevel(client_t *client, stage_t *dev, int32_t vel,
	int report_in_unit);

int stage_stagecmd_help(client_t *client, stage_t *dev);
int stage_shutcmd_help(client_t *client, stage_t *dev);
int stage_allcmd_help(client_t *client);

#ifdef __cplusplus
}
#endif

#endif /* _STAGE_H */
