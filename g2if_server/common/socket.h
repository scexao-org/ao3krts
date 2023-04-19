/*
 * socket.h -- Definitions for functions for communicating with server
 *             through socket connection
 *
 * Written by Makoto WATANABE
 */

#ifndef _SOCKET_H
#define _SOCKET_H

#include <netinet/in.h>			/* for struct sockaddr_in */

#ifdef __cplusplus
extern "C" {
#endif

/* Function prototypes */

int getsock(struct sockaddr_in *sin, const char *addr, int port);
int connserv(const char *addr, int port);
int closeconn(int sockfd);
int clearbuf(int sockfd);
int waitdata(int sockfd, long timeout);
int recvdata(int sockfd, char *buf, int size, long timeout);
int recvstr(int sockfd, char *str, int size, const char *ending, long timeout);

#ifdef __cplusplus
}
#endif

#endif /* _SOCKET_H */
