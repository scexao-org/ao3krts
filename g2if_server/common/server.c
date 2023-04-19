/* -------------------------------------------------------------------------
 * server.c -- Functions for server program receiving requests via socket
 * -------------------------------------------------------------------------
 * Time-stamp: <2011-06-06 21:37:21 ao> 
 * -------------------------------------------------------------------------
 * Update History:
 * <Date>       <Who>         <What>    
 * 2008          M. Watanabe   Initial version
 * 2010/12/07    Y. Minowa     Modified to record configuration in a global 
 *                             constant (server_conffile_name)
 * 2019/04/11    Y. Ono        Fixed a bag in server_procreq
 *                             Modified server_procconf to accept "hostname"
 *                             instead of "addr".
 * 2019/04/16    Y.Ono         Added getargv_flt for float
 * -------------------------------------------------------------------------
 */
#ifndef _GNU_SOURCE
#define _GNU_SOURCE				/* for program_invocation_short_name */
#endif /* _GNU_SOURCE */

#include <unistd.h>				/* for getopt(), close() */
#include <stdio.h>				/* for fopen(), fclose(), snprintf() */
#include <stdlib.h> 			/* for malloc(), free() */
#include <stdarg.h> 			/* for va_list, va_start(), va_end() */
#include <string.h> 			/* for strlen() */
#include <signal.h> 			/* for sigemptyset(), sigaddset() */
#include <pthread.h>			/* for pthread_*() */
#include <sys/types.h>			/* for pid_t, bind(), listen(), accept() */
#include <sys/socket.h> 		/* for bind(), listen(), accept() */
#include <netinet/in.h> 		/* for struct sockaddr_in */
#include <netinet/tcp.h>		/* for TCP_NODELAY */
#include <arpa/inet.h>			/* for inet_ntoa() */
#include <errno.h>				/* for errno */
#include <limits.h>
#include "log.h"				/* for error(), info(), debug() */
#include "alias.h"				/* for alias_t, alias_*() */
#include "conf.h"				/* for setpar_strdup(), setpar_int() */
#include "device.h"				/* for struct device, device_*() */
#include "socket.h" 			/* for recvstr() */
#include "stringx.h"			/* for strsplit() */
#include "tpool.h"				/* for tpool_t, tpool_*() */
#include "servif.h"
#include "server.h"
#include "tool.h"                       /* for get_ip() */

#ifdef progname
#undef progname
#endif
#define progname program_invocation_short_name

static int server_shutdown_flag = 0;	/* shutdown flag */

static const char *server_header = "server";

/*
 * Initialize server data
 */
static int server_init(server_t *server)
{
	debug("%s: init", server_header);

	server->pid = getpid();
	server->addr = NULL;
	server->sockfd = -1;
	server->connmax = CONNMAX;
	server->connnum = 0;
	server->dump = 0;
	server->thmin = THREADS_MIN;
	server->thmax = THREADS_MAX;
	server->linger = LINGER;
	server->tpool = NULL;
	server->logfile = NULL;
	server->num_devs = 0;
	server->devs = NULL;
	if (alias_init(&(server->alias)) < 0) {
		return -1;
	}
	pthread_mutex_init(&(server->lock), NULL);

	return 0;
}

/*
 * Free resources in server data
 */
static int server_free(server_t *server)
{
	debug("%s: free", server_header);

	if (server->tpool != NULL) {
		tpool_destroy(server->tpool, 0);
	}
	free(server->addr);
	server->addr = NULL;
	free(server->logfile);
	server->logfile = NULL;
	alias_free(&(server->alias));
	pthread_mutex_destroy(&(server->lock));

	return 0;
}

/*
 * Process a configuration parameter for server
 */
