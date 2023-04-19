/* -------------------------------------------------------------------------
 * tool.c -- Define useful tools
 * -------------------------------------------------------------------------
 * Update History:
 * <Date>       <Who>         <What>    
 *  2019/04/11   Y.Ono         Initial version
 * -------------------------------------------------------------------------
 */

#ifndef _TOOL_H
#define _TOOL_H

#include <stdio.h>				/* for FILE */
#include <stdint.h>				/* for int32_t */
#include <time.h>

#ifdef __cplusplus
extern "C" {
#endif

  /* Function prototypes */
  
  int get_ip(const char *hostname , char* ip);
  int cmp_timespec(const struct timespec *ts1, const struct timespec *ts2);
  int fits_write_flt(const char *filename, float *data, const long xs, const long ys);

#ifdef __cplusplus
}
#endif

#endif /* _TOOL_H */
