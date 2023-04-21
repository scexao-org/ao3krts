/*
 * conf.c -- Functions to process configuration parameters
 *
 * 2008/10/30 Makoto WATANABE -- Initial version
 * 2019/07/08 Yoshito ONO -- Added setpar_flt
 */

#include <stdlib.h>				/* for strtol(), strtod() */
#include <stdint.h>				/* for int32_t */
#include <limits.h>				/* for INT_MIN, INT_MAX */
#include <string.h>				/* for strncat() */
#include <errno.h>				/* for errno */
#include "alias.h"				/* for alias_t, alias_*() */
#include "log.h"				/* for error(), info(), debug() */
#include "stringx.h"		        	/* for strjoin() */
#include "conf.h"

static const char *conf_header = "conf";

/*
 * Remove comments starting charactor '#' in string
 *
 * '#' charactors inside a quote (by ' or ") are ignored
 */
char *strrmcomment(char *str)
{
	char c, *s, quote = 0;

	for (s = str; (c = *s); s++) {
		if (quote == 0 && c == '#') {
			*s = '\0';
			break;
		} else if (c == quote) {
			quote = 0;
		} else if (c == '\'' || c == '\"') {
			quote = c;
		}
	}

	return str;
}

/*
 * Get a configuration parameter from file
 */
int getconfpar(FILE *fp, char *buf, size_t size, char **argv, int maxargc)
{
	int argc;

	while (fgets(buf, size, fp) != NULL) {

		/* Remove CR at end of line */
		strrmcrlf(buf);

		/* Check length of parameter string */
		if (strlen(buf) > size - 2) {
			error("%s: too long parameter line -- %s: "
				"must be within %d charactors", conf_header, buf, size - 2);
			return -1;
		}

		/* Remove comments and spaces at head and tail */
		strrmcomment(buf);
		strrmspace(buf);

		/* Skip blank lines */
		if (buf[0] == '\0') {
			continue;
		}

		/* Split into array of arguments with space separators */
		argc = strsplit(buf, argv, maxargc);

		/* If valid arguments, return */
		if (argv[0][0] != '\0') {
			return argc;
		}
	}

	return 0;
}

/*
 * Print parameter name and arguments if debug mode
 */
void debug_doing_par(int argc, const char **argv)
{
	char buf[CONF_PAR_MAX + 1];

	buf[0] = '\0';
	strjoin(buf, sizeof(buf), argv, 0, argc - 1);
	debug("doing parameter \"%s\"", buf);
}

/*
 * Check if section indicator
 *
 * If arg is a section indicator, return 1 and section name. If arg is not a
 * section indicator, return 0. If error, return -1.
 */
int chksect(const char *arg, char *name, size_t size)
{
	char *s;

	if (arg[0] != '[') {
		return 0;
	}

	name[0] = '\0';
	strncat(name, arg + 1, size - 1);
	if ((s = strrchr(name, ']')) == NULL) {
		error("%s: invalid section indicator -- '%s'", conf_header, arg);
		return -1;
	}
	*s = '\0';
	strtolower(name);

	debug("Processing section \"[%s]\"", name);

	return 1;
}

/*
 * Get n-th subsection name from secton string like "section.subsection".
 * (number starts from 0)
 */
int getsubsect(const char *sect, int n, char *subsect, size_t size)
{
	int i;
	char *s;

	/* Find start of n-th sub-section name */
	s = (char *)sect;
	for (i = 0; i < n; i++) {
		s = strchr(s, '.');
		if (s == NULL) {
			return 0;
		}
		s++;
	}

	/* Copy subsection name */
	subsect[0] = '\0';
	strncat(subsect, s, size - 1);
	if ((s = strchr(subsect, '.')) != NULL) {
		*s = '\0';
	}

	return 1;
}

/*
 * Print "unknown section" warning message
 */
void setpar_unknown_sect(const char *sect)
{
	warn("%s: unknown section -- '%s' (ignored)", conf_header, sect);
}

/*
 * Print "unknown parameter" warning message
 */
