/*
 * log.h -- Definitions for logging functions
 *
 * Written by Makoto WATANABE
 */

#ifndef _LOG_H
#define _LOG_H

/* Log levels */

enum {
	LOG_ERR,
	LOG_WARN,
	LOG_INFO,
	LOG_DEBUG,
};

/* Header string of error/warning message */

#define LOG_HEAD_ERR	"Error"
#define LOG_HEAD_WARN	"Warning"

/* Buffer size of log message */

enum {
	LOG_MSG_BUFSIZ = 1024,
};

#ifdef __cplusplus
extern "C" {
#endif

/* Function prototypes */

int setlogfile(const char *path);
int setlogterm(int use);
int setloglevel(int level);
int logisprint(int priority);
int putlog(int priority, const char *format, ...);
int error_num(int errnum, const char *format, ...);

#define error(...) putlog(LOG_ERR, __VA_ARGS__)
#define warn(...) putlog(LOG_WARN, __VA_ARGS__)
#define info(...) putlog(LOG_INFO, __VA_ARGS__)
#define debug(...) putlog(LOG_DEBUG, __VA_ARGS__)
#define debugisprint(x) logisprint(LOG_DEBUG)

#ifdef __cplusplus
}
#endif

#endif /* _LOG_H */