static int server_procconf(server_t *server, const char *sect, int argc,
	const char **argv)
{
	char subsect[32];
	const char *key = argv[0];
	char **ip;

	if (getsubsect(sect, 1, subsect, sizeof(subsect))) {
	        setpar_unknown_sect(sect);
		return 0;
	} else if (strcmp(key, "addr") == 0) {		/* ip address */
	        return setpar_strdup(argc, argv, 1, &(server->addr));
	} else if (strcmp(key, "hostname") == 0) {		/* hostname */
	        ip = (char**)malloc(sizeof(char*));
	        ip[0] = (char*)malloc(sizeof(char)*100);
	        get_ip(argv[1], ip[0]);
		return setpar_strdup(1, (const char**)ip, 0, &(server->addr));
	} else if (strcmp(key, "port") == 0) {		/* port number */
		return setpar_int(argc, argv, 1, &(server->port), 0, USHRT_MAX);
	} else if (strcmp(key, "connmax") == 0) {	/* maximum connections */
		return setpar_int(argc, argv, 1, &(server->connmax), 0, USHRT_MAX);
	} else if (strcmp(key, "dump") == 0) {		/* dump flag */
		return setpar_int(argc, argv, 1, &(server->dump), 0, 1);
	} else if (strcmp(key, "thmin") == 0) {		/* minimum threads */
		return setpar_int(argc, argv, 1, &(server->thmin), 0, USHRT_MAX);
	} else if (strcmp(key, "thmax") == 0) {		/* maximum threads */
		return setpar_int(argc, argv, 1, &(server->thmax), 2, USHRT_MAX);
	} else if (strcmp(key, "linger") == 0) {	/* linger period */
		return setpar_int(argc, argv, 1, &(server->linger), 2, USHRT_MAX);
	} else if (strcmp(key, "logfile") == 0) {	/* logfile */
		return setpar_strdup(argc, argv, 1, &(server->logfile));
	} else if (strcmp(key, "alias") == 0) {		/* alias names of devices */
		return setpar_alias(argc, argv, &(server->alias));
	}
	setpar_unknown_par(key);
	return 0;
}

/*
 * Do post processing of configuration parameters of server
 */
static void server_postconf(server_t *server)
{
	/* Print configuration parameters of server */
	info("%s: addr = \"%s\"", server_header, server->addr);
	info("%s: port = %d", server_header, server->port);
	info("%s: connmax = %d", server_header, server->connmax);
	info("%s: dump = %d", server_header, server->dump);
	info("%s: thmin = %d", server_header, server->thmin);
	info("%s: thmax = %d", server_header, server->thmax);
	info("%s: linger = %d", server_header, server->linger);
	info("%s: logfile = \"%s\"", server_header, server->logfile);
}

/*
 * Read configuration paramters from file
 */
static int readconf(const char *filename, server_t *server)
{
	int ret, argc, sectcode, num_devs;
	char buf[CONF_PAR_MAX + 2];
	char sect[CONF_PAR_MAX + 1], sectmain[CONF_PAR_MAX + 1];
	const char *key, *argv[CONF_ARGC_MAX];
	struct device *dev, *devs;
	FILE *fp;

	num_devs = server->num_devs;
	devs = server->devs;
	dev = NULL;

	/* Open config file */
	if ((fp = fopen(filename, "r")) == NULL) {
		error("%s: cannot open config file (%s)", server_header, filename);
		return -1;
	}

	/* Print messgae */
	info("%s: reading parameters from configuration file (%s)", server_header,
		filename);

	sectcode = -1;
	sect[0] = '\0';
	while ((ret = getconfpar(fp, buf, sizeof(buf), (char **)argv, CONF_ARGC_MAX)) > 0) {

		argc = ret;
		key = argv[0];

		/* Check if section indicator */
		if ((ret = chksect(key, sect, sizeof(sect))) < 0) {
			break;
		} else if (ret > 0) {

			/* Get main section name */
			getsubsect(sect, 0, sectmain, sizeof(sectmain));

			if (strcmp(sectmain, "server") == 0) {
				sectcode = 0;
			} else if ((dev = device_getdev(devs, num_devs, sectmain)) != NULL) {
				sectcode = 1;
			} else {
				sectcode = -1;
				setpar_unknown_sect(sect);
			}
			continue;
		}

		/* Print parameter name and arguments if debug mode */
		debug_doing_par(argc, argv);

		/* Parse parameters */
		switch (sectcode) {

		case 0:
			ret = server_procconf(server, sect, argc, argv);
			break;
		case 1:
			ret = device_procconf(dev, sect, argc, argv);
			break;
		case -1:
			setpar_unknown_par(key);
			break;
		}

		if (ret < 0) {
			break;
		}
	}

	fclose(fp);

	return ret;
}

/*
 * Bind socket to server address, and listen on it
 */
static int listensock(const char *hostname, int port, int maxconn)
{
	int sockfd, saved_errno;
	struct sockaddr_in sin;

	/* Get a socket and setup sockaddr for server */
	if ((sockfd = getsock(&sin, hostname, port)) < 0) {
		error_num(errno, "%s: cannot get socket (addr = %s, port = %d)",
			server_header, hostname, port);
		return sockfd;
	}
	printf("hostname:%s\n",hostname);
	printf("port:%d\n",port);
	/* Bind server address to socket */
	if (bind(sockfd, (struct sockaddr *)&sin, sizeof(sin)) < 0) {
		error_num(errno, "%s: cannot bind address to socket (sockfd = %d)",
			  server_header, sockfd);
		saved_errno = errno;
		close(sockfd);
		errno = saved_errno;
		return -1;
	}

	/* Listen on the socket */
	if (listen(sockfd, maxconn) < 0) {
		error_num(errno, "%s: cannot start listen (sockfd = %d, maxconn = %d)",
			server_header, sockfd, maxconn);
		saved_errno = errno;
		close(sockfd);
		errno = saved_errno;
		return -1;
	}

	return sockfd;
}

