/* -------------------------------------------------------------------------
 * tool.c -- Useful Functions
 * -------------------------------------------------------------------------
 * Update History:
 * <Date>       <Who>         <What>    
 *  2019/04/11   Y.Ono         Initial version
 * -------------------------------------------------------------------------
 */

#include <stdlib.h>				/* for strtol(), strtod() */
#include <stdint.h>				/* for int32_t */
#include <string.h>				/* for strncat() */
#include <netdb.h>                              /* for gethostbyname(), herror, hostent */
#include <arpa/inet.h>		        	/* for inet_ntoa() */
#include "fitsio.h"
#include "log.h"


/*
 * Get ip addr from hostname
 */
int get_ip(const char *hostname , char* ip) 
{ 
  struct hostent *he;     
  struct in_addr **addr_list;     
  int i;

  if ( (he = gethostbyname( hostname ) ) == NULL) { 
    herror("gethostbyname");         
    return -1;
  }     
  addr_list = (struct in_addr **) he->h_addr_list;
  for(i = 0; addr_list[i] != NULL; i++){ 
    strcpy(ip , inet_ntoa(*addr_list[i]));
  }
  return 1;
}

/*
 * Compare Time Spec
 */
int cmp_timespec(const struct timespec *ts1, const struct timespec *ts2){
  double t1 = ts1->tv_sec*1.0 + ts1->tv_nsec*1e-9;
  double t2 = ts2->tv_sec*1.0 + ts2->tv_nsec*1e-9;
  if(t1 > t2) return 1;
  else if(t1 == t2) return 0;
  else return -1;
}

/*
 * Write data to fitsfile (float)
 */
int fits_write_flt(const char *filename, float *data, const long xs, const long ys){

  fitsfile *fptr; /* pointer to the FITS file; defined in fitsio.h */
  int status;
  long fpixel = 1, naxis = 2, nelements;
  long naxes[2]; /* image */
  naxes[0] = xs;
  naxes[1] = ys;

  status = 0; /* initialize status before calling fitsio routines */

  /* create new file */
  fits_create_file(&fptr, filename, &status);

  /* Create the primary array image */
  fits_create_img(fptr, FLOAT_IMG, naxis, naxes, &status);

  /* Write the array of integers to the image */
  nelements = naxes[0] * naxes[1]; /* number of pixels to write */
  fits_write_img(fptr, TFLOAT, fpixel, nelements, data, &status);

  /* close the file */
  fits_close_file(fptr, &status);

  return status;
}

