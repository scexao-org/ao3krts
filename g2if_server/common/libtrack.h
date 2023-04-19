/*
 * libtrack.h -- Definitions for functions dealing with tracking mode
 *
 * Written by Yosuke Minowa
 */

#ifndef _LIBTRACK_H
#define _LIBTRACK_H

#ifdef __cplusplus
extern "C" {
#endif

#define fix(x)   ( (double)((int)x) )

/***** Telescope Location *****/
/* latitude in [rad] */
#define P_RAD ( 19.8285*(M_PI/180.0) )
/* longitude in [rad]; note that the east is defined as '+' */
#define L_RAD ( -155.4802*(M_PI/180.0) )

/*** offset angle for ADI IMR tracking mode ***/
#define ADI_OFFSET	-180.0 // deg

/* Function prototypes */
  int resolve_ra(char *ra, double *alpha);
  int resolve_dec(char *dec, double *delta);
  int resolve_utc(char *utc, time_t *t);
  int get_current_azel(double alpha0, double delta0, double *az, double *el);
  double tp(double az, double el);
  double dar(double el, double lambda, double lambda0, double TC, double RH, double P);
  double calc_adipa(double alpha0, double delta0, double offset);
#ifdef __cplusplus
}
#endif

#endif /* _LIBTRACK_H */
