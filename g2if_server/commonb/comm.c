/*
 * comm.c -- Functions to communicate with a serial port device on terminal
 *           server via socket
 *
 * 2008/11/18 Makoto WATANABE -- Initial version
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE			/* for for using GNU version of strerror_r() */
#endif /* _GNU_SOURCE */
#include <stdio.h>
#include <unistd.h>				/* for close() */
#include <stdlib.h>				/* for free() */
#include <string.h>				/* for strdup(), strlen() */
#include <pthread.h>			/* for pthread_*() */
#include <sys/types.h>			/* for send(), setsockopt() */
#include <sys/socket.h>			/* for send(), setsockopt() */
#include <netinet/tcp.h>		/* for TCP_NODELAY */
#include <errno.h>				/* for errno */
#include "log.h"				/* for error(), info(), debug() */
#include "server.h"				/* for sendres(), sendres_*() */
#include "socket.h"				/* for connserv(), clrbuf(), recvstr() */
#include "stringx.h"			/* for strspecial() */
#include "comm.h"				/* for comm_t */

/*
 * Initialize data for handling communication
 */
int comm_init(comm_t *comm, const char *header)
{
/*	debug("comm: init"); */

	comm->addr = NULL;
	comm->port = 2101;
	comm->timeout = -1;
	comm->connect = 0;
	comm->access = 0;
	comm->dump = 0;
	pthread_cond_init(&(comm->end_of_access), NULL);
	pthread_mutex_init(&(comm->lock), NULL);

	comm->delim_in = strdup(COMM_DELIM_DEFAULT);
	comm->delim_out = strdup(COMM_DELIM_DEFAULT);
	if (header != NULL) {
		comm->header = strdup(header);
	} else {
		comm->header = strdup("comm");
	}
	if (comm->delim_in == NULL || comm->delim_out == NULL
		|| comm->header == NULL) {
		error_num(errno, "%s: cannot initialize comm data", header);
		free(comm->delim_in);
		free(comm->delim_out);
		free(comm->header);
		comm->delim_in = NULL;
		comm->delim_out = NULL;
		comm->header = NULL;
		return -1;
	}
	comm->delim_outlen = strlen(comm->delim_out);

	return 0;
}

/*
 * Free resources in data for handling communication
 */
int comm_free(comm_t *comm)
{
/*	debug("comm: free"); */

	free(comm->addr);
	free(comm->delim_in);
	free(comm->delim_out);
	free(comm->header);
	comm->addr = NULL;
	comm->delim_in = NULL;
	comm->delim_out = NULL;
	comm->header = NULL;
	pthread_cond_destroy(&(comm->end_of_access));
	pthread_mutex_destroy(&(comm->lock));

	return 0;
}

/*
 * Set IP address for connection to device
 */
int comm_setaddr(comm_t *comm, const char *addr)
{
	char *s = NULL;

	pthread_mutex_lock(&(comm->lock));

	/* Check connection and memory allocation */
	if (comm->connect
		|| (addr != NULL && (s = strdup(addr)) == NULL)) {
		pthread_mutex_unlock(&(comm->lock));
		if (comm->connect) {
			errno = EISCONN;
		}
		error_num(errno, "%s: cannot change address", comm->header);
		return -1;
	}
	free(comm->addr);
	comm->addr = s;

	pthread_mutex_unlock(&(comm->lock));

	return 0;
}

/*
 * Set TCP port number for connection to device
 */
int comm_setport(comm_t *comm, int port)
{
	pthread_mutex_lock(&(comm->lock));

	/* Check connection */
	if (comm->connect) {
		pthread_mutex_unlock(&(comm->lock));
		errno = EISCONN;
		error_num(errno, "%s: cannot change port", comm->header);
		return -1;
	}
	comm->port = port;

	pthread_mutex_unlock(&(comm->lock));

	return 0;
}

/*
 * Set timeout period for communication with device
 */
int comm_settimeout(comm_t *comm, int timeout)
{
	pthread_mutex_lock(&(comm->lock));
	comm->timeout = timeout;
	pthread_mutex_unlock(&(comm->lock));

	return 0;
}

/*
 * Set delimiter string for sending and receiving
 */
