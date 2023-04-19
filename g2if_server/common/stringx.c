/*
 * stringx.c -- Functions for dealing with string
 *
 * Written by Makoto WATANABE
 */

#include <stdio.h>				/* for snprintf() */
#include <stdarg.h>				/* for va_start(), va_end() */
#include <string.h>				/* for strspn(), memmove() */
#include <ctype.h>				/* for isdigit(), tolower() */
#include "stringx.h"

/*
 * Split a string into fields separated by spaces (space, \t, \f, \n, \r, \v).
 *
 * This function modifies the input string, putting '\0' into the string,
 * and returns the number of fields and pointers of heads of fields.
 * The spaces at head and end of string are removed. The string sandwiched
 * between a pair of quote charactors (' and ") not be separated into fields,
 * but the pair of quote charactors are removed.
 */
int strsplit(char *str, char **fields, size_t max_fields)
{
	size_t i, n, k, newf;
	int quote;
	char c, *s;

	/* Clear field pointers to NULL, but first one points start of string */
	fields[0] = str;
	for (i = 1; i < max_fields; i++) {
		fields[i] = NULL;
	}

	/* Clear spaces and quote into '\0', scanning fields */
	newf = 1;			/* flag indicating searching start of field */
	n = 0;				/* number of fields */
	k = 0;				/* amount of shift to remove quote charactors */
	quote = 0;			/* quote charactor */
	for (s = str; (c = *s); s++) {
		if (quote) {				/* inside of quote */
			if (c == quote) {				/* end of quote */
				quote = 0;
				k++;
			} else {
				*(s - k) = c;				/* shift charactor */
			}
		} else {					/* outside of quote */
			if (isspace(c)) {				/* end of field */
				newf = 1;
				*(s - k) = '\0';
				k = 0;
			} else if (newf) {				/* start of field */
				newf = 0;
				k = 0;
				if (n < max_fields) {
					fields[n] = s;
					n++;
				}
			} else if (k > 0) {				/* in field, but need shift */
				*(s - k) = c;
			}

			if (c == '\'' || c == '\"') {	/* start of quote */
				quote = c;
				k++;
			}
		}
	}

	/* Set '\0' for last field */
	if (k > 0) {
		*(s - k) = '\0';
	}

	return n;
}

/*
 * Check if string means an integer number (digits only or sign + digits)
 */
int strisint(const char *str)
{
	char c;

	if (*str == '+' || *str == '-') {
		str++;
	}

	if (*str == '\0') {
		return 0;
	}

	for (; (c = *str); str++) {
		if (!isdigit(c)) {
			return 0;
		}
	}

	return 1;
}

/*
 *	Convert letters into lower case in string
 */
char *strtolower(char *str)
{
	char *c;

	for (c = str; *c; c++) {
		*c = tolower(*c);
	}

	return str;
}

/*
 *	Convert letters into lower case in string
 */
char *strtoupper(char *str)
{
	char *c;

	for (c = str; *c; c++) {
		*c = toupper(*c);
	}

	return str;
}

/*
 * Remove CR and LF charactors at end of string
 */
char *strrmcrlf(char *str)
{
	size_t i, n;
	char c, *s;

	/* Get length of str and goto end of string */
	n = 0;
	for (s = str; *s; s++) {
		n++;
	}

	/* Remove CR and LF from end */
	for (i = 0; i < n; i++) {
		s--;
		c = *s;
		if (c != '\n' && c != '\r') {
			break;
		}
		*s = '\0';
	}

	return str;
}

/*
 * Remove spaces (space, \t, \f, \n ,\r, \v) at head and tail of string
 */
char *strrmspace(char *str)
{
	size_t i, n;
	char c, *s;
	const char *spaces = " \t\f\n\r\v";

	/* Get length of str and goto end of string */
	n = 0;
	for (s = str; *s; s++) {
		n++;
	}

	/* Remove space charactors from end */
	for (i = 0; i < n; i++) {
		s--;
		c = *s;
		if (!isspace(c)) {
			break;
		}
		*s = '\0';
	}

	i = strspn(str, spaces);
	if (i > 0) {
		memmove(str, str + i, n - i + 1);
	}

	return str;
}