/*
 * Start server (create thread pool and listen socket)
 */
static int server_start(server_t *server)
{
	/* Get server pid */
	server->pid = getpid();

	debug("%s: start (pid = %d)", server_header, server->pid);

	/* Create thread pool for worker threads */
	if (tpool_init(&(server->tpool), server->thmin, server->thmax,
		server->connmax * 2, server->linger) < 0) {
		return -1;
	}

	/* Listen socket */
	if ((server->sockfd = listensock(server->addr, server->port,
		server->connmax)) < 0) {
		tpool_destroy(server->tpool, 0);
		server->tpool = NULL;
		return -1;
	}

	debug("%s: listen socket (sockfd = %d, addr = %s, port = %d)",
		server_header, server->sockfd, server->addr, server->port);

	info("%s: listening for client connections on %s port %d",
		server_header, server->addr, server->port);

	return 0;
}

/*
 * Shutdown server (destroy thread pool and close server socket)
 */
static int server_shutdown(server_t *server)
{
	int sockfd;
	tpool_t tpool;

	debug("%s: shutdown (pid = %d)", server_header, server->pid);

	/* Wait for finishing works, then destroy threads */
	tpool = server->tpool;
	if (tpool != NULL) {
		tpool_destroy(tpool, 1);
		server->tpool = NULL;
	}

	/* Close server socket */
	sockfd = server->sockfd;
	if (sockfd != -1) {
		debug("%s: close socket (sockfd = %d)", server_header, server->sockfd);
		close(sockfd);
		server->sockfd = -1;
	}

	return 0;
}

/*
 * Set server dump flag
 */
static int server_setdump(server_t *server, int dump)
{
	pthread_mutex_lock(&(server->lock));
	server->dump = dump;
	pthread_mutex_unlock(&(server->lock));

	return 0;
}

/*
 * Get server dump flag
 */
static int server_getdump(server_t *server)
{
	int dump;

	pthread_mutex_lock(&(server->lock));
	dump = server->dump;
	pthread_mutex_unlock(&(server->lock));

	return dump;
}

/*
 * Receive a command string from client
 */
static int recvcmd(client_t *client, char *cmdstr, size_t size)
{
	int ret;
	char buf[CMDSTR_MAX * 4 + 1];

	/*
	 * Wait until receive a string ending charactor 'CR' from client.
	 * If return value is 0, connection is closed.
	 */
	ret = recvstr(client->sockfd, cmdstr, size, "\r", -1);
	if (ret <= 0) {
		if (ret < 0) {
			error_num(errno,
				"%s: cannot receive command from client (sockfd = %d)",
				server_header, client->sockfd);
		}
		return ret;
	}

	/* Logging command string if dump on */
	if (server_getdump(client->server)) {
		info("%s:%d >> %s", client->addr, client->port,
			strspecial(buf, sizeof(buf), cmdstr));
	}

	return ret;
}

/*
 * Check cancellation signal of command from client
 */
static int chkcancel(client_t *client)
{
	int ret;
	char cmdstr[CMDSTR_MAX + 1], buf[CMDSTR_MAX * 4 + 1];

	/* Get data from client */
	ret = recvdata(client->sockfd, cmdstr, sizeof(cmdstr), 0);
	if (ret <= 0) {
		return ret;
	}

	/* Logging received data */
	cmdstr[ret] = '\0';
	if (server_getdump(client->server)) {
		info("%s:%d >> %s", client->addr, client->port,
			strspecial(buf, sizeof(buf), cmdstr));
	}

	/* Check receiving of cancel character */
	if (strchr(cmdstr, CLIENT_CAN) != NULL) {
		debug("%s: client cancelled command (sockfd = %d, addr = %s, port = %d)",
			server_header, client->sockfd,  client->addr, client->port);
		return 1;
	}

	return 0;
}

/*
 * Send message to client
 */