void setpar_unknown_par(const char *key)
{
	warn("%s: unknown parameter -- '%s' (ignored)", conf_header, key);
}

/*
 * Print "missing arguments" error message
 */
void setpar_missing_arg(const char *key)
{
	error("%s: missing arguments for '%s' parameter", conf_header, key);
}

/*
 * Print "invalid argument" error message
 */
void setpar_invalid_argument(const char *key, const char *arg)
{
	error("%s: invalid argument for '%s' parameter -- %s", conf_header,
		key, arg);
}

/*
 * Print "too many argument" error message
 */
void setpar_toomany_argument(const char *key)
{
	error("%s: toomany argument for '%s' parameter", conf_header, key);
}

/*
 * Check if i-th argument exists and is not empty
 */
int setpar_chkargi(int argc, const char **argv, int i)
{
	if (argc <= i || *(argv[i]) == '\0') {
		setpar_missing_arg(argv[0]);
		return -1;
	}
	return 0;
}

/*
 * Get a string parameter value w/ allocating memory
 * (index starts from zero, this function returns pointer of new string
 *  the memory of old string will be free, if pointer is not NULL)
 */
int setpar_strdup(int argc, const char **argv, int i, char **valp)
{
	char *s;

	if (setpar_chkargi(argc, argv, i) < 0) {
		return -1;
	} else if ((s = strdup(argv[i])) == NULL) {
		error_num(errno, "%s: cannot allocate memory for string -- %s",
			conf_header, argv[i]);
		return -1;
	} else if (*valp != NULL) {
		free(*valp);
	}
	*valp = s;

	return 1;
}

static const char *setpar_toolong =
	"%s: too long value for '%s' parameter -- '%s' "
	"(must be within %d charactors)";

/*
 * Set a string parameter value w/ copying string (index starts from zero)
 */
int setpar_strcpy(int argc, const char **argv, int i, char *val, size_t size)
{
	size_t max;
	const char *key, *arg;

	if (setpar_chkargi(argc, argv, i) < 0) {
		return -1;
	}
	key = argv[0];
	arg = argv[i];

	max = size - 1;
	if (strlen(arg) > max) {
		error(setpar_toolong, conf_header, key, arg, max);
		return -1;
	}
	val[0] = '\0';
	strncat(val, arg, max);

	return 1;
}

/*
 * Set a string parameter w/ joining arguments
 */
int setpar_strjoin(int argc, const char **argv, char *val, size_t size)
{
	size_t max;
	const char *key;
	char arg[CONF_PAR_MAX + 1];

	if (argc <= 1) {
		setpar_missing_arg(argv[0]);
		return -1;
	}
	key = argv[0];
	arg[0] = '\0';
	strjoin(arg, sizeof(arg), argv, 1, argc - 1);

	max = size - 1;
	if (strlen(arg) > max) {
		error(setpar_toolong, conf_header, key, arg, max);
		return -1;
	}
	val[0] = '\0';
	strncat(val, arg, max);

	return 1;
}

static const char *setpar_inval_int =
	"%s: invalid value for '%s' parameter -- %s: "
	"must be an integer between %ld and %ld";

/*
 * Get a long integer parameter value w/ checking range of value
 */
int setpar_long(int argc, const char **argv, int i, long *val, long min,
	long max)
{
	char *s;
	const char *key, *arg;
	long l;

	if (setpar_chkargi(argc, argv, i) < 0) {
		return -1;
	}
	key = argv[0];
	arg = argv[i];

	errno = 0;
	l = strtol(arg, &s, 10);
	if (errno || *s != '\0'
		|| ((min != 0 || max != 0) && (l < min || l > max))) {
		error(setpar_inval_int, conf_header, key, arg, min, max);
		return -1;
	}
	*val = l;

	return 1;
}

/*
 * Get an unsigned long integer parameter value w/ checking range of value
 */
