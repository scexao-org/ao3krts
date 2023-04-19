/*
 * stage.c -- Functions to handle linear and rotation stage, and shutters
 *            on stepper motor controllers
 *
 * 2008/11/19 Makoto WATANABE -- Initial version
 */

#include <stdio.h>				/* for snprintf() */
#include <stdlib.h>				/* for realloc() */
#include <stdint.h>				/* for int32_t */
#include <string.h>				/* for strncat(), strcmp(), strcasecmp() */
#include <math.h>				/* for round() */
#include <errno.h>				/* for errno */
#include "log.h"				/* for error(), info(), debug() */
#include "alias.h"				/* for alias_t, alias_*() */
#include "conf.h"				/* for setpar_int() and etc */
#include "stage.h"				/* for stage_t */
#include "server.h"				/* for client_t, sendres(), sendres_*() */
#include "stringx.h"			/* for strtolower() */

int stage_setpar_posname(int argc, const char **argv, stage_t *dev,
	int32_t min, int32_t max)
{
	stage_posname_t *posname;

	if (argc < 3) {
		setpar_missing_arg(argv[0]);
		return -1;
	}

	/* Reallocate memory */
	posname = realloc(dev->posnames,
		sizeof(stage_posname_t) * (dev->num_posnames + 1));
	if (posname == NULL) {
		error_num(errno, "cannot allocate memory for stage_posname_t");
		return -1;
	}
	dev->num_posnames++;
	dev->posnames = posname;

	posname = &(dev->posnames[dev->num_posnames - 1]);
	if (setpar_strcpy(argc, argv, 1, posname->key, sizeof(posname->key)) < 0
		|| setpar_int32(argc, argv, 2, &(posname->val), min, max) < 0) {
		return -1;
	}
	return 1;
}

/*
 * Process a configuration parameter of a device
 */
int stage_procconf(stage_t *dev, int argc, const char **argv, int axis_min,
	int axis_max, int type_min, int type_max, int seq_min, int seq_max,
	int32_t pos_min, int32_t pos_max, int32_t vel_min, int32_t vel_max)
{
	const char *key = argv[0];

	if (strcmp(key, "name") == 0) {				/* name of device */
		return setpar_strjoin(argc, argv, dev->name, sizeof(dev->name));
	} else if (strcmp(key, "desc") == 0) {		/* description of device */
		return setpar_strjoin(argc, argv, dev->desc, sizeof(dev->desc));
	} else if (strcmp(key, "axis") == 0) {		/* axis number */
		return setpar_int(argc, argv, 1, &(dev->axis), axis_min, axis_max);
	} else if (strcmp(key, "type") == 0) {		/* type of device */
		return setpar_int(argc, argv, 1, &(dev->type), type_min, type_max);
	} else if (strcmp(key, "unitname") == 0) {	/* name of unit of position */
		return setpar_strcpy(argc, argv, 1, dev->unitname,
			sizeof(dev->unitname));
	} else if (strcmp(key, "unitfmt") == 0) {	/* format of unit for printf() */
		return setpar_strcpy(argc, argv, 1, dev->unitfmt, sizeof(dev->unitfmt));
	} else if (strcmp(key, "convfac") == 0) {	/* factor of conversion */
		return setpar_dbl(argc, argv, 1, &(dev->convfac), 0, 0);
	} else if (strcmp(key, "convoff") == 0) {	/* offset of conversion */
		return setpar_dbl(argc, argv, 1, &(dev->convoff), 0, 0);
	} else if (strcmp(key, "homeseq") == 0) {	/* program # for homing */
		return setpar_int(argc, argv, 1, &(dev->homeseq), seq_min, seq_max);
	} else if (strcmp(key, "posbase") == 0) {	/* base position in microstep */
		return setpar_int32(argc, argv, 1, &(dev->posbase), pos_min, pos_max);
	} else if (strcmp(argv[0], "posname") == 0) {	/* named positions */
		return stage_setpar_posname(argc, argv, dev, pos_min, pos_max);
	} else if (strcmp(key, "posmin") == 0) {	/* minimum position */
		return setpar_int32(argc, argv, 1, &(dev->posmin), pos_min, pos_max);
	} else if (strcmp(key, "posmax") == 0) {	/* maximum position */
		return setpar_int32(argc, argv, 1, &(dev->posmax), pos_min, pos_max);
	} else if (strcmp(key, "posrot") == 0) {	//* microsteps for one turn */
		return setpar_int32(argc, argv, 1, &(dev->posrot), 0, pos_max);
	} else if (strcmp(key, "velmax") == 0) {	/* maximum velocity */
		return setpar_int32(argc, argv, 1, &(dev->velmax), vel_min, vel_max);
	} else if (strcmp(key, "backlash") == 0) {	/* backlash */
		return setpar_int32(argc, argv, 1, &(dev->backlash), 0, pos_max);
	} else if (strcmp(key, "lmtuse") == 0) {	/* lmtuse flag */
		return setpar_int(argc, argv, 1, &(dev->lmtuse), 0, 1);
	} else if (strcmp(key, "lmtpol") == 0) {	/* sensor polarity */
		return setpar_int(argc, argv, 1, &(dev->lmtpol), 0, 1);
	}

	setpar_unknown_par(key);
	return 0;
}

