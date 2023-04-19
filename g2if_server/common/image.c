/*
 * image.c - Functions to handle imera image data
 *
 * 2008/12/19 Makoto WATANABE - Initial version (derived from aqcam_camera.cpp)
 */

#include <unistd.h>				/* for getcwd(), access(), mkdir() */
#include <stdio.h>				/* for snprintf() */
#include <stdlib.h>				/* for malloc(), free() */
#include <string.h>				/* for strdup() */
#include <pthread.h>			/* for pthread_*() */
#include <fitsio.h>				/* for fits_*() */
#include <sys/stat.h>			/* for mkdir() */
#include <sys/time.h>			/* for struct timeval and gettimeofday() */
#include <time.h>				/* for struct tm, gmtime_r(), localtime_r() */
#include <errno.h>				/* for errno */
#include "log.h"				/* for error(), info(), debug() */
#include "server.h"				/* for client_t, getargv() */
#include "stringx.h"			/* for strncatx(), strncatf() */
#include "image.h"				/* for image_t */

/*
 * Initialize image_t data
 */
int image_init(image_t *im, const char *header)
{
	if (header != NULL) {
		im->header = strdup(header);
	} else {
		im->header = strdup("image");
	}
	if (im->header == NULL) {
		error_num(errno, "%s: cannot initialize image_t data", header);
		return -1;
	}

	/* Initialize fields */
	im->dir[0] = '\0';
	strncat(im->dir, ".", sizeof(im->dir) - 1);
	im->numfile[0] = '\0';
	strncat(im->numfile, "image_imnum", sizeof(im->numfile) - 1);
	im->dispcmd = NULL;
	im->num_cams = 0;
	im->cams = NULL;
	pthread_mutex_init(&(im->lock), NULL);

	return 0;
}

/*
 * Allocate memory for parameters related to each camera
 */
int image_alloccam(image_t *im, int n)
{
	int i;
	image_camera_t *imcam;

	im->cams = malloc(sizeof(struct image_camera) * n);
	if (im->cams == NULL) {
		error_num(errno, "%s: cannot allocate memory for image parameters",
			im->header);
		return -1;
	}
	im->num_cams = n;

	for (i = 0; i < n; i++) {
		imcam = &(im->cams[i]);
		imcam->detid = i + 1;
		snprintf(imcam->prefix, sizeof(imcam->prefix),
			IMAGE_PREFIX_DEFAULT"_%c", 'a' + i);
		imcam->imnum = 1;
		imcam->latest[0] = '\0';
		imcam->objname[0] = '\0';
		imcam->dispmode = 1;
		imcam->dispframe = i + 1;
	}

	return 0;
}

/*
 * Free resources in image_t structure
 */
int image_free(image_t *im)
{
/*	debug("image: free");*/

	free(im->cams);
	free(im->dispcmd);
	free(im->header);
	pthread_mutex_destroy(&(im->lock));

	return 0;
}

/*
 * Set data directory of image file
 */
int image_setdir(image_t *im, const char *dir)
{
	char cwd[PATH_MAX];

	pthread_mutex_lock(&(im->lock));
	if (dir[0] == '/') {
		im->dir[0] = '\0';
		strncpy(im->dir, dir, sizeof(im->dir) - 1);
	} else {
		snprintf(im->dir, sizeof(im->dir), "%s/%s",
			getcwd(cwd, sizeof(cwd) - 1), dir);
	}
	pthread_mutex_unlock(&(im->lock));

	return 0;
}

/*
 * Get data directory of image file
 */
char *image_getdir(image_t *im, char *dir, size_t size)
{
	dir[0] = '\0';
	pthread_mutex_lock(&(im->lock));
	strncat(dir, im->dir, size - 1);
	pthread_mutex_unlock(&(im->lock));

	return dir;
}

/*
 * Set prefix of image file for n-th camera
 */
int image_setprefix(image_t *im, int n, const char *prefix)
{
	image_camera_t *imcam;

	pthread_mutex_lock(&(im->lock));
	imcam = &(im->cams[n]);
	imcam->prefix[0] = '\0';
	strncat(imcam->prefix, prefix, sizeof(imcam->prefix) - 1);
	pthread_mutex_unlock(&(im->lock));

	return 0;
}

/*
 * Return prefix of image file for n-th camera
 */