/*
 *	Conversion special charactors into a string with format "<%02X>"
 */
char *strspecial(char *dest, size_t size, const char *src)
{
	const char *s1, *hex = "0123456789ABCDEF";
	char c, *s2 = dest;

	for (s1 = src; (c = *s1); s1++) {
		if (size <= 1) {
			break;
		} else if (isprint(c)) {
			*s2 = c;
			s2++;
			size--;
			continue;
		} else if (size <= 4) {
			break;
		} else {
			*s2 = '<';
			s2++;
			*s2 = hex[(c >> 4) & 0xf];
			s2++;
			*s2 = hex[c & 0xf];
			s2++;
			*s2 = '>';
			s2++;
			size -= 4;
		}
	}

	if (size > 0) {
		*s2 = '\0';
	}

	return dest;
}

/*
 * Concatenate one string at end of other string
 * (size is buffer size of str1)
 */
char *strncatx(char *str1, size_t size, const char *str2)
{
	char c, *s1;
	const char *s2;
	size_t n;

	/* Find end of string */
	n = 1;
	for (s1 = str1; *s1; s1++) {
		n++;
	}

	/* If buffer is full, return */
	if (size < n) {
		return str1;
	}
	size -= n;

	/* Copy string */
	for (s2 = str2; (c = *s2); s2++) {
		if (size == 0) {
			break;
		}
		*s1 = c;
		s1++;
		size--;
	}
	*s1 = '\0';

	return str1;
}

/*
 * Concatenate one formatted string at end of other string
 * (size is buffer size of str)
 */
char *strncatf(char *str, size_t size, const char *format, ...)
{
	char buf[4096];
	va_list ap;

	va_start(ap, format);
	vsnprintf(buf, sizeof(buf), format, ap);
	va_end(ap);

	return strncatx(str, size, buf);
}

/*
 * Join strings in array into a string with a space charactor
 */
char *strjoin(char *str, size_t size, const char **argv, size_t first,
	size_t end)
{
	size_t i, n;
	char c, *s1;
	const char *s2;

	/* Find end of string */
	n = 1;
	for (s1 = str; *s1; s1++) {
		n++;
	}

	/* If buffer is full, return */
	if (size < n) {
		return str;
	}
	size -= n;

	/* Append first string */
	for (s2 = argv[first]; (c = *s2); s2++) {
		if (size == 0) {
			break;
		}
		*s1 = c;
		s1++;
		size--;
	}

	/* Append rest strings w/ an blank separators */
	for (i = first + 1; i <= end; i++) {
		if (size == 0) {
			break;
		}
		*s1 = ' ';
		s1++;
		size--;
		for (s2 = argv[i]; (c = *s2); s2++) {
			if (size == 0) {
				break;
			}
			*s1 = c;
			s1++;
			size--;
		}
	}
	*s1 = '\0';

	return str;
}

int strsplit_delim(char *str, char **fields, char *delim, size_t max_fields){
    size_t i, n, newf;
    char c, *s;
    int flag;

    /* Clear field pointers to NULL, but first one points start of string */
    fields[0] = str;
    for (i = 1; i < max_fields; i++) {
	fields[i] = NULL;
    }

    /* Clear spaces and quote into '\0', scanning fields */
    newf = 1;	/* flag indicating searching start of field */
    n = 0;	/* number of fields */
    flag = 0;   /* flag indicating delimit character */
    for (s = str; (c = *s); s++) {

	for(i=0;i<strlen(delim);i++){
	    if (c == delim[i]) {
		flag = 1;
	    }
	}
	
	if (flag) {	/* end of field */
	    flag = 0;
	    newf = 1;
	    *s = '\0';
	} else if (newf) {	/* start of field */
	    newf = 0;
	    if (n < max_fields) {
		fields[n] = s;
		n++;
	    }
	}
    }

    return n;
}
