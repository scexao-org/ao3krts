/*
 * client.c -- Client program for commuticating with server via socket for AO188
 *
 * Written by Makoto WATANABE
 */

#define _GNU_SOURCE			/* for program_invocation_short_name */

#include <unistd.h>			/* for close() */
#include <stdio.h>			/* for fprintf() */
#include <stdlib.h>			/* for exit() */
#include <stdarg.h>			/* for va_list, va_start(), va_end(), vsnprintf() */
#include <string.h>			/* for strncat(), strerror() */
#include <ctype.h>			/* for isdigit() */
#include <libgen.h>			/* for basename() */
#include <signal.h>			/* for signal() */
#include <errno.h>			/* for errno, program_invocation_short_name */
#include <netinet/tcp.h>        	/* for TCP_NODELAY */
#include "socket.h"			/* for connserv() */
#include "servif.h"			/* for SERVER_EOR, CMDSTR_MAX, RESSTR_MAX */
#include "tool.h"			/* for get_ip() */

/* Define defaults if undefined */

#ifndef PROGNAME
#define progname program_invocation_short_name
#else
static const char *progname = PROGNAME;
#endif

#ifndef SERVER_ADDR
#define SERVER_ADDR "localhost"
#endif

#ifndef SERVER_PORT
#define SERVER_PORT 18800
#endif

#ifndef CLIENT_TIMEOUT
#define CLIENT_TIMEOUT 3600
#endif

#ifndef HOSTNAME_OP
#define HOSTNAME_OP 0
#endif

static const char *server_addr = SERVER_ADDR;
static int server_port = SERVER_PORT;

/* socket descriptor to use in client_exit() */

static int sockfd = -1;

/* flag indicating completion of command */

static int eor = 1;

/* flag for shutdown of client */

static int client_shutdown = 0;

/*
 * Print usage
 */
static int client_usage(const char *cmd)
{

#ifdef PROGTITLE
	fputs(PROGTITLE, stderr);
	fputs("\n", stderr);
#endif

	if (cmd[0] != '\0') {
		fprintf(stderr, "Usage: %s [-h] [-s host] [-p port] "
			"[<command> [<arguments>]]\n", cmd);
	} else {
		fprintf(stderr, "Usage: %s [-h] [-s host] [-p port] "
			"<command> [<arguments>]\n", progname);
	}
	fprintf(stderr, "  options:\n");
	fprintf(stderr,
		"    -s host  use this as server (default: %s)\n", server_addr);
	fprintf(stderr,
		"    -p port  use this as port number (default: %d)\n", server_port);
	fprintf(stderr, "    -h       print this message\n");

	exit(1);
}

/*
 * Make command string for server, joining arguments with space separators
 */
static int make_cmdstr(char *cmdstr, size_t size, int argc, char **argv)
{
	size_t i, n;
	int quote;
	char c, *s1, *s2;

	/* Find end of initial command string */
	n = 0;
	for (s1 = cmdstr; *s1; s1++) {
		n++;
	}

	/* If buffer is full, return */
	if (size < n + 2) {
		return n;
	}
	size -= n + 2;

	/* Append arguments w/ blank separators */
	for (i = 0; i < argc; i++) {

		if (size == 0) {
			break;
		}

		/* Append space as a sepateter */
		if (cmdstr[0] != '\0' || i > 0) {
			*s1 = ' ';
			s1++;
			n++;
			size--;
			if (size == 0) {
				break;
			}
		}

		/* Check need of quote */
		if (strchr(argv[i], ' ') == NULL) {
			quote = 0;
		} else {
			quote = 1;
			*s1 = '\"';
			s1++;
			n++;
			size--;
			if (size == 0) {
				break;
			}
		}

		/* Append an argument */
		for (s2 = argv[i]; (c = *s2); s2++) {
			*s1 = c;
			s1++;
			n++;
			size--;
			if (size == 0) {
				break;
			}
		}

		/* Close quote */
		if (quote) {
			*s1 = '\"';
			s1++;
			n++;
			size--;
		}
	}

	/* Append EOC charactor as marker of end of command string */
	*s1 = CLIENT_EOC;
	s1++;
	n++;
	*s1 = '\0';

	return n;
}

static void sighandler(int status)
{
	client_shutdown = 1;

	return;
}

/*
 * Exit client program w/ closing connection
 */
static void client_exit(int status)
{
	char str[] = { CLIENT_CAN };

	/* Send control charactor to cancel command if command is running */
	if (eor == 0 && sockfd != -1) {
		send(sockfd, str, 1, 0);
	}

	/* Close socket */
	if (sockfd != -1) {
		close(sockfd);
	}

	exit(status);
}

/*
 * Print error message and exit client
 */
static void eprintf(const char *format, ...)
{
	char msg[1024];
	va_list ap;

	va_start(ap, format);
	vsnprintf(msg, sizeof(msg), format, ap);
	va_end(ap);

	fprintf(stderr, "%s: %s\n", progname, msg);
	client_exit(1);
}

/*
 * Print message on stdin or stderr if error message
 */
#define fputline(fp, line) { \
	if (strstr(line, RES_HEAD_ERR) == line) { \
		fp = stderr; \
		err = 1; \
	} else { \
		fp = stdout; \
	} \
	fputs(line, fp); \
}

