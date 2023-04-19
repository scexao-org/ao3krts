/* -------------------------------------------------------------------------
 * fifo_func.h -- Definitions of function for fifo commnication
 *
 * -------------------------------------------------------------------------
 * Update History:
 *    <Date>       <Who>         <What>    
 *    2019/09/26   Y. Ono        Initial version
 * -------------------------------------------------------------------------
 */

#ifndef _FIFO_FUNC_H
#define _FIFO_FUNC_H

#define FIFO_DEF_TIMERSEC     2
#define FIFO_CMD_LENGTH       1024

#define FIFO_FPSCTRL_NAME     "/milk/shm/ao188_new_fpsCTRL.fifo" // ao188 = hardware, ao188lhs_ = cacao simulator
#define FIFO_MKFIFO_COMMAND   "/home/vdeo/src/rts/g2if_server/g2if/scripts/mymkfifo"
#define FIFO_GET_COMMAND      "fwrval"
#define FIFO_SET_COMMAND      "setval"

struct fifo_t{
  char *name;
  int fd;
  int timersec;
  pthread_mutex_t lock;
};

int fifo_init(struct fifo_t *fifo);
int fifo_set_name(struct fifo_t *fifo, const char *name);
int fifo_set_timersec(struct fifo_t *fifo, int timersec);
int fifo_create(struct fifo_t *fifo);
int fifo_open(struct fifo_t *fifo);
int fifo_close(struct fifo_t *fifo);
int fifo_free(struct fifo_t *fifo);
int fifo_read(struct fifo_t *fifo, char *buff);

#endif /* _FIFO_FUNC_H */
