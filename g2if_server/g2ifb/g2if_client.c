/* -------------------------------------------------------------------------
 * g2if_server.c -- client program for g2if between RTS and
 *                       Gen2/AO188
 *
 * -------------------------------------------------------------------------
 * Description
 *    This is a client program for g2if server between AO188 RTS and 
 *    AO188 OBCP/Gen2.
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/11   Y. Ono        Initial version
 *
 * -------------------------------------------------------------------------
 */

#include "g2if_servif.h"

#define PROGNAME	"g2if_client"
#define PROGTITLE	"RTS-OBCP/Gen2 g2if client"

#define SERVER_ADDR	G2IF_SERVER_ADDR
#define SERVER_PORT	G2IF_SERVER_PORT

#include "../common/client.c"