/*
 * Main function for client
 */
int main(int argc, char **argv)
{
	int i, ret, optind, flag, n, l, delim_len, lf = 1, err = 0;
	char opt, options[256], *optarg;
	char cmdstr[CMDSTR_MAX + 1], resstr[RESSTR_MAX + 1];
	char *s, c, d, *delim, buf[RESSTR_MAX + 1], line[RESSTR_MAX + 1];
	FILE *fp = stdout;
	char ip[RESSTR_MAX + 1];

	/* Copy program name if it is command string for server */
	cmdstr[0] = '\0';
	strncat(cmdstr, basename(argv[0]), sizeof(cmdstr) - 1);
	if (strcmp(cmdstr, progname) == 0) {
		if (argc < 2) {
			eprintf("missing command");
		}
		cmdstr[0] = '\0';
	}

	/* HOSTNAME to IP ADDR if HOSTNAME_OP is 1 */
	if (HOSTNAME_OP == 1){
	  get_ip(server_addr, ip);
	  server_addr = ip;
	}

	/* Parse command line options */
	optind = 1;					/* Skip first argument */
	while (optind < argc) {

		/* Check if argv has option */
		if (*(argv[optind]) != '-') {
			break;
		}

		/* Ignore '-' with a nummber */
		if (isdigit(*(argv[optind] + 1))) {
			break;
		}

		/* Scan option charactor */
		options[0] = '\0';
		strncat(options, argv[optind], sizeof(options) - 1);
		n = strlen(options);
		for (i = 1; i < n; i++) {
			opt = options[i];
			switch (opt) {
			case 's':
				if (argc == optind + 1) {
					eprintf("option requires an argument -- %c", opt);
				}
				server_addr = argv[optind + 1];
				optind++;
				break;
			case 'p':
				if (argc == optind + 1) {
					eprintf("option requires an argument -- %c", opt);
				}
				optarg = argv[optind + 1];
				errno = 0;
				server_port = strtol(optarg, &s, 10);
				if (errno || *s != '\0') {
					eprintf("invalid option argument -- %s", optarg);
				}
				break;
			case 'h':
				client_usage(cmdstr);
				break;
			default:
				eprintf("unknown option -- %c", opt);
			}
		}
		optind++;
	}
	argc -= optind;
	argv += optind;

	/* Check if operation command is provided */
	if (argc < 1 && cmdstr[0] == '\0') {
		eprintf("operation command is required");
	}

	/* Set signal handlers */
	signal(SIGTERM, sighandler);
	signal(SIGINT, sighandler);

	/* Open socket to connect server */
	if ((sockfd = connserv(server_addr, server_port)) < 0) {
		eprintf("cannot connect to server on %s port %d: %s", server_addr,
			server_port, strerror(errno));
	}

	/* Set TCP_NODELAY option */
	flag = 1;
	if (setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, (char *)&flag,
		sizeof(flag)) < 0) {
		eprintf("cannot set TCP_NODELAY option");
	}

	/* Make and send command string to server */
	n = make_cmdstr(cmdstr, sizeof(cmdstr), argc, argv);
	if ((ret = send(sockfd, cmdstr, n, 0)) < 0) {
		eprintf("cannot send command to server on %s port %d: %s",
			server_addr, server_port, strerror(errno));
	}

	/* Set delimitor string of response string */
	delim = SERVER_EOR;
	delim_len = strlen(delim);
	d = delim[0];
	eor = 0;
	lf = 1;

	/* Loop until receive a delimitor string, printing response messages */
	l = 0;
	while (eor == 0 && client_shutdown == 0) {
		/* Receive response from server */
		ret = recvdata(sockfd, buf, sizeof(buf) - 1, CLIENT_TIMEOUT);
		if (ret == 0 || client_shutdown) {
			break;
		} else if (ret < 0) {
			if (errno == ETIMEDOUT) {
				eprintf("server response is timeout");
			}
			eprintf("cannot receive response from server: %s", strerror(errno));
		}
		buf[ret] = '\0';
		resstr[l] = '\0';
		strncat(resstr, buf, sizeof(resstr) - l - ret - 1);

		/* Print response line by line w/ finding delimitor */
		n = 0;
		l = 0;
		for (s = resstr; (c = *s); s++) {
			if (c == d) {
				if (strstr(s, delim) == s) {
					eor = 1;
					break;
				} else if ((i = strlen(s)) < delim_len) {
					l = i;
					break;
				}
			}
			line[n] = c;
			n++;
			if (c == '\n') {
				line[n] = '\0';
				fputline(fp, line);
				lf = 1;
				n = 0;
			}
		}
		if (n > 0) {
			line[n] = '\0';
			fputline(fp, line);
			lf = 0;
		}

		/*
		 * If rest string exists, move them into beginning of buffer to
		 * concatenate them with next inputs
		 */
		if (l > 0) {
			memmove(resstr, s, l);
		}
	}

	/* Put line feed if last line has no line feed */
	if (lf == 0) {
		fputs("\n", fp);
	}

	/* Exit client */
	client_exit(client_shutdown || err);

	return 0;
}