char *image_getprefix(image_t *im, int n, char *prefix, size_t size)
{

	prefix[0] = '\0';
	pthread_mutex_lock(&(im->lock));
	strncat(prefix, (im->cams[n]).prefix, size - 1);
	pthread_mutex_unlock(&(im->lock));

	return prefix;
}

/*
 * Set filename of image number file
 */
int image_setnumfile(image_t *im, const char *path)
{
	pthread_mutex_lock(&(im->lock));
	im->numfile[0] = '\0';
	strncat(im->numfile, path, sizeof(im->numfile) - 1);
	pthread_mutex_unlock(&(im->lock));

	return 0;
}

/*
 * Read image number and latest image name from file
 */
int image_readnumfile(image_t *im)
{
	int i, n, in, detid, imnum, oldstate;
	char line[512], latest[NAME_MAX + 1];
	image_camera_t *imcam;
	FILE *fp;

	/* If no file is specified, return w/o reading */
	pthread_mutex_lock(&(im->lock));
	if (im->numfile[0] == '\0') {
		pthread_mutex_unlock(&(im->lock));
		return 0;
	}
	pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, &oldstate);

	info("%s: reading image number and latest image name "
		"from image number file (%s)", im->header, im->numfile);

	/* Open image number file */
	if ((fp = fopen(im->numfile, "r")) == NULL) {
		error_num(errno, "%s: cannot read image number file (%s)",
			im->header, im->numfile);
		pthread_mutex_unlock(&(im->lock));
		pthread_setcancelstate(oldstate, NULL);
		return -1;
	}

	/* Get line by line from file */
	n = im->num_cams;
	while (fgets(line, sizeof(line) - 1, fp) != NULL) {

		/* Skip comment lines starting '#' */
		if (line[0] == '#') {
			continue;
		}

		/* Scan detector id, image number, and latest image name */
		latest[0] = '\0';
		if ((in = sscanf(line, "%d %d %255s", &detid, &imnum, latest)) < 2
			|| imnum < 0) {
			errno = EINVAL;
			error_num(errno,
				"%s: unexpected string in image number file -- %s",
				im->header, line);
			continue;
		}

		/* Set image number and latest image name */
		for (i = 0; i < n; i++) {
			imcam = &(im->cams[i]);
			if (imcam->detid == detid) {
				info("%s.%d: setting image number to %d", im->header, detid,
					imnum);
				imcam->imnum = imnum;
				if (in > 2) {
					info("%s.%d: getting latest image name '%s'", im->header,
						detid, latest);
					imcam->latest[0] = '\0';
					strncat(imcam->latest, latest, sizeof(imcam->latest) - 1);
				}
			}
		}
	}
	fclose(fp);

	pthread_mutex_unlock(&(im->lock));
	pthread_setcancelstate(oldstate, NULL);

	return 0;
}

/*
 * Update image number on image number file (file must exist before)
 */
int image_writenumfile(image_t *im)
{
	int i, n, noreplace, detid, imnum, oldstate;
	char line[512], buf[4096];
	FILE *fp;
	image_camera_t *imcam;

	/* If no file is specified, return w/o writing */
	pthread_mutex_lock(&(im->lock));
	if (im->numfile[0] == '\0') {
		pthread_mutex_unlock(&(im->lock));
		return 0;
	}

	pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, &oldstate);

	/* Open image number file */
	if ((fp = fopen(im->numfile, "r+")) == NULL) {
		error_num(errno, "%s: cannot open image number file (%s)",
			im->header, im->numfile);
		pthread_mutex_unlock(&(im->lock));
		pthread_setcancelstate(oldstate, NULL);
		return -1;
	}

	/* Get line by line from file */
	n = im->num_cams;
	buf[0] = '\0';
	while (fgets(line, sizeof(line) - 1, fp) != NULL) {

		noreplace = 1;

		/* Replace line w/ updated image number and latest image name */
		if (line[0] != '#' && sscanf(line, "%d %d", &detid, &imnum) > 1) {
			for (i = 0; i < n; i++) {
				imcam = &(im->cams[i]);
				if (imcam->detid == detid) {
					strncatf(buf, sizeof(buf), "%d %d %s\n",
						detid, imcam->imnum, imcam->latest);
					noreplace = 0;
				}
			}
		}

		/* Output original line if no need replace */
		if (noreplace) {
			strncatx(buf, sizeof(buf), line);
		}
	}

	/* Write buffer into file */
	rewind(fp);
	fputs(buf, fp);
	if (fclose(fp) != 0) {
		error_num(errno, "error in closing image number file (%s)",
			im->numfile);
	}

	pthread_mutex_unlock(&(im->lock));
	pthread_setcancelstate(oldstate, NULL);

	return 0;
}