int comm_setdelim(comm_t *comm, const char *delim_in, const char *delim_out)
{
	char *s1, *s2;

	pthread_mutex_lock(&(comm->lock));

	/* Check connection and memory allocation */
	s1 = NULL;
	if (comm->connect || delim_in == NULL || delim_out == NULL
		|| (s1 = strdup(delim_in)) == NULL
		|| (s2 = strdup(delim_out)) == NULL) {
		pthread_mutex_unlock(&(comm->lock));
		if (comm->connect) {
			errno = EISCONN;
		} else if (delim_in == NULL || delim_out == NULL) {
			errno = EINVAL;
		} else {
			free(s1);
		}
		error_num(errno, "%s: cannot change delimiter", comm->header);
		return -1;
	}

	/* Save data */
	free(comm->delim_in);
	free(comm->delim_out);
	comm->delim_in = s1;
	comm->delim_out = s2;
	comm->delim_outlen = strlen(s2);

	pthread_mutex_unlock(&(comm->lock));

	return 0;
}

/*
 * Turn on/off dump of input/output strings
 */
int comm_setdump(comm_t *comm, int dump)
{
	pthread_mutex_lock(&(comm->lock));
	comm->dump = dump;
	pthread_mutex_unlock(&(comm->lock));

	return 0;
}

/*
 * Get dump flag value
 */
int comm_getdump(comm_t *comm)
{
	int dump;

	pthread_mutex_lock(&(comm->lock));
	dump = comm->dump;
	pthread_mutex_unlock(&(comm->lock));

	return dump;
}

/*
 * Wait until end of communication with device by other threads,
 * and then disable communication by other threads
 */
void comm_lock(comm_t *comm)
{
	pthread_t my_tid = pthread_self();

	pthread_mutex_lock(&(comm->lock));
	pthread_cleanup_push((void *)pthread_mutex_unlock, &(comm->lock));

	/* Wait until device becomes free */
	while (comm->access && pthread_equal(my_tid, comm->tid) == 0) {
		pthread_cond_wait(&(comm->end_of_access), &(comm->lock));
	}
	comm->access++;
	comm->tid = my_tid;

	pthread_cleanup_pop(1);	/* pthread_mutex_unlock(&(comm->lock)); */
}

/*
 * Unlock communicaton with device from other threads
 */
void comm_unlock(comm_t *comm)
{
	pthread_mutex_lock(&(comm->lock));
	comm->access--;
	pthread_cond_signal(&(comm->end_of_access));
	pthread_mutex_unlock(&(comm->lock));
}

/*
 * Open connection to device
 */
int comm_connect(comm_t *comm)
{
	int ret = 0, flag;

	/* Lock communication with device from other threads */
	comm_lock(comm);
	pthread_cleanup_push((void *)comm_unlock, comm);

	if (comm->connect == 0) {

		info("%s: connecting to device on %s port %d", comm->header,
			comm->addr, comm->port);

		/* Connect to controller */
		if (comm->addr == NULL || comm->addr[0] == '\0'
			|| (ret = connserv(comm->addr, comm->port)) < 0) {
			if (ret == 0) {
				errno = EFAULT;
				ret = -1;
			}
			error_num(errno, "%s: cannot connect to device on %s port %d",
				comm->header, comm->addr, comm->port);
		} else {
			pthread_mutex_lock(&(comm->lock));
			comm->sockfd = ret;
			comm->connect = 1;
			pthread_mutex_unlock(&(comm->lock));
			debug("%s: connected (sockfd = %d, addr = %s, port = %d)",
				comm->header, comm->sockfd, comm->addr, comm->port);

			/* Set TCP_NODELAY option */
			flag = 1;
			if ((ret = setsockopt(comm->sockfd, IPPROTO_TCP, TCP_NODELAY,
				(char *)&flag, sizeof(flag))) < 0) {
				error_num(errno, "%s: cannot set TCP_NODELAY option",
					comm->header);
			}
		}
	}

	/* Unlock communication with device from other threads */
	pthread_cleanup_pop(1);		/* comm_unlock(comm); */

	return ret;
}

/*
 * Close connection to controller
 */
int comm_disconnect(comm_t *comm)
{
	int sockfd;

	/* Lock communication with device from other threads */
	comm_lock(comm);
	pthread_cleanup_push((void *)comm_unlock, comm);

	if (comm->connect) {

		info("%s: disconnecting from device on %s port %d", comm->header,
			comm->addr, comm->port);

		/* Close connection */
		sockfd = comm->sockfd;
		close(sockfd);
		pthread_mutex_lock(&(comm->lock));
		comm->sockfd = -1;
		comm->connect = 0;
		pthread_mutex_unlock(&(comm->lock));

		debug("%s: disconnected (sockfd = %d, addr = %s, port = %d)",
			comm->header, sockfd, comm->addr, comm->port);
	}

	/* Unlock communication with device from other threads */
	pthread_cleanup_pop(1);		/* comm_unlock(comm); */

	return 0;
}