/*
 * Print all configuration parameters
 */
int stage_printconf(stage_t *devs, int num_devs, const char *header)
{
	int i, j;
	stage_t *dev;
	stage_posname_t *posname;

	info("%s: num_devs = %d", header, num_devs);
	for (i = 1; i <= num_devs; i++) {
		dev = &(devs[i - 1]);
		info("%s: devs[%d].id = \"%s\"", header, i, dev->id);
		info("%s: devs[%d].name = \"%s\"", header, i, dev->name);
		info("%s: devs[%d].desc = \"%s\"", header, i, dev->desc);
		info("%s: devs[%d].axis = %d", header, i, dev->axis);
		info("%s: devs[%d].unitname = \"%s\"", header, i, dev->unitname);
		info("%s: devs[%d].unitfmt = \"%s\"", header, i, dev->unitfmt);
		info("%s: devs[%d].convfac = %g", header, i, dev->convfac);
		info("%s: devs[%d].convoff = %g", header, i, dev->convoff);
		info("%s: devs[%d].homeseq = %d", header, i, dev->homeseq);
		info("%s: devs[%d].posbase = %d", header, i, dev->posbase);
		info("%s: devs[%d].num_posnames = %d", header, i, dev->num_posnames);
		for (j = 1; j <= dev->num_posnames; j++) {
			posname = &(dev->posnames[j - 1]);
			info("%s: devs[%d].posnames[%d].key = \"%s\"", header, i, j, posname->key);
			info("%s: devs[%d].posnames[%d].val = %d", header, i, j, posname->val);
		}
		info("%s: devs[%d].posmin = %d", header, i, dev->posmin);
		info("%s: devs[%d].posmax = %d", header, i, dev->posmax);
		info("%s: devs[%d].posrot = %d", header, i, dev->posrot);
		info("%s: devs[%d].valmin = %d", header, i, dev->velmin);
		info("%s: devs[%d].valmax = %d", header, i, dev->velmax);
		info("%s: devs[%d].backlash = %d", header, i, dev->backlash);
		info("%s: devs[%d].lmtuse = %d", header, i, dev->lmtuse);
		info("%s: devs[%d].lmtpol = %d", header, i, dev->lmtpol);
	}
	return 0;
}

/*
 * Post process after reading configuration
 */
int stage_procconf_post(stage_t *devs, int num_devs)
{
	int i;
	stage_t *dev;

	for (i = 0; i < num_devs; i++) {

		dev = &(devs[i]);
		if (dev->name[0] == '\0') {
			snprintf(dev->name, sizeof(dev->name), "Axis %d", dev->axis);
		}
		if (dev->desc[0] == '\0') {
			snprintf(dev->desc, sizeof(dev->desc), "Axis %d", dev->axis);
		}
		if (dev->unitfmt[0] == '\0') {
			strncat(dev->unitfmt, STAGE_UNITFMT_DEFAULT,
				sizeof(dev->unitfmt) - 1);
		}
	}

	return 0;
}

/*
 * Get a named position by name (if not found, return NULL pointer)
 */
stage_posname_t *stage_getposnamebyname(stage_t *dev, const char *name)
{
	int i;
	stage_posname_t *posname, *posname_found;

	posname_found = NULL;
	for (i = 0; i < dev->num_posnames; i++) {
		posname = &(dev->posnames[i]);
		if (strcasecmp(posname->key, name) == 0) {
			posname_found = posname;
			break;
		}
	}

	return posname_found;
}

/*
 * Get a named position by position (if not found, return NULL pointer)
 */
stage_posname_t *stage_getposnamebypos(stage_t *dev, int32_t pos)
{
	int i;
	stage_posname_t *posname, *posname_found;

	posname_found = NULL;
	for (i = 0; i < dev->num_posnames; i++) {
		posname = &(dev->posnames[i]);
		if (posname->val == pos) {
			posname_found = posname;
			break;
		}
	}

	return posname_found;
}

/*
 * Convert unit of position value from microstep to stage unit
 */
double stage_step2unit(const stage_t *dev, int32_t step)
{
	return step * dev->convfac + dev->convoff;
}

/*
 * Convert unit of position value from stage unit to microstep
 */
int32_t stage_unit2step(const stage_t *dev, double unit)
{
	double s;

	s = (unit - dev->convoff) / dev->convfac;
	if (!isfinite(s)) {
		error("stage: too small conversion factor of unit (%g) for \"%s\"",
		dev->convfac, dev->id);
	}
	s = round(s);

	return s;
}

/*
 * Check range of motion
 */