int sendres(client_t *client, const char *format, ...)
{
	size_t n;
	char c, msg[RESSTR_MAX + 1], line[RESSTR_MAX + 1], buf[RESSTR_MAX + 1];
	const char *s;
	va_list ap;

	/* Get formatted string */
	va_start(ap, format);
	vsnprintf(msg, sizeof(msg), format, ap);
	va_end(ap);

	/* Send response string to client */
	if (send(client->sockfd, msg, strlen(msg), 0) < 0) {
		error_num(errno, "%s: cannot send data to client (sockfd = %d)",
			server_header, client->sockfd);
		return -1;
	}

	/* If debug output is disable, skip below */
	if (server_getdump(client->server) == 0) {
		return 0;
	}

	/* Print message strings line by line as debugging message */
	n = 0;
	for (s = msg; (c = *s); s++) {
		if (c == '\n' && n > 0) {
			line[n] = '\0';
			info("%s:%d << %s", client->addr, client->port,
				strspecial(buf, sizeof(buf), line));
			n = 0;
		} else {
			line[n] = c;
			n++;
		}
	}
	if (n > 0) {
		line[n] = '\0';
		info("%s:%d << %s", client->addr, client->port,
				strspecial(buf, sizeof(buf), line));
	}

	return 0;
}

/*
 * Send a section header for help command
 */
int sendres_hsect(client_t *client, const char *sect)
{
	return sendres(client, "  %s:\n", sect);
}

/*
 * Send a help item for help command
 */
int sendres_hitem(client_t *client, const char *cmd, const char *desc)
{
	return sendres(client, "    %-22s  %s\n", cmd, desc);
}

/*
 * Send error message client
 */
int sendres_error(client_t *client, const char *format, ...)
{
	char msg[RESSTR_MAX + 1];
	va_list ap;

	/* Get formatted string */
	va_start(ap, format);
	vsnprintf(msg, sizeof(msg), format, ap);
	va_end(ap);

	/* Add error header */
	return sendres(client, RES_HEAD_ERR"%s\n", msg);
}

/*
 * Send "unknown device" error massage to client
 */
int sendres_unknown_dev(client_t *client, const char *dev)
{
	return sendres(client, RES_HEAD_ERR"unknown device -- %s\n", dev);
}

/*
 * Send "unknown command" error massage to client
 */
int sendres_unknown_cmd(client_t *client, const char *cmd)
{
	return sendres(client, RES_HEAD_ERR"unknown command -- %s\n", cmd);
}

/*
 * Send "missing argument" error massage to client
 */
int sendres_missing_arg(client_t *client)
{
	return sendres(client, RES_HEAD_ERR"missing argument\n");
}

/*
 * Send "invalid argument" error massage to client
 */
int sendres_invalid_arg(client_t *client, const char *arg)
{
	return sendres(client, RES_HEAD_ERR"invalid argument -- %s\n", arg);
}

/*
 * Get number of arguments of command string from client
 */
int getargc(client_t *client)
{
	return client->argc;
}

/*
 * Get i-th argument of command string from client
 */
char *getargv(client_t *client, int i)
{
	return client->argv[i];
}

static const char *getargv_toolong =
	RES_HEAD_ERR"too long value -- %s (must be within %d charactors)\n";

/*
 * Get a string parameter w/ joining arguments
 */
int getargv_strjoin(client_t *client, int i, char *val, size_t size)
{
	size_t max;
	char arg[CMDSTR_MAX + 1];

	if (client->argc <= i) {
		sendres_missing_arg(client);
		return -1;
	}
	arg[0] = '\0';
	strjoin(arg, sizeof(arg), (const char **)client->argv, i,
		client->argc - 1);

	max = size - 1;
	if (strlen(arg) > max) {
		sendres(client, getargv_toolong, arg, max);
		return -1;
	}
	val[0] = '\0';
	strncat(val, arg, max);

	return 0;
}

static const char *getargv_inval_long =
	RES_HEAD_ERR"invalid value -- %s (must be an integer)\n";
static const char *getargv_inval_long_rng =
	RES_HEAD_ERR"invalid value -- %s (must be an integer between %ld and %ld)\n";

/*
 * Get a long integer value by converting i-th argument of command string
 */
int getargv_long(client_t *client, int i, long *val, long min, long max)
{
	char *arg, *s;
	long l;

	if (client->argc <= i) {
		sendres_missing_arg(client);
		return -1;
	}
	arg = client->argv[i];

	errno = 0;
	l = strtol(arg, &s, 10);
	if (errno || *s != '\0'
		|| ((min != 0 || max != 0) && (l < min || l > max))) {
		if (min != 0 || max != 0) {
			sendres(client, getargv_inval_long_rng, arg, min, max);
		} else {
			sendres(client, getargv_inval_long, arg);
		}
		return -1;
	}
	*val = l;

	return 0;
}

/*
 * Get an unsigned long integer value by converting i-th argument of command
 * string
 */
