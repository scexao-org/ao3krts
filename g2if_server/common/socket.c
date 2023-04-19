/*
 * socket.c -- Functions for communicating through socket connection
 *
 * Written by Makoto WATANABE
 */

#include <unistd.h>				/* for close() */
#include <string.h>				/* for memcpy(), strlen() */
#include <sys/select.h>			/* for select() */
#include <sys/types.h>			/* for socket() */
#include <sys/socket.h>			/* for socket() */
#include <netdb.h>				/* for gethostbyname_r() */
#include <netinet/in.h>			/* for htons() */
#include <errno.h>
#include "socket.h"
#include "log.h"

/*
 * Get a socket and setup socket address data
 */
int getsock(struct sockaddr_in *sin, const char *addr, int port)
{
	int sockfd, h_errnop;
	struct hostent hp, *result;
	char buf[256];

	/* Get a socket descriptor */
	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
		return -1;
	}

	/* Get host entry on network */
	if (gethostbyname_r(addr, &hp, buf, sizeof(buf), &result, &h_errnop)) {
		return -1;
	}

	/* Set address and port into sockaddr */
	sin->sin_family = AF_INET;
	sin->sin_port = htons(port);
	memcpy(&(sin->sin_addr), hp.h_addr, hp.h_length);

	return sockfd;
}

/*
 * Open socket connection to server
 */
int connserv(const char *addr, int port)
{
	int sockfd, saved_errno;
	struct sockaddr_in sin;

	/* Get socket and setup sockaddr for server */
	if ((sockfd = getsock(&sin, addr, port)) < 0) {
		return sockfd;
	}

	/* Open socket connection */
	if (connect(sockfd, (struct sockaddr *)&sin, sizeof(sin)) < 0) {
		saved_errno = errno;
		close(sockfd);
		errno = saved_errno;
		return -1;
	}

	return sockfd;
}

/*
 * Close socket connection
 */
int closeconn(int sockfd)
{
	shutdown(sockfd, SHUT_RDWR);
	close(sockfd);
	return 0;
}

/*
 * Clear receive buffer
 * (if connection is closed, return -1 and errno = ECONNRESET)
 */
int clearbuf(int sockfd)
{
	int ret;
	char buf[1024];

	/* Read buffer until it is empty */
	while ((ret = recv(sockfd, buf, sizeof(buf), MSG_DONTWAIT)) > 0) {
		;
	}

	if (ret == 0) {
		errno = ECONNRESET;
		return -1;
	} else if (errno != EAGAIN) {
		return -1;
	}

	return 0;
}

/*
 * Wait until data is ready to receive
 *
 * Return value: 1 (data is ready), 0 (timeout), -1 (error, errno is set)
 */
int waitdata(int sockfd, long timeout)
{
	int nfds;
	fd_set readfds;
	struct timeval tv;

	/* Set descriptor into list */
	FD_ZERO(&readfds);
	FD_SET(sockfd, &readfds);

	if (timeout < 0) {
		/* Timeout is disable */
		nfds = select(FD_SETSIZE, &readfds, NULL, NULL, NULL);
	} else {
		/* Set timeout (in seconds) */
		tv.tv_sec = timeout;
		tv.tv_usec = 0;
		nfds = select(FD_SETSIZE, &readfds, NULL, NULL, &tv);
	}

	/* Check if error (nfds = -1) */
	if (nfds < 0) {
		return nfds;
	}

	/* Return status of descritptor */
	return FD_ISSET(sockfd, &readfds);
}

/*
 * Receive data from socket (return value is size of data received)
 *
 * Return value: number of bytes received (if 0, connection is closed),
 *				 or -1 if error (errno is set, if timeout errno = ETIMEDOUT)
 */
int recvdata(int sockfd, char *buf, int size, long timeout)
{

	int ret;

	/* Wait for data */
	ret = waitdata(sockfd, timeout);

	if (ret < 0) {
		return ret;
	} else if (ret == 0) {
		errno = ETIMEDOUT;
		return -1;
	}

	/* Receive data via socket */
	return recv(sockfd, buf, size, 0);
}

/*
 * Receive a string until receive an ending string from socket.
 * The ending string (and below) will be removed, therefore, when only the
 * ending string is received null string is returned.
 *
 * Return value: 1 when data is received, 0 when connection is closed,
 *				 or -1 if error (errno is set, if timeout errno = ETIMEDOUT)
 */
int recvstr(int sockfd, char *str, int size, const char *ending, long timeout)
{

	int ret;
	char *s, buf[size];

	str[0] = '\0';

	/* Receive data until get an ending string */
	do {
		if ((ret = recvdata(sockfd, buf, sizeof(buf) - 1, timeout)) <= 0) {
			return ret;
		}
		buf[ret] = '\0';		/* set terminal charactor */
		strncat(str, buf, size - strlen(str) - 1);
	} while ((s = strstr(str, ending)) == NULL);

	/* Remove an ending string */
	*s = '\0';

	return 1;
}
