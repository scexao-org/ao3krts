/* -------------------------------------------------------------------------
 * server.h -- Definitions for functions for server program
 * -------------------------------------------------------------------------
 * Time-stamp: <2010-12-07 01:00:55 ao> 
 * -------------------------------------------------------------------------
 * Update History:
 * <Date>       <Who>         <What>    
 * 2008          M. Watanabe   Initial version
 * 2010/12/07    Y. Minowa     Add global constant "server_conffile_name"
 * 2019/04/16    Y.Ono         Added getargv_flt for float
 * -------------------------------------------------------------------------
 */
#ifndef _SERVER_H
#define _SERVER_H

#include <sys/types.h> 			/* for pid_t */
#include <netinet/in.h> 		/* for struct sockaddr_in */
#include <pthread.h> 			/* pthread_mutex_t */
#include "alias.h" 				/* alias_t */
#include "tpool.h" 				/* tpool_t */
#include "servif.h"


/* Constant for storing the configuration file name */
const char *server_conffile_name;
pthread_mutex_t server_conffile_lock;

/* Default values of server configuration */

enum {
	CONNMAX 	= 5,	/* default maximum number of client connections */
	THREADS_MIN = 5,	/* default minimum number of worker threads */
	THREADS_MAX = 30,	/* default maximum number of worker threads */
	LINGER 		= 60,	/* default linger period (in seconds) */
};

/* Structure to store server data */

typedef struct server {
	pid_t pid;			/* process id */
	char *addr;			/* address for listen */
	int port;			/* TCP port number for listen */
	int sockfd;			/* socket descriptor */
	int connmax;		/* maximum number of client connections */
	int connnum;		/* number of client connections */
	int dump;			/* flag to control on/off of dump of communication */
	int thmin;			/* mimimum number of worker threads */
	int thmax;			/* maximum number of worker threads */
	int linger;			/* linger period (in seconds) to close idle threads */
	tpool_t tpool;				/* worker thread pool */
	char *logfile;				/* logfile name */
	pthread_mutex_t lock;		/* lock of data */
	int num_devs;				/* number of devices */
	struct device *devs;		/* pointer of array of devices */
	alias_t alias;				/* alias name of device */
} server_t;

/* Structure to store client data */

typedef struct client {
	char *addr;						/* address */
	int port;						/* TCP port number */
	int sockfd;						/* socket descriptor */
	int argc;						/* number of arguments */
	char *argv[CMDARGC_MAX];		/* pointer to command arguments */
	char cmdstr[CMDSTR_MAX + 1];	/* buffer for command string */
	server_t *server;				/* Pointer to server data */
} client_t;

/* Structure to store option parameters of server configuration */

struct server_option {
	const char *title;				/* title message */
	const char *conffile;			/* configuration file name */
	const char *logfile;			/* log file name */
	const char *addr;				/* hostname to bind */
	int port;						/* port number to listen */
	int num_devs;					/* number of devices */
	struct device *devs;			/* pointer to array of devices */
};

#ifdef __cplusplus
extern "C" {
#endif

/* Function prototypes */

int server_main(struct server_option *servopt, int argc, char **argv);

int sendres(client_t *client, const char *format, ...);
int sendres_hsect(client_t *client, const char *sect);
int sendres_hitem(client_t *client, const char *cmd, const char *desc);
int sendres_error(client_t *client, const char *format, ...);
int sendres_unknown_dev(client_t *client, const char *dev);
int sendres_unknown_cmd(client_t *client, const char *cmd);
int sendres_missing_arg(client_t *client);
int sendres_invalid_arg(client_t *client, const char *arg);

int getargc(client_t *client);
char *getargv(client_t *client, int i);
int getargv_strjoin(client_t *client, int i, char *val, size_t size);
int getargv_long(client_t *client, int i, long *val, long min, long max);
int getargv_ulong(client_t *client, int i, unsigned long *val,
	unsigned long min, unsigned long max);
int getargv_int(client_t *client, int i, int *val, int min, int max);
int getargv_uint(client_t *client, int i, unsigned int *val, unsigned int min,
	unsigned int max);
int getargv_int32(client_t *client, int i, int32_t *val, int32_t min,
	int32_t max);
int getargv_longhex(client_t *client, int i, long *val, long min, long max);
int getargv_inthex(client_t *client, int i, int *val, int min, int max);
int getargv_dbl(client_t *client, int i, double *val, double min, double max);
int getargv_flt(client_t *client, int i, float *val, float min, float max);

#ifdef __cplusplus
}
#endif

#endif /* _SERVER_H */