int getargv_ulong(client_t *client, int i, unsigned long *val,
	unsigned long min, unsigned long max)
{
	char *arg, *s;
	unsigned long l;

	if (client->argc <= i) {
		sendres_missing_arg(client);
		return -1;
	}
	arg = client->argv[i];

	errno = 0;
	l = strtol(arg, &s, 10);
	if (errno || *s != '\0'
		|| ((min != 0 || max != 0) && (l < min || l > max))) {
		if (min != 0 || max != 0) {
			sendres(client, getargv_inval_long_rng, arg, min, max);
		} else {
			sendres(client, getargv_inval_long, arg);
		}
		return -1;
	}
	*val = l;

	return 0;
}

/*
 * Get an integer value by converting i-th argument of command string
 */
int getargv_int(client_t *client, int i, int *val, int min, int max)
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

	if ((ret = getargv_long(client, i, &l, lmin, lmax)) < 0) {
		return ret;
	}
	*val = l;
	return ret;
}

/*
 * Get an integer value by converting i-th argument of command string
 */
int getargv_uint(client_t *client, int i, unsigned int *val, unsigned int min,
	unsigned int max)
{
	int ret;
	unsigned long l, lmin, lmax;

	if (min == 0 && max == 0) {
		lmin = 0;
		lmax = UINT_MAX;
	} else {
		lmin = min;
		lmax = max;
	}

	if ((ret = getargv_ulong(client, i, &l, lmin, lmax)) < 0) {
		return ret;
	}
	*val = l;
	return ret;
}

/*
 * Get a 32-bit integer value by converting i-th argument of command string
 */
int getargv_int32(client_t *client, int i, int32_t *val, int32_t min,
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

	if ((ret = getargv_long(client, i, &l, lmin, lmax)) < 0) {
		return ret;
	}
	*val = l;
	return ret;
}

static const char *getargv_inval_longhex =
	RES_HEAD_ERR"invalid value -- %s (must be an integer in hexadecimal)\n";
static const char *getargv_inval_longhex_rng =
	RES_HEAD_ERR"invalid value -- %s (must be an integer between 0x%lx and 0x%lx)\n";

/*
 * Get a long integer value in hexadecimal by converting i-th argument of
 * command string
 */
int getargv_longhex(client_t *client, int i, long *val, long min, long max)
{
	char *arg, *s;
	long l;

	if (client->argc <= i) {
		sendres_missing_arg(client);
		return -1;
	}
	arg = client->argv[i];

	errno = 0;
	l = strtol(arg, &s, 16);
	if (errno || *s != '\0'
		|| ((min != 0 || max != 0) && (l < min || l > max))) {
		if (min != 0 || max != 0) {
			sendres(client, getargv_inval_longhex_rng, arg, min, max);
		} else {
			sendres(client, getargv_inval_longhex, arg);
		}
		return -1;
	}
	*val = l;

	return 0;
}

/*
 * Get an integer value in hexadecimal by converting i-th argument of command
 * string
 */
int getargv_inthex(client_t *client, int i, int *val, int min, int max)
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

	if ((ret = getargv_longhex(client, i, &l, lmin, lmax)) < 0) {
		return ret;
	}
	*val = l;
	return ret;
}

/*
 * Get a double value by converting i-th argument of command string
 */
int getargv_dbl(client_t *client, int i, double *val, double min, double max)
{
	char *arg, *s;
	double d;

	if (client->argc <= i) {
		sendres_missing_arg(client);
		return -1;
	}
	arg = client->argv[i];

	errno = 0;
	d = strtod(arg, &s);
	if (errno || *s != '\0'
		|| ((min != 0 || max != 0) && (d < min || d > max))) {
		if ((min != 0 || max != 0)) {
			sendres(client, RES_HEAD_ERR"invalid value -- %s "
				"(must be a floating point between %g and %g)\n",
				arg, min, max);
		} else {
			sendres(client, RES_HEAD_ERR
				"invalid value -- %s (must be a floating point)\n", arg);
		}
		return -1;
	}
	*val = d;

	return 0;
}

/*
 * Get a float value by converting i-th argument of command string
 */
int getargv_flt(client_t *client, int i, float *val, float min, float max)
{
	char *arg, *s;
	float d;

	if (client->argc <= i) {
		sendres_missing_arg(client);
		return -1;
	}
	arg = client->argv[i];

	errno = 0;
	d = strtof(arg, &s);
	if (errno || *s != '\0'
		|| ((min != 0 || max != 0) && (d < min || d > max))) {
		if ((min != 0 || max != 0)) {
			sendres(client, RES_HEAD_ERR"invalid value -- %s "
				"(must be a floating point between %g and %g)\n",
				arg, min, max);
		} else {
			sendres(client, RES_HEAD_ERR
				"invalid value -- %s (must be a floating point)\n", arg);
		}
		return -1;
	}
	*val = d;

	return 0;
}

