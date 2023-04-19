/* -------------------------------------------------------------------------
 * g2if_server.c -- server program for g2if between RTS and Gen2/AO188
 *
 * -------------------------------------------------------------------------
 * Description
 *    This is a server program for g2if server between AO188 RTS and 
 *    AO188 OBCP/Gen2. In order to send commands to severs in AO188 local
 *    network (10.0.0.3), this server program nees to access the relay
 *    server in AO188 OBCP.
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/04/11   Y. Ono        Initial version
 *    2019/06/20   Y. Ono        Add apdsafe
 *    2019/09/24   Y. Ono        Add cmtx
 * -------------------------------------------------------------------------
 */

#include "server.h"	        /* for struct server_option, server_main() */
#include "device.h"	        /* for struct device */
#include "howfs.h"        	/* for howfs_t */
#include "lowfs.h"        	/* for lowfs_t */
#include "entshut.h"        	/* for entshut_t */
#include "shms.h"        	/* for shms_t */
#include "adf.h"        	/* for adf_t */
#include "loop.h"        	/* for loop_t */
#include "gain.h"        	/* for gain_t */
#include "status.h"        	/* for status_t */
#include "dm.h"        	        /* for dm_t */
#include "tt.h"        	        /* for tt_t */
#include "wtt.h"        	/* for wtt_t */
#include "apdsafe.h"        	/* for apdsafe_t */
#include "cmtx.h"        	/* for cmtx_t */
#include "g2if_server.h"
#include "g2if_servif.h"

/* Title message */

static const char *title =
  "RTS-Gen2/AO188 g2if server ver."
  G2IF_SERVER_VERSION" (" __DATE__ ")";

/*
 * Server main function
 */
int main(int argc, char **argv){
  shms_t shms;
  howfs_t howfs;
  lowfs_t lowfs;
  loop_t loop;
  wtt_t wtt;
  gain_t gain = {.shms = &shms, .loop = &loop};
  cmtx_t cmtx = {.gain = &gain};
  adf_t adf = {.shms = &shms, .gain = &gain};
  dm_t dm = {.shms = &shms};
  tt_t tt = {.shms = &shms};
  apdsafe_t apdsafe = {.shms = &shms, .howfs = &howfs, .lowfs = &lowfs};
  status_t status = {.shms = &shms, .gain = &gain, .howfs = &howfs, .lowfs = &lowfs, .loop = &loop, .apdsafe = &apdsafe};

  /* List of devices */
  struct device devs[] = {
    {
      .name = "howfs",
      .desc = "HOWFS shutter control",
      .data = &howfs,
      .ops = &howfs_ops,
    },
    {
      .name = "lowfs",
      .desc = "LOWFS shutter control",
      .data = &lowfs,
      .ops = &lowfs_ops,
    },
    {
      .name = "shms",
      .desc = "Shared Memory",
      .data = &shms,
      .ops = &shms_ops,
    },
    {
      .name = "adf",
      .desc = "ADF control",
      .data = &adf,
      .ops = &adf_ops,
    },
    {
      .name = "loop",
      .desc = "Loop control",
      .data = &loop,
      .ops = &loop_ops,
    },
    {
      .name = "gain",
      .desc = "gain control",
      .data = &gain,
      .ops = &gain_ops,
    },
    {
      .name = "status",
      .desc = "show all status",
      .data = &status,
      .ops = &status_ops,
    },
    {
      .name = "dm",
      .desc = "DM control",
      .data = &dm,
      .ops = &dm_ops,
    },
    {
      .name = "tt",
      .desc = "TT control",
      .data = &tt,
      .ops = &tt_ops,
    },
    {
      .name = "wtt",
      .desc = "WTT control",
      .data = &wtt,
      .ops = &wtt_ops,
    },
    {
      .name = "apdsafe",
      .desc = "APDSAFE control",
      .data = &apdsafe,
      .ops = &apdsafe_ops,
    },
    {
      .name = "cmtx",
      .desc = "Command Matrix control",
      .data = &cmtx,
      .ops = &cmtx_ops,
    },
  };
    
  /* Options of server configuration */
  struct server_option servopt = {
    .title = title,
    .logfile = G2IF_SERVER_LOGFILE,
    .conffile = G2IF_SERVER_CONFFILE,
    .addr = G2IF_SERVER_ADDR,
    .port = G2IF_SERVER_PORT,
    .num_devs = sizeof(devs) / sizeof(struct device),
    .devs = devs,
  };
    
  server_main(&servopt, argc, argv);

  return 0;
}
