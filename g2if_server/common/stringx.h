/*
 * stringx.h -- Definitions for functions dealing with string
 *
 * Written by Makoto WATANABE
 */

#ifndef _STRINGX_H
#define _STRINGX_H

#define YESNO(x)	( (x) ? "YES" : "NO" )
#define ONOFF(x)	( (x) ? "ON" : "OFF" )
#define onoff(x)	( (x) ? "on" : "off" )
#define OPENCLOSE(x)	( (x) ? "OPEN" : "CLOSE" )
#define openclose(x)	( (x) ? "open" : "close" )

#ifdef __cplusplus
extern "C" {
#endif

/* Function prototypes */

int strsplit(char *str, char **fields, size_t max_fields);
int strsplit_delim(char *str, char **fields, char *delim, size_t max_fields);
int strisint(const char *str);
char *strtolower(char *str);
char *strtoupper(char *str);
char *strrmcrlf(char *str);
char *strrmspace(char *str);
char *strspecial(char *dest, size_t size, const char *src);
char *strncatx(char *str1, size_t size, const char *str2);
char *strncatf(char *str, size_t size, const char *format, ...);
char *strjoin(char *str, size_t size, const char **argv, size_t first,
	size_t end);

#ifdef __cplusplus
}
#endif

#endif /* _STRINGX_H */