/*
 * Process server help command
 */
static int server_proccmd_help(client_t *client, server_t *server)
{
	int i, n;
	struct device *dev, *devs;

	n = server->num_devs;
	devs = server->devs;

	sendres(client, "Usage: <command> [<argument>]\n");
	sendres(client, "    or <device> <command> [<argument>]\n");
	sendres_hsect(client, "devices");
	for (i = 0; i < n; i++) {
		dev = &(devs[i]);
		sendres_hitem(client, dev->name, dev->desc);
	}
	sendres_hsect(client, "commands and arguments");
	sendres_hitem(client, "debug {on|off}", "turn debug output on/off");
	sendres_hitem(client,
		"dump {on|off}", "turn on/off dump of communication with clients");
	sendres_hitem(client, "quit", "close connection");
	sendres_hitem(client, "help", "show help message");

	return 0;
}

/*
 * Process server debug command
 */
static int server_proccmd_debug(client_t *client)
{
	char *arg = client->argv[1];

	if (arg != NULL) {
		strtolower(arg);
	}

	if (arg == NULL) {
		sendres_missing_arg(client);
	} else if (strcmp(arg, "on") == 0) {
		info("> debug on");
		setloglevel(LOG_DEBUG);
	} else if (strcmp(arg, "off") == 0) {
		info("> debug off");
		setloglevel(LOG_INFO);
	} else {
		sendres_invalid_arg(client, arg);
	}

	return 0;
}

/*
 * Process server "dump" command
 */
static int server_proccmd_dump(client_t *client, server_t *server)
{
	char *arg = client->argv[1];

	if (arg != NULL) {
		strtolower(arg);
	}

	if (arg == NULL) {
		sendres_missing_arg(client);
	} else if (strcmp(arg, "on") == 0) {
		info("> dump on");
		server_setdump(server, 1);
	} else if (strcmp(arg, "off") == 0) {
		info("> dump off");
		server_setdump(server, 0);
	} else {
		sendres_invalid_arg(client, arg);
	}

	return 0;
}

/*
 * Process error at adding work into thread pool
 */
static void server_procerr_workadd(client_t *client)
{
	char *errstr, buf[RESSTR_MAX + 1];

	if (errno == ECANCELED) {
		sendres(client, RES_HEAD_ERR"server is being shutdown\n");
	} else if (errno == EAGAIN) {
		sendres(client, RES_HEAD_ERR"server is busy\n");
	} else {
		errstr = strerror_r(errno, buf, sizeof(buf));
		sendres(client, RES_HEAD_ERR"server internal error: %s\n", errstr);
	}
}

/*
 * Allocate memory for new client connection
 */
static client_t *client_alloc(void)
{
	client_t *client;

	client = malloc(sizeof(client_t));
	if (client == NULL) {
		error_num(errno, "%s: cannot allocate memory for client data",
			server_header);
		return NULL;
	}
	client->addr = NULL;
	client->sockfd = -1;

	return client;
}

/*
 * Close connection and free memory for client data
 */
static void client_free(client_t *client)
{
	int oldstate;

	/* Disable cancellation at end of function for debug() */
	pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, &oldstate);

	if (client->sockfd >= 0) {
		if (client->addr != NULL) {
			debug("%s: client disconncted (sockfd = %d, addr = %s, port = %d)",
				server_header, client->sockfd, client->addr, client->port);
		} else {
			debug("%s: client disconncted (sockfd = %d)",
				server_header, client->sockfd);
		}
		close(client->sockfd);
	}
	free(client->addr);
	free(client);

	pthread_setcancelstate(oldstate, NULL);
}

/*
 * Cleanup connection state of client
 */
static void cleanup_client(client_t *client)
{
	server_t *server = client->server;

	/* Decrement counter for number of connections */
	pthread_mutex_lock(&(server->lock));
	server->connnum--;
	pthread_mutex_unlock(&(server->lock));

	/* Close connection and free memory of client data */
	client_free(client);
}

/*
 * Process requests from a client
 */
