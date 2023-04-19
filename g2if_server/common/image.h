/*
 * image.h -- Definitions for functions to handle camera image data
 *
 * 2008/12/19 Makoto WATANABE - Initial version (derived from aqcam_camera.h)
 */

#ifndef _IMAGE_H
#define _IMAGE_H

#include <limits.h>				/* for PATH_MAX, NAME_MAX */
#include <fitsio.h>				/* for fitsfile, FLEN_VALUE */
#include "server.h"				/* for client_t */

#define IMAGE_PREFIX_DEFAULT	"ao188_%%y%%m%%d"
#define IMAGE_NUMBER_FORMAT		"%05d"

/* Structure to store image parameters related to each camera */

typedef struct image_camera {
	int detid;						/* detector id number for DET-ID */
	char prefix[NAME_MAX + 1];		/* prefix of image file */
	int imnum;						/* image number of next image */
 	char latest[NAME_MAX + 1];		/* file name of latest image */
	char objname[FLEN_VALUE + 1];	/* currect object name of image */
	int dispmode;					/* mode of automatic display of image */
	int dispframe;					/* frame number for display command */
} image_camera_t;

/* Structure to handle image data */

typedef struct image {
	char dir[PATH_MAX];				/* directory of image files */
 	char numfile[PATH_MAX];			/* file name of image number file */
 	char *dispcmd;					/* display command string */
	int num_cams;					/* number of cameras to store params */
	image_camera_t *cams;			/* pointer to parameters for each camera */
	char *header;					/* header string for logging message */
	pthread_mutex_t lock;			/* mutex for access alta driver */
} image_t;

/* Structure to store setting parameter values of image handler */

struct image_stat {
	int detid;						/* detector id number for DET-ID */
	char dir[PATH_MAX];				/* directory of image files */
	char prefix[NAME_MAX + 1];		/* prefix of image file */
	int imnum;						/* image number of next image */
 	char latest[NAME_MAX + 1];		/* file name of latest image */
	char objname[FLEN_VALUE + 1];	/* currect object name of image */
	int dispmode;					/* mode of automatic display of image */
	int dispframe;					/* frame number for display command */
};

/* Structure to store information for image headers and image data array */

struct image_data {
	int nx;						/* number of pixels of image along x */
	int ny;						/* number of pixels of image along y */
	int bitpix;					/* bitpix value of image (USHORT_IMG, etc) */
	int datatype;				/* data type of image data (TUSHORT, etc) */
	void *data;					/* pointer to image data array */
	char *objname;				/* object name */
	char *type;					/* type of data */
	int detid;					/* detector id number for DET-ID */
	char *detector;				/* detector name */
	char *detver;				/* detector version name */
	struct timeval tv;			/* start time of exposure */
	double exptime;				/* exposure time in seconds */
};

#ifdef __cplusplus
extern "C" {
#endif

/* Function prototypes */

int image_init(image_t *im, const char *header);
int image_alloccam(image_t *im, int n);
int image_free(image_t *im);

int image_setdir(image_t *im, const char *dir);
char *image_getdir(image_t *im, char *dir, size_t size);

int image_setprefix(image_t *im, int n, const char *prefix);
char *image_getprefix(image_t *im, int n, char *prefix, size_t size);

int image_setnumfile(image_t *im, const char *path);
int image_readnumfile(image_t *im);
int image_writenumfile(image_t *im);
int image_setimnum(image_t *im, int n, int imnum);
int image_incimnum(image_t *im, int n);
int image_getimnum(image_t *im, int n);
int image_setlatest(image_t *im, int n, const char *latest);
char *image_getlatest(image_t *im, int n, char *latest, size_t size);
int image_getimname(image_t *im, int n, time_t *t, char *dir, int size_dir,
	char *filename, size_t size_filename);

int image_setobjname(image_t *im, int n, const char *objname);
char *image_getobjname(image_t *im, int n, char *objname, size_t size);

int image_setdispcmd(image_t *im, const char *cmd);
int image_setdispmode(image_t *im, int n, int mode);
int image_getdispmode(image_t *im, int n);
int image_disp(image_t *im, int n, const char *path);

int image_getstat(image_t *im, int n, struct image_stat *stat);

int image_setkeywords(image_t *im, int n, struct image_data *imdata,
	fitsfile *fptr);
int image_write(image_t *im, int n, struct image_data *imdata, char *path,
	int (*func)(void *, void *, fitsfile *), void *arg1, void *arg2,
	int *errcode);

int image_chkdir(image_t *im, const char *dir);

int image_cmd_dir(client_t *client, image_t *im);
int image_cmd_fp(client_t *client, image_t *im, int n);
int image_cmd_fn(client_t *client, image_t *im, int n);
int image_cmd_obj(client_t *client, image_t *im, int n);
int image_cmd_dispmode(client_t *client, image_t *im, int n);

#ifdef __cplusplus
}
#endif

#endif /* _IMAGE_H */