/*
 * Set image number for n-th camera
 */
int image_setimnum(image_t *im, int n, int imnum)
{
	if (imnum < 0) {
		errno = EINVAL;
		error_num(errno, "%s: invalid image number", im->header);
		return -1;
	}
	pthread_mutex_lock(&(im->lock));
	(im->cams[n]).imnum = imnum;
	pthread_mutex_unlock(&(im->lock));

	return 0;
}

/*
 * Increment image number for n-th camera
 */
int image_incimnum(image_t *im, int n)
{
	pthread_mutex_lock(&(im->lock));
	(im->cams[n]).imnum++;
	pthread_mutex_unlock(&(im->lock));

	return 0;
}

/*
 * Get current image number for n-th camera
 */
int image_getimnum(image_t *im, int n)
{
	int imnum;

	pthread_mutex_lock(&(im->lock));
	imnum = (im->cams[n]).imnum;
	pthread_mutex_unlock(&(im->lock));

	return imnum;
}

/*
 * Set latest image file name for n-th camera
 */
int image_setlatest(image_t *im, int n, const char *latest)
{
	image_camera_t *imcam;

	pthread_mutex_lock(&(im->lock));
	imcam = &(im->cams[n]);
	imcam->latest[0] = '\0';
	strncat(imcam->latest, latest, sizeof(imcam->latest) - 1);
	pthread_mutex_unlock(&(im->lock));

	return 0;
}

/*
 * Get image file name of latest image for n-th camera
 */
char *image_getlatest(image_t *im, int n, char *latest, size_t size)
{
	latest[0] = '\0';
	pthread_mutex_lock(&(im->lock));
	strncat(latest, (im->cams[n]).latest, size - 1);
	pthread_mutex_unlock(&(im->lock));

	return latest;
}

/*
 * Get dir and prefix name after convertion of date format string
 */
int image_getimname(image_t *im, int n, time_t *t, char *dir, int size_dir,
	char *filename, size_t size_filename)
{
	char prefix[NAME_MAX + 1];
	image_camera_t *imcam;
	struct tm tm;

	/* Create image file name w/ information of start time of exposure */
	gmtime_r(t, &tm);
	pthread_mutex_lock(&(im->lock));
	imcam = &(im->cams[n]);
	strftime(dir, size_dir, im->dir, &tm);
	strftime(prefix, sizeof(prefix), imcam->prefix, &tm);
	snprintf(filename, size_filename, "%s"IMAGE_NUMBER_FORMAT".fits",
		prefix, imcam->imnum);
	pthread_mutex_unlock(&(im->lock));

	return 0;
}

/*
 * Set object name of image for n-th camera
 */
int image_setobjname(image_t *im, int n, const char *objname)
{
	image_camera_t *cam;

	pthread_mutex_lock(&(im->lock));
	cam = &(im->cams[n]);
	cam->objname[0] = '\0';
	strncat(cam->objname, objname, sizeof(cam->objname) - 1);
	pthread_mutex_unlock(&(im->lock));

	return 0;
}

/*
 * Get current object name for n-th camera
 */
char *image_getobjname(image_t *im, int n, char *objname, size_t size)
{
	pthread_mutex_lock(&(im->lock));
	objname[0] = '\0';
	strncat(objname, (im->cams[n]).objname, size - 1);
	pthread_mutex_unlock(&(im->lock));

	return objname;
}

/*
 * Set command line string for display command
 */
int image_setdispcmd(image_t *im, const char *cmd)
{
	pthread_mutex_lock(&(im->lock));
	im->dispcmd[0] = '\0';
	strncat(im->dispcmd, cmd, sizeof(im->dispcmd) - 1);
	pthread_mutex_unlock(&(im->lock));

	return 0;
}

/*
 * Set automatic display mode for n-th camera
 * (1: on, 0: off)
 */
int image_setdispmode(image_t *im, int n, int mode)
{
	pthread_mutex_lock(&(im->lock));
	(im->cams[n]).dispmode = mode;
	pthread_mutex_unlock(&(im->lock));

	return 0;
}

/*
 * Get automatic display mode
 * (1: on, 0: off)
 */