int setpar_ulong(int argc, const char **argv, int i, unsigned long *val,
	unsigned long min, unsigned long max)
{
	char *s;
	const char *key, *arg;
	unsigned long l;

	if (setpar_chkargi(argc, argv, i) < 0) {
		return -1;
	}
	key = argv[0];
	arg = argv[i];

	errno = 0;
	l = strtoul(arg, &s, 10);
	if (errno || *s != '\0'
		|| ((min != 0 || max != 0) && (l < min || l > max))) {
		error(setpar_inval_int, conf_header, key, arg, min, max);
		return -1;
	}
	*val = l;

	return 1;
}

/*
 * Set an integer parameter value w/ checking range of value
 */
int setpar_int(int argc, const char **argv, int i, int *val, int min, int max)
{
	int ret;
	long l, lmin, lmax;

	if (min == 0 && max == 0) {
		lmin = INT_MIN;
		lmax = INT_MAX;
	} else {
		lmin = min;
		lmax = max;
	}

	if ((ret = setpar_long(argc, argv, i, &l, lmin, lmax)) < 0) {
		return ret;
	}
	*val = l;
	return ret;
}

/*
 * Set an unsigned integer parameter value w/ checking range of value
 */
int setpar_uint(int argc, const char **argv, int i, unsigned int *val,
	unsigned int min, unsigned int max)
{
	int ret;
	ulong l, lmin, lmax;

	if (min == 0 && max == 0) {
		lmin = 0;
		lmax = UINT_MAX;
	} else {
		lmin = min;
		lmax = max;
	}

	if ((ret = setpar_ulong(argc, argv, i, &l, lmin, lmax)) < 0) {
		return ret;
	}
	*val = l;
	return ret;
}

/*
 * Set a 32-bit integer parameter value w/ checking range of value
 */
int setpar_int32(int argc, const char **argv, int i, int32_t *val, int32_t min,
	int32_t max)
{
	int ret;
	long l, lmin, lmax;

	if (min == 0 && max == 0) {
		lmin = INT32_MIN;
		lmax = INT32_MAX;
	} else {
		lmin = min;
		lmax = max;
	}

	if ((ret = setpar_long(argc, argv, i, &l, lmin, lmax)) < 0) {
		return ret;
	}
	*val = l;
	return ret;
}

/*
 * Set a double parameter value w/ checking range of value
 */
int setpar_dbl(int argc, const char **argv, int i, double *val, double min,
	double max)
{
	char *s;
	const char *arg;
	double d;

	if (setpar_chkargi(argc, argv, i) < 0) {
		return -1;
	}
	arg = argv[i];

	errno = 0;
	d = strtod(arg, &s);
	if (errno || *s != '\0'
		|| ((min != 0 || max != 0) && (d < min || d > max))) {
		error("%s: invalid value for '%s' parameter -- %s: "
			"must be a floating point between %g and %g",
			conf_header, argv[0], arg, min, max);
		return -1;
	}
	*val = d;

	return 1;
}

/*
 * Set a float parameter value w/ checking range of value
 */
int setpar_flt(int argc, const char **argv, int i, float *val, float min,
	float max)
{
	char *s;
	const char *arg;
	float d;

	if (setpar_chkargi(argc, argv, i) < 0) {
		return -1;
	}
	arg = argv[i];

	errno = 0;
	d = strtof(arg, &s);
	if (errno || *s != '\0'
		|| ((min != 0 || max != 0) && (d < min || d > max))) {
		error("%s: invalid value for '%s' parameter -- %s: "
			"must be a floating point between %g and %g",
			conf_header, argv[0], arg, min, max);
		return -1;
	}
	*val = d;

	return 1;
}

/*
 * Add an alias item
 */
int setpar_alias(int argc, const char **argv, alias_t *alias)
{
	const char *arg1, *arg2;

	arg1 = argv[1];
	arg2 = argv[2];
	if (argc < 2) {
		error("%s: no enough arguments for '%s' parameter", conf_header,
			argv[0]);
		return -1;
	} else if (alias_add(alias, arg1, arg2) < 0) {
		error_num(errno, "%s: cannot add alias \"%s %s\"", conf_header,
			arg1, arg2);
		return -1;
	}

	return 1;
}