int stage_chkrangepos(client_t *client, stage_t *dev, int32_t pos,
	int report_in_unit)
{
	int32_t min, max;
	char *unitfmt, minstr[32], maxstr[32];

	/* Get device information */
	min = dev->posmin;
	max = dev->posmax;

	/* Check if target is within range of motion */
	if (pos < min || pos > max) {
		if (report_in_unit) {
			unitfmt = dev->unitfmt;
			snprintf(minstr, sizeof(minstr), unitfmt, stage_step2unit(dev, min));
			snprintf(maxstr, sizeof(maxstr), unitfmt, stage_step2unit(dev, max));
			sendres(client,
				RES_HEAD_ERR"out of range of motion (must be between %s and %s %s)\n",
				minstr, maxstr, dev->unitname);
		} else {
			sendres(client,
				RES_HEAD_ERR"out of range of motion (must be within %d - %d microstep)\n",
				min, max);
		}
		return -1;
	}

	return 0;
}

/*
 * Check range of velocity
 */
int stage_chkrangevel(client_t *client, stage_t *dev, int32_t vel,
	int report_in_unit)
{
	int32_t min, max;
	char *unitfmt, minstr[32], maxstr[32];

	/* Get device information */
	min = dev->velmin;
	max = dev->velmax;

	/* Check if target is within range of velocity */
	if (vel < min || vel > max) {
		if (report_in_unit) {
			unitfmt = dev->unitfmt;
			snprintf(minstr, sizeof(minstr), unitfmt, stage_step2unit(dev, min));
			snprintf(maxstr, sizeof(maxstr), unitfmt, stage_step2unit(dev, max));
			sendres(client,
				RES_HEAD_ERR"out of range of velocity (must be between %s and %s %s/s)\n",
				minstr, maxstr, dev->unitname);
		} else {
			sendres(client,
				RES_HEAD_ERR"out of range of velocity (must be within %d - %d microstep/s)\n",
				min, max);
		}
		return -1;
	}

	return 0;
}

/*
 * Process stage "help" command
 */
int stage_stagecmd_help(client_t *client, stage_t *dev)
{
	int i;
	stage_posname_t *posname;
	char *grp, cmd[STAGE_POSNAME_MAX + 1], desc[80];

	grp = getargv(client, 0);

	sendres(client, "%s Control\n", dev->desc);
	sendres(client, "Usage: %s %s <command> [<argument>]\n", grp, dev->id);
	sendres_hsect(client, "commands and arguments");
	sendres_hitem(client, "home", "do homing");
	sendres_hitem(client, "init", "do homing and move base position");
	for (i = 0; i < dev->num_posnames; i++) {
		posname = &(dev->posnames[i]);
		cmd[0] = '\0';
		strncat(cmd, posname->key, sizeof(cmd) - 1);
		strtolower(cmd);
		snprintf(desc, sizeof(desc), "move to \"%s\" position", posname->key);
		sendres_hitem(client, cmd, desc);
	}
	snprintf(desc, sizeof(desc), "move to X in %s", dev->unitname);
	sendres_hitem(client, "ma X", desc);
	snprintf(desc, sizeof(desc), "move by X in %s", dev->unitname);
	sendres_hitem(client, "mr X", desc);
	sendres_hitem(client, "mas X", "move to X in microstep");
	sendres_hitem(client, "mrs X", "move by X in microstep");
	sendres_hitem(client, "run [+|-]", "move endless into +/- direction");
	sendres_hitem(client, "stop", "stop motion");
	snprintf(desc, sizeof(desc), "set velocity to X in %s/s", dev->unitname);
	sendres_hitem(client, "vel X", desc);
	sendres_hitem(client, "vels X", "set velocity to X in microstep/s");
	snprintf(desc, sizeof(desc), "show current position in %s", dev->unitname);
	sendres_hitem(client, "pos", desc);
	sendres_hitem(client, "st [all]", "show status (using cache)");
	sendres_hitem(client, "stu [all]", "show status (not using cache)");
	sendres_hitem(client, "help", "show help message");

	return 0;
}

/*
 * Process shutter "help" command
 */
int stage_shutcmd_help(client_t *client, stage_t *dev)
{
	char *grp = getargv(client, 0);

	sendres(client, "%s Control\n", dev->desc);
	sendres(client, "Usage: %s %s <command> [<argument>]\n", grp, dev->id);
	sendres_hsect(client, "commands and arguments");
	sendres_hitem(client, "open", "open shutter");
	sendres_hitem(client, "close", "close shutter");
	sendres_hitem(client, "st", "show status (using cache)");
	sendres_hitem(client, "stu", "show status (not using cache)");
	sendres_hitem(client, "help", "show help message");

	return 0;
}

/*
 * Process "all help" command
 */
int stage_allcmd_help(client_t *client)
{
	char *grp = getargv(client, 0);

	sendres(client, "Usage: %s all <command>\n", grp);
	sendres_hsect(client, "commands and arguments");
	sendres_hitem(client, "home", "do homing");
	sendres_hitem(client, "init", "do homing and move base position");
	sendres_hitem(client, "st [all]", "show status (using cache)");
	sendres_hitem(client, "stu [all]", "show status (not using cache)");
	sendres_hitem(client, "help", "show help message");

	return 0;
}