static void *server_procreq(client_t *client)
{
	int sockfd, num_devs;
	char *cmdstr, **argv;
	const char *s, *cmd;
	server_t *server;
	alias_t *alias;
	tpool_t tpool;
	tpool_work_t *tp_work;
	struct device *dev, *devs;
	struct device_workreq req;

	cmdstr = client->cmdstr;
	argv = client->argv;
	sockfd = client->sockfd;
	server = client->server;
	alias = &(server->alias);
	tpool = server->tpool;
	num_devs = server->num_devs;
	devs = server->devs;

	/* Push cleanup routine for cancellation */
	pthread_cleanup_push((void *)cleanup_client, (void *)client);

	/* Loop for receiving a command and sending a response from/to client */
	while (recvcmd(client, client->cmdstr, sizeof(client->cmdstr)) > 0) {

		/* Split command string into array */
		client->argc = strsplit(cmdstr, argv, CMDARGC_MAX);
		cmd = strtolower(argv[0]);

		/* Parse and process server commands */
		if (strcmp(cmd, "debug") == 0) {			/* debug */
			server_proccmd_debug(client);
		} else if (strcmp(cmd, "dump") == 0) {		/* dump */
			server_proccmd_dump(client, server);
		} else if (strcmp(cmd, "help") == 0) {		/* help */
			server_proccmd_help(client, server);
		} else if (strcmp(cmd, "quit") == 0) {		/* quit */
			break;
		} else if (cmd[0] != '\0') {

			/* Check alias name of device name */
			if ((s = alias_lookup(alias, cmd)) != NULL) {
				cmd = s;
			}

			/* Parse and process device commands */
			if ((dev = device_getdev(devs, num_devs, cmd)) != NULL) {

				/* Add work into thread pool to process other commands */
				req.dev = dev;
				req.client = client;
				if (tpool_work_add(tpool, &tp_work, (void *)device_proccmd,
					&req, 0, 0) < 0) {
					server_procerr_workadd(client);
				} else {
					do {
						if (chkcancel(client) > 0) {
							tpool_work_cancel(tpool, tp_work);
							tpool_work_wait(tpool, tp_work, NULL);
							break;
						}
					} while (tpool_work_timedwait(tpool, tp_work, NULL,
						100000) < 0 && errno == ETIMEDOUT);
				}
			} else {
				sendres(client,
					RES_HEAD_ERR"unknown device or command -- %s\n", cmd);
			}
		}

		/* Clear buffer to ignore rest data from client before send prompt */
		if (clearbuf(sockfd) < 0) {
			break;
		}

		/* Send indicator for completion of command or prompt */
		sendres(client, SERVER_EOR);
	}

	/* Close connection and cleanup client data */
	pthread_cleanup_pop(1);		/* cleanup_client(client) */

	return NULL;
}

/*
 * Signal handler to catch shutdown signals
 */
static void server_sighandler(int signal)
{
	server_shutdown_flag = 1;
}

/*
 * Main routine of main thread
 */
static int server_loop(server_t *server)
{
	int sockfd, server_sockfd, flag = 1;
	sigset_t sigmask;
	struct sigaction sigact;
	struct sockaddr_in sin;
	socklen_t addrlen;
	client_t *client;
	tpool_t tpool;

	/* Setup signal handler to handle shutdown signals for main thread */
	sigact.sa_handler = server_sighandler;
	sigemptyset(&(sigact.sa_mask));
	sigact.sa_flags = 0;
	sigaction(SIGTERM, &sigact, NULL);
	sigaction(SIGINT, &sigact, NULL);

	/* Unmask signal to catch shutdown signals */
	sigemptyset(&sigmask);
	sigaddset(&sigmask, SIGTERM);
	sigaddset(&sigmask, SIGINT);
	pthread_sigmask(SIG_UNBLOCK, &sigmask, NULL);

	server_sockfd = server->sockfd;
	tpool = server->tpool;

	/* Accept loop */
	while (!server_shutdown_flag) {

		/* Allocate memory for new work request */
		if ((client = client_alloc()) == NULL) {
			break;
		}

		/* Wait for connection from client */
		addrlen = sizeof(struct sockaddr_in);
		sockfd = accept(server_sockfd, (struct sockaddr *)&sin, &addrlen);
		if (sockfd < 0) {
			/* Check if shutdown signal is catched */
			if (errno != EINTR || !server_shutdown_flag) {
				error_num(errno,
					"%s: cannot accept socket (server_scokfd = %d)",
					server_header, server_sockfd);
			} else {
				info("%s: received shutdown signal", server_header);
			}
			client_free(client);
			break;
		}

		/* Set TCP_NODELAY option */
		if (setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, (char *)&flag,
			sizeof(flag)) < 0) {
			error_num(errno, "%s: cannot set TCP_NODELAY option",
				server_header);
			client_free(client);
			continue;
		}

		/* Setup fields of client structure */
		client->sockfd = sockfd;
		client->addr = strdup(inet_ntoa(sin.sin_addr));
		if (client->addr == NULL) {
			error_num(errno, "%s: cannot allocate memory for client data",
				server_header);
			client_free(client);
			continue;
		}
		client->port = ntohs(sin.sin_port);
		client->server = server;

		debug("%s: client connected (sockfd = %d, addr = %s, port = %d)",
			server_header, sockfd, client->addr, client->port);

		/* Increment counter for number of connections */
		pthread_mutex_lock(&(server->lock));
		if (server->connnum >= server->connmax) {
			pthread_mutex_unlock(&(server->lock));
			sendres(client, RES_HEAD_ERR"too many clients\n");
			client_free(client);
			continue;
		}
		server->connnum++;
		pthread_mutex_unlock(&(server->lock));

		/* Add client work request to queue for worker threads */
		if (tpool_work_add(tpool, NULL, (void *)server_procreq, client, 1, 0) < 0) {
			server_procerr_workadd(client);
			cleanup_client(client);
		}
	}

	return 0;
}