/*
 * Open connection to device (no log)
 */
int comm_connect_nolog(comm_t *comm)
{
	int ret = 0, flag;

	/* Lock communication with device from other threads */
	comm_lock(comm);
	pthread_cleanup_push((void *)comm_unlock, comm);

	if (comm->connect == 0) {

		/* Connect to controller */
		if (comm->addr == NULL || comm->addr[0] == '\0'
			|| (ret = connserv(comm->addr, comm->port)) < 0) {
			if (ret == 0) {
				errno = EFAULT;
				ret = -1;
			}
			error_num(errno, "%s: cannot connect to device on %s port %d",
				comm->header, comm->addr, comm->port);
		} else {
			pthread_mutex_lock(&(comm->lock));
			comm->sockfd = ret;
			comm->connect = 1;
			pthread_mutex_unlock(&(comm->lock));
			debug("%s: connected (sockfd = %d, addr = %s, port = %d)",
				comm->header, comm->sockfd, comm->addr, comm->port);

			/* Set TCP_NODELAY option */
			flag = 1;
			if ((ret = setsockopt(comm->sockfd, IPPROTO_TCP, TCP_NODELAY,
				(char *)&flag, sizeof(flag))) < 0) {
				error_num(errno, "%s: cannot set TCP_NODELAY option",
					comm->header);
			}
		}
	}

	/* Unlock communication with device from other threads */
	pthread_cleanup_pop(1);		/* comm_unlock(comm); */

	return ret;
}

/*
 * Close connection to controller (no log)
 */
int comm_disconnect_nolog(comm_t *comm)
{
	int sockfd;

	/* Lock communication with device from other threads */
	comm_lock(comm);
	pthread_cleanup_push((void *)comm_unlock, comm);

	if (comm->connect) {

		/* Close connection */
		sockfd = comm->sockfd;
		close(sockfd);
		pthread_mutex_lock(&(comm->lock));
		comm->sockfd = -1;
		comm->connect = 0;
		pthread_mutex_unlock(&(comm->lock));

		debug("%s: disconnected (sockfd = %d, addr = %s, port = %d)",
			comm->header, sockfd, comm->addr, comm->port);
	}

	/* Unlock communication with device from other threads */
	pthread_cleanup_pop(1);		/* comm_unlock(comm); */

	return 0;
}


/*
 * Return status of connection
 */
int comm_isconn(comm_t *comm)
{
	int connect;

	pthread_mutex_lock(&(comm->lock));
	connect = comm->connect;
	pthread_mutex_unlock(&(comm->lock));
	return connect;
}

/*
 * Check connection to device (if no connection return -1, otherwise 0)
 */
int comm_chkconn(comm_t *comm)
{
	if (comm->connect == 0) {
		errno = ENOTCONN;
		error_num(errno, comm->header);
		return -1;
	}
	return 0;
}

/*
 * Clear receive buffer of socket
 */
int comm_clearbuf(comm_t *comm)
{
	int ret;
	if ((ret = clearbuf(comm->sockfd)) < 0) {
		error_num(errno, "%s: cannot clear buffer", comm->header);
		return ret;
	}

	return 0;
}

/*
 * Send string to device
 */
int comm_sendstr(comm_t *comm, const char *str)
{
	int ret;
	size_t len = strlen(str);
	size_t n = len + comm->delim_outlen;
	char buf[len * 4 + 1];
	/* Print sending string as debugging message */
	if (comm_getdump(comm)) {
		info("%s: << %s", comm->header, strspecial(buf, sizeof(buf), str));
	}

	/* Concatenate string and delimiter into one, and send it to device */
	memcpy(buf, str, len);
	memcpy(buf + len, comm->delim_out, comm->delim_outlen);
	if ((ret = send(comm->sockfd, buf, n, 0)) < 0) {
		error_num(errno, "%s: cannot send data", comm->header);
		return ret;
	}

	return 0;
}

/*
 * Receive string from device
 */