int image_getdispmode(image_t *im, int n)
{
	int mode;

	pthread_mutex_lock(&(im->lock));
	mode = (im->cams[n]).dispmode;
	pthread_mutex_unlock(&(im->lock));

	return mode;
}

/*
 * Display image on image viewer (Execute display command)
 */
int image_disp(image_t *im, int n, const char *path)
{
	char cmd[PATH_MAX];
	image_camera_t *imcam;

	/* Check if display command is specified and dispmode */
	pthread_mutex_lock(&(im->lock));
	imcam = &(im->cams[n]);
	if (im->dispcmd[0] == '\0' || imcam->dispmode == 0) {
		pthread_mutex_unlock(&(im->lock));
		return 0;
	}

	/* Create command string */
	snprintf(cmd, sizeof(cmd), "%s %d %s", im->dispcmd, imcam->dispframe,
		path);
	pthread_mutex_unlock(&(im->lock));

	/* Excute display command */
	debug("%s.%d: executing display command \"%s\"", im->header, imcam->detid,
		cmd);
	errno = 0;
	if (system(cmd) != 0) {
		if (errno) {
			errno = EINVAL;
		}
		error_num(errno,
			"%s.%d: cannot display image: error in excuting command '%s'",
			im->header, imcam->detid, cmd);
		return -1;
	}

	return 0;
}

/*
 * Get setting parameter values of image handler
 */
int image_getstat(image_t *im, int n, struct image_stat *stat)
{
	time_t t;
	struct tm tm;
	image_camera_t *imcam;

	time(&t);
	gmtime_r(&t, &tm);

	pthread_mutex_lock(&(im->lock));

	imcam = &(im->cams[n]);
	stat->detid = imcam->detid;
	strftime(stat->dir, sizeof(stat->dir), im->dir, &tm);
	strftime(stat->prefix, sizeof(stat->prefix), imcam->prefix, &tm);
	stat->imnum = imcam->imnum;
	stat->latest[0] = '\0';
	strncat(stat->latest, imcam->latest, sizeof(stat->latest) - 1);
	stat->objname[0] = '\0';
	strncat(stat->objname, imcam->objname, sizeof(stat->objname) - 1);
	stat->dispmode = imcam->dispmode;
	stat->dispframe = imcam->dispframe;

	pthread_mutex_unlock(&(im->lock));

	return 0;
}

/*
 * Logging error message of FITSIO function
 */
static int image_error_fitsio(image_t *im, int n, int errcode)
{
	char errstr[FLEN_STATUS + 1];

	fits_get_errstatus(errcode, errstr);
	error("%s.%d: FITSIO Error %d: %s", im->header, (im->cams[n]).detid,
		errcode, errstr);

	return 0;
}

/*
 * Set fits keywords into image file
 */
