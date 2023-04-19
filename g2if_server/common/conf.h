/*
 * conf.h -- Definitions for functions to process configuration parameters
 *
 * 2008/10/30 Makoto WATANABE -- Initial version
 * 2019/07/08 Yoshito ONO -- Added setpar_flt
 */

#ifndef _CONF_H
#define _CONF_H

#include <stdio.h>				/* for FILE */
#include <stdint.h>				/* for int32_t */
#include "alias.h"				/* for alias_t */

enum {
	CONF_PAR_MAX  = 124,	/* Maximum length of string for parameter */
	CONF_ARGC_MAX = 32,		/* Maximum number of arguments for parameter */
};

#ifdef __cplusplus
extern "C" {
#endif

/* Function prototypes */

char *strrmcomment(char *str);
int getconfpar(FILE *fp, char *buf, size_t size, char **argv, int maxargc);
int chksect(const char *arg, char *name, size_t size);
int getsubsect(const char *sect, int n, char *subsect, size_t size);

void debug_doing_par(int argc, const char **argv);
void setpar_unknown_sect(const char *sect);
void setpar_unknown_par(const char *key);
void setpar_missing_arg(const char *key);
void setpar_invalid_argument(const char *key, const char *arg);
void setpar_toomany_argument(const char *key);

int setpar_chkargi(int argc, const char **argv, int i);
int setpar_strdup(int argc, const char **argv, int i, char **valp);
int setpar_strcpy(int argc, const char **argv, int i, char *val, size_t size);
int setpar_strjoin(int argc, const char **argv, char *val, size_t size);
int setpar_long(int argc, const char **argv, int i, long *val, long min,
	long max);
int setpar_ulong(int argc, const char **argv, int i, unsigned long *val,
	unsigned long min, unsigned long max);
int setpar_int(int argc, const char **argv, int i, int *val, int min, int max);
int setpar_uint(int argc, const char **argv, int i, unsigned int *val,
	unsigned int min, unsigned int max);
int setpar_int32(int argc, const char **argv, int i, int32_t *val, int32_t min,
	int32_t max);
int setpar_dbl(int argc, const char **argv, int i, double *val, double min,
	double max);
int setpar_flt(int argc, const char **argv, int i, float *val, float min,
	float max);
int setpar_alias(int argc, const char **argv, alias_t *alias);


#ifdef __cplusplus
}
#endif

#endif /* _CONF_H */
