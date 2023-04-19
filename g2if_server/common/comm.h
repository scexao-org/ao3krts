/*
 * comm.h -- Definitions for functions to communicate with a serial port
 *           device on terminal server via socket
 *
 * 2008/11/18 Makoto WATANABE -- Initial version
 */

#ifndef _COMM_H
#define _COMM_H

#include <pthread.h>			/* for pthread_* */
#include "server.h"				/* for client_t */

/* Prompt string of controller */

#define COMM_DELIM_DEFAULT	"\r"

/* Structure data for handling communication with device */

typedef struct comm {
	char *addr;				/* IP Address or hostname */
	int port;				/* TCP port number */
	int sockfd;				/* socket descriptor */
	int timeout;			/* period (in seconds) to timeout communication */
	int connect;			/* status of connection (1: connected) */
	int access;				/* count of access lock */
	pthread_t tid;			/* id of thread locking access */
	char *delim_in;			/* delimitor string for input */
	char *delim_out;		/* delimitor string for output */
	size_t delim_outlen;	/* length of delimitor string for output */
	char *header;			/* header string for logging message */
	int dump;				/* flag indicating dump input/output strings */
	pthread_cond_t end_of_access;	/* cv to signal end of access */
	pthread_mutex_t lock;			/* lock of data */
} comm_t;

#ifdef __cplusplus
extern "C" {
#endif

/* Function prototypes */

int comm_init(comm_t *comm, const char *header);
int comm_free(comm_t *comm);

int comm_setaddr(comm_t *comm, const char *addr);
int comm_setport(comm_t *comm, int port);
int comm_settimeout(comm_t *comm, int timeout);
int comm_setdelim(comm_t *comm, const char *delim_in, const char *delim_out);
int comm_setdump(comm_t *comm, int dump);

void comm_lock(comm_t *comm);
void comm_unlock(comm_t *comm);

int comm_connect(comm_t *comm);
int comm_disconnect(comm_t *comm);
int comm_connect_nolog(comm_t *comm);
int comm_disconnect_nolog(comm_t *comm);
int comm_isconn(comm_t *comm);
int comm_chkconn(comm_t *comm);
int comm_clearbuf(comm_t *comm);
int comm_sendstr(comm_t *comm, const char *str);
int comm_recvstr(comm_t *comm, char *str, size_t size);
int comm_recvdata(comm_t *comm, char *str, size_t size);
int comm_sendrecv(comm_t *comm, const char *cmdstr, char *retstr, size_t size);
int comm_sendstr_lock(comm_t *comm, const char *cmdstr);
int comm_sendrecv_lock(comm_t *comm, const char *cmdstr, char *retstr,
	size_t size);

int comm_cmd_dump(client_t *client, comm_t *comm);

#ifdef __cplusplus
}
#endif

#endif /* _COMM_H */