int comm_recvstr(comm_t *comm, char *str, size_t size)
{
	int ret;
	size_t n;
	char c, line[size], buf[256];
	const char *s, *header;
	/* Receive string ending by delimiter string */
	ret = recvstr(comm->sockfd, str, size, comm->delim_in, comm->timeout);
	if (ret <= 0) {
		if (ret == 0) {
			errno = ECONNRESET;
		}
		error_num(errno, "%s: cannot receive data", comm->header);
		return -1;
	}

	/* If debug output is disable, skip below */
	if (comm_getdump(comm) == 0) {
		return 0;
	}
	/* Print received string line by line as debugging message */
	header = comm->header;
	n = 0;
	for (s = str; (c = *s); s++) {
		if (c == '\n') {
			line[n] = '\0';
			info("%s: >> %s", header, strspecial(buf, sizeof(buf), line));
			n = 0;
		} else {
			line[n] = c;
			n++;
		}
	}
	if (n > 0) {
		line[n] = '\0';
		info("%s: >> %s", header, strspecial(buf, sizeof(buf), line));
	}

	return 0;
}

/*
 * Receive data from device
 */
int comm_recvdata(comm_t *comm, char *str, size_t size)
{

    int ret;
    size_t n;
    char c, line[size], buf[256];
    const char *s, *header;
    /* Receive string ending by delimiter string */
    ret = recvdata(comm->sockfd, str, size, comm->timeout);
    if (ret <= 0) {
	if (ret == 0) {
	    errno = ECONNRESET;
	}
	error_num(errno, "%s: cannot receive data", comm->header);
	return -1;
    }

    /* If debug output is disable, skip below */
    if (comm_getdump(comm) == 0) {
	return ret;
    }
    /* Print received string line by line as debugging message */
    header = comm->header;
    n = 0;
    for (s = str; (c = *s); s++) {
	if (c == '\n') {
	    line[n] = '\0';
	    info("%s: >> %s", header, strspecial(buf, sizeof(buf), line));
	    n = 0;
	} else {
	    line[n] = c;
	    n++;
	}
    }
    if (n > 0) {
	line[n] = '\0';
	info("%s: >> %s", header, strspecial(buf, sizeof(buf), line));
    }
    
    return ret;
}

/*
 * Clear buffer, send and receive string to/from device
 */
int comm_sendrecv(comm_t *comm, const char *cmdstr, char *retstr, size_t size)
{
	int ret;

	/* Clear buffer, send, and receive */
	if ((ret = comm_clearbuf(comm)) < 0
		|| (ret = comm_sendstr(comm, cmdstr)) < 0
		|| (ret = comm_recvstr(comm, retstr, size)) < 0) {
		return ret;
	}
	       
	return 0;
}

/*
 * Send string to device w/ locking communication
 */
int comm_sendstr_lock(comm_t *comm, const char *cmdstr)
{
	int ret;

	/* Lock communication with device from other threads */
	comm_lock(comm);
	pthread_cleanup_push((void *)comm_unlock, comm);

	if ((ret = comm_chkconn(comm)) >= 0) {
		ret = comm_sendstr(comm, cmdstr);
	}

	/* Unlock communication with device from other threads */
	pthread_cleanup_pop(1);		/* comm_unlock(comm); */

	return ret;
}

/*
 * Clear buffer, send and receive string to/from device w/ locking
 * communication
 */
int comm_sendrecv_lock(comm_t *comm, const char *cmdstr, char *retstr,
	size_t size)
{
	int ret;

	/* Lock communication with device from other threads */
	comm_lock(comm);
	pthread_cleanup_push((void *)comm_unlock, comm);
	if ((ret = comm_chkconn(comm)) >= 0) {
	    ret = comm_sendrecv(comm, cmdstr, retstr, size);
	    //ret = comm_sendstr(comm, "\r\r");
	}

	/* Unlock communication with device from other threads */
	pthread_cleanup_pop(1);		/* comm_unlock(comm); */
	return ret;
}

/*
 * Process "dump" command (dump on/off)
 */
int comm_cmd_dump(client_t *client, comm_t *comm)
{
	int ret, dump;
	char *errstr, buf[RESSTR_MAX + 1];
	char *grp = comm->header;
	char *arg = getargv(client, 2);

	/* Check argument */
	if (arg == NULL) {
		sendres_missing_arg(client);
		return -1;
	} else if (strcasecmp(arg, "on") == 0) {
		dump = 1;
	} else if (strcasecmp(arg, "off") == 0) {
		dump = 0;
	} else {
		sendres_invalid_arg(client, arg);
		return -1;
	}

	info("%s: dump %s", grp, onoff(dump));

	/* Set dump on/off */
	ret = comm_setdump(comm, dump);
	if (ret < 0) {
		errstr = strerror_r(errno, buf, sizeof(buf));
		sendres(client, RES_HEAD_ERR"%s: %s\n", grp, errstr);
		return -1;
	}

	return 0;
}