/*
 * Print usage message and exit
 */
static void server_usage(struct server_option *servopt)
{
	fputs(servopt->title, stderr);
	fprintf(stderr, "Usage: %s [-vd] [-c configfile] [-l logfile]\n",
		program_invocation_short_name);
	fprintf(stderr, "  options:\n");
	fprintf(stderr, "    -v               verbose mode\n");
	fprintf(stderr, "    -d               print debug messages\n");
	fprintf(stderr,
		"    -c configfile    use this file as config file (default: %s)\n",
		servopt->conffile);
	fprintf(stderr,
		"    -l logfile       use this file as log file (default: %s)\n",
		servopt->logfile);
	fprintf(stderr, "    -h               show help message\n");
	fputs("\n", stderr);

	exit(1);
}

/*
 * Server main thread
 */
int server_main(struct server_option *servopt, int argc, char **argv)
{
    int opt;
    server_t server;
    
    /* Set defaults to flags and filenames */
    int debug_flag = 0;
    int verbose_flag = 0;
    const char *logfile = servopt->logfile;
    const char *conffile = servopt->conffile;
    
    /* Parse command-line options */
    while ((opt = getopt(argc, argv, "vdc:l:h")) != -1) {
	switch (opt) {
	    case 'v':
		verbose_flag = 1;
		break;
	    case 'd':
		debug_flag = 1;
		break;
	    case 'c':
		conffile = optarg;
		break;
	    case 'l':
		logfile = optarg;
		break;
	    case 'h':
		server_usage(servopt);
	    default:
		fprintf(stderr, "%s: unknown option -- %c", progname, opt);
		server_usage(servopt);
	}
    }
    argc -= optind;
    argv += optind;
    
    /* record config file name into global constant */
    server_conffile_name = conffile;
    pthread_mutex_init(&server_conffile_lock, NULL);

    /* Setup logging */
    setlogfile(logfile);
    setlogterm(verbose_flag);
    if (debug_flag) {
	setloglevel(LOG_DEBUG);
    }
    
    info("%s: start", server_header);
    info("%s: %s", server_header, servopt->title);
    
    /* Initialize fields of server data */
    if (server_init(&server) < 0) {
	goto exit5;
    }
    server.addr = strdup(servopt->addr);
    server.port = servopt->port;
    server.devs = servopt->devs;
    server.num_devs = servopt->num_devs;

    /* Initialize fields of device data */
    if (device_init(server.devs, server.num_devs) < 0) {
	goto exit4;
    }
    
    /* Read configuration from file */
    if (readconf(conffile, &server) < 0) {
	goto exit3;
    }
    server_postconf(&server);
    device_postconf(server.devs, server.num_devs);
    
    /*
     * If not verbose mode, then becomes daemon process, it should do before
     * create any threads. Redirects of stdout/stderr are not done this time.
     */
    if (!verbose_flag) {
	daemon(1, 1);
    }
    
    /* Connect to controllers and start server */
    if (device_open(server.devs, server.num_devs) < 0) {
	goto exit2;
    } else if (server_start(&server) < 0) {
	goto exit1;
    }
    
    /* Close stdin and redirect stdout and stderr to /dev/null */
    if (!verbose_flag) {
	fclose(stdin);
	freopen("/dev/null", "w", stdout);
	freopen("/dev/null", "w", stderr);
    }
    
    /* Enter to accept loop */
    server_loop(&server);
    
    /* Shutdown server */
 exit1:
    server_shutdown(&server);
    
 exit2:
    device_close(server.devs, server.num_devs);
    
 exit3:
    device_free(server.devs, server.num_devs);
    
 exit4:
    server_free(&server);
    
 exit5:
    info("%s: terminated", server_header);
    
    pthread_mutex_destroy(&server_conffile_lock);

    return 0;
}
