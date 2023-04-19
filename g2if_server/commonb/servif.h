/*
 * servif.h -- Definitions for interface between server and client program
 *
 * 2008/12/09 Makoto WATANABE -- Initial version
 */

#ifndef _SERVIF_H
#define _SERVIF_H

/* Limits of messages between server and client */

enum {
	CMDARGC_MAX = 32,		/* maximum number of command arguments */
	CMDSTR_MAX = 256,		/* maximum length of command string */
	RESSTR_MAX = 4096,		/* maximum length of response string */
};

/* Header and prompt strings from server */

#define RES_HEAD_ERR	"Error: "	/* header of error message */
#define SERVER_EOR		"\r"		/* for end of response from server */
#define CLIENT_EOC		'\r'		/* for end of command from client */
#define CLIENT_CAN		'\x18'		/* control charactor for command cancel */

#endif /* _SERVIF_H */