int image_setkeywords(image_t *im, int n, struct image_data *imdata,
	fitsfile *fptr)
{
	int errcode;
	char val[FLEN_VALUE + 1];
	double hexptime;
	struct timeval tv2, tv3;
	struct tm tm;

	debug("%s.%d: setting common fits keywords into file", im->header,
		(im->cams[n]).detid);

	/* Write OBSERVAT keyword */
	errcode = 0;
	fits_write_key_str(fptr, "OBSERVAT", "NAOJ", "Observatory name", &errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	/* Write TELESCOP keyword */
	errcode = 0;
	fits_write_key_str(fptr, "TELESCOP", "SUBARU", "Name of telescope",
		&errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	/* Write INSTRUME keyword */
	errcode = 0;
	fits_write_key_str(fptr, "INSTRUME", "AO188", "Name of instrument",
		&errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	/* Write OBJECT keyword */
	snprintf(val, sizeof(val), "%s", imdata->objname);
	errcode = 0;
	fits_write_key_str(fptr, "OBJECT", val, "Name of object", &errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	/* Write DATA-TYP keyword */
	errcode = 0;
	fits_write_key_str(fptr, "DATA-TYP", imdata->type, "Type of data",
		&errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	/* Write DET-ID keyword */
	errcode = 0;
	fits_write_key_lng(fptr, "DET-ID", imdata->detid,
		 "Detector id. (1:HOWFS, 2:LOWFS)", &errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	/* Write DETECTOR keyword */
	errcode = 0;
	fits_write_key_str(fptr, "DETECTOR", imdata->detector,
		"Name of detector", &errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	/* Write DET-VER keyword */
	errcode = 0;
	fits_write_key_str(fptr, "DET-VER", imdata->detver,
		"Version of detector control software", &errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	/* Write TIMESYS keyword */
	errcode = 0;
	fits_write_key_str(fptr, "TIMESYS", "UTC",
		"Time system used in this header", &errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	/* Write DATE-OBS keyword */
	gmtime_r(&(imdata->tv.tv_sec), &tm);
	errcode = 0;
	fits_date2str(tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, val, &errcode);
	errcode = 0;
	fits_write_key_str(fptr, "DATE-OBS", val,
		"UT date of observation (yyyy-mm-dd)", &errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	/* Write EXPTIME keyword */
	errcode = 0;
	fits_write_key_fixdbl(fptr, "EXPTIME", imdata->exptime, 5,
		"Integration time in seconds", &errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	/* Write UT-STR keyword */
	errcode = 0;
	fits_time2str(0, 0, 0, tm.tm_hour, tm.tm_min,
		tm.tm_sec + imdata->tv.tv_usec / 1E6, 3, val, &errcode);
	errcode = 0;
	fits_write_key_str(fptr, "UT-STR", val,
		"Start exposure at UTC (hh:mm:ss.ss)", &errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	/* Write UT keyword */
	hexptime = imdata->exptime / 2.0;
	tv2.tv_sec = hexptime;
	tv2.tv_usec = (hexptime - tv2.tv_sec) * 1E6;
	timeradd(&(imdata->tv), &tv2, &tv3);
	gmtime_r(&(tv3.tv_sec), &tm);
	errcode = 0;
	fits_time2str(0, 0, 0, tm.tm_hour, tm.tm_min,
		tm.tm_sec + tv3.tv_usec / 1E6, 3, val, &errcode);
	errcode = 0;
	fits_write_key_str(fptr, "UT", val,
		"Typical UTC at exposure (hh:mm:ss.ss)", &errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	/* Write UT-END keyword */
	tv2.tv_sec = imdata->exptime;
	tv2.tv_usec = (imdata->exptime - tv2.tv_sec) * 1E6;
	timeradd(&(imdata->tv), &tv2, &tv3);
	gmtime_r(&(tv3.tv_sec), &tm);
	errcode = 0;
	fits_time2str(0, 0, 0, tm.tm_hour, tm.tm_min,
		tm.tm_sec + tv3.tv_usec / 1E6, 3, val, &errcode);
	errcode = 0;
	fits_write_key_str(fptr, "UT-END", val,
		"End exposure at UTC (hh:mm:ss.ss)", &errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	/* Write HST keyword */
	localtime_r(&(imdata->tv.tv_sec), &tm);
	errcode = 0;
	fits_time2str(0, 0, 0, tm.tm_hour, tm.tm_min,
		tm.tm_sec + imdata->tv.tv_usec / 1E6, 3, val, &errcode);
	errcode = 0;
	fits_write_key_str(fptr, "HST", val,
		"Start exposure at HST (hh:mm:ss.ss)", &errcode);
	if (errcode != 0) {
		image_error_fitsio(im, n, errcode);
	}

	return 0;
}

/*
 * Cleanup routine for cancellation
 */
static void image_write_cleanup(fitsfile *fptr)
{
	int errcode;

	debug("image: writing of image is cancelled -- closing fits file");
	fits_close_file(fptr, &errcode);
}

/*
 * Write image data into a 2-dimensional FITS image file
 */
int image_write(image_t *im, int n, struct image_data *imdata, char *path,
	int (*func)(void *, void *, fitsfile *), void *arg1, void *arg2,
	int *errcode)
{
	int naxis, detid;
	long naxes[2], fpixel[] = { 1, 1 }, nelements;
	fitsfile *fptr;

	detid = (im->cams[n]).detid;

	info("%s.%d: writing image to file (%s)", im->header, detid, path);

	/* errcode must be initialized before calling fitsio routines */
	*errcode = 0;

	/* Create an empty FITS file */
	debug("%s.%d: creating empty fits file", im->header, detid);
	fits_create_file(&fptr, path, errcode);
	if (*errcode != 0) {
		image_error_fitsio(im, n, *errcode);
		return 0;
	}
	pthread_cleanup_push((void *)image_write_cleanup, &fptr);

	/* Create an image on FITS file */
	debug("%s.%d: writing pixel data into fits file", im->header, detid);
	naxis = 2;
	naxes[0] = imdata->nx;
	naxes[1] = imdata->ny;
	fits_create_img(fptr, imdata->bitpix, naxis, naxes, errcode);
	if (*errcode != 0) {
		image_error_fitsio(im, n, *errcode);
	} else {

		/* Write fits keywords */
		image_setkeywords(im, n, imdata, fptr);
		(*func)(arg1, arg2, fptr);

		/* Write data array into FITS image */
		nelements = naxes[0] * naxes[1];
		fits_write_pix(fptr, imdata->datatype, fpixel, nelements, imdata->data,
			errcode);
		if (*errcode != 0) {
			image_error_fitsio(im, n, *errcode);
		}
	}

	pthread_cleanup_pop(0);

	/* Close fits file */
	debug("%s.%d: closing fits file", im->header, detid);
	fits_close_file(fptr, errcode);
	if (*errcode != 0) {
		image_error_fitsio(im, n, *errcode);
	}

	return 0;
}

/*
 * Check if image directory exists, if does not exist create it
 */
int image_chkdir(image_t *im, const char *dir)
{
	int ret;

	debug("%s: checking image directory (%s)", im->header, dir);

	if (access(dir, W_OK) < 0) {
		if (errno != ENOENT) {
			error_num(errno, "cannot accesss image directory (%s)", dir);
			return -1;
		} else if ((ret =
			mkdir(dir, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH)) < 0) {
			error_num(errno, "cannot create image directory (%s)", dir);
			return ret;
		}
	}

	return 0;
}

/*
 * Process "dir" command (set directory of image)
 */
int image_cmd_dir(client_t *client, image_t *im)
{
	char *grp = im->header;
	char *arg = getargv(client, 3);

	if (arg == NULL) {
		sendres_error(client, "missing directory name");
		return -1;
	} else if (image_setdir(im, arg) < 0) {
		sendres_error(client, "invalid directory name -- %s", arg);
		return -1;
	}
	info("%s: setdir %s", grp, arg);

	return 0;
}

/*
 * Process "fp" command (set file prefix of image)
 */
int image_cmd_fp(client_t *client, image_t *im, int n)
{
	const char *grp = im->header;
	char *arg = getargv(client, 3);
	image_camera_t *imcam = &(im->cams[n]);

	if (arg == NULL) {
		sendres_error(client, "missing file prefix");
		return -1;
	} else if (image_setprefix(im, n, arg) < 0) {
		sendres_error(client, "invalid image file prefix -- %s", arg);
		return -1;
	}
	info("%s.%d: setprefix %s", grp, imcam->detid, arg);

	return 0;
}

/*
 * Process "fn" command (set file number)
 */
int image_cmd_fn(client_t *client, image_t *im, int n)
{
	int i;
	char *grp = im->header;
	char *arg = getargv(client, 3);
	image_camera_t *imcam = &(im->cams[n]);

	if (getargv_int(client, 3, &i, 0, INT_MAX) < 0) {
		return -1;
	} else if (image_setimnum(im, n, i) < 0) {
		sendres_error(client, "invalid image file number -- %s", arg);
		return -1;
	}
	info("%s.%d: setimnum %d", grp, imcam->detid, i);

	return 0;
}

/*
 * Process "obj" command (set object name)
 */
int image_cmd_obj(client_t *client, image_t *im, int n)
{
	char objname[FLEN_VALUE + 1];
	const char *grp = im->header;
	image_camera_t *imcam = &(im->cams[n]);

	if (getargv_strjoin(client, 3, objname, sizeof(objname)) < 0) {
		return -1;
	} else if (image_setobjname(im, n, objname) < 0) {
		sendres_error(client, "invalid object name -- %s", objname);
		return -1;
	}
	info("%s.%d: setobjname %s", grp, imcam->detid, objname);

	return 0;
}

/*
 * Process "obj" command (set object name)
 */
int image_cmd_dispmode(client_t *client, image_t *im, int n)
{
	int mode;
	const char *grp = im->header;
	char *arg = getargv(client, 3);
	image_camera_t *imcam = &(im->cams[n]);

	if (arg == NULL) {
		sendres_error(client, "missing display mode");
		return -1;
	} else if (strcasecmp(arg, "on") == 0) {
		mode = 1;
	} else if (strcasecmp(arg, "off") == 0) {
		mode = 0;
	} else {
		sendres_error(client, "invalid display mode -- %s", arg);
		return -1;
	}

	info("%s.%d: setdispmode %d", grp, imcam->detid, mode);
	image_setdispmode(im, n, mode);

	return 0;
}
