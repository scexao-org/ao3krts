#include <stdio.h>			/* for snprintf() */
#include <stdlib.h>                     /* for system() */
#include <errno.h>			/* for errno */
#include <unistd.h>                     /* for read() */
#include <sys/fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <time.h>
#include <pthread.h>   	         	/* for pthread_* */
#include <string.h>                     /* for strdup */
#include "fifo_func.h"
#include "tool.h"

/*
 * init mutex lock for fifo
 */
int fifo_init(struct fifo_t *fifo){
  pthread_mutex_init(&(fifo->lock), NULL);
  fifo->timermsec = FIFO_DEF_TIMERMSEC;
  fifo->name = 0;

  return 0;
}

/*
 * set fifo name
 */
int fifo_set_name(struct fifo_t *fifo, const char *name){
  pthread_mutex_lock(&(fifo->lock));
  fifo->name = strdup(name);
  pthread_mutex_unlock(&(fifo->lock));

  return 0;
}

/*
 * get fifo timer
 */
int fifo_set_timermsec(struct fifo_t *fifo, int timermsec){
  pthread_mutex_lock(&(fifo->lock));
  fifo->timermsec = timermsec;
  pthread_mutex_unlock(&(fifo->lock));

  return 0;
}

/*
 * create fifo
 */
int fifo_create(struct fifo_t *fifo){
  char cmd[FIFO_CMD_LENGTH];

  if(fifo->name == 0) return -1;
  sprintf(cmd,FIFO_MKFIFO_COMMAND" %s", fifo->name);
  system(cmd);
  sleep(1);
  return 0;
}

/*
 * open fifo
 */
int fifo_open(struct fifo_t *fifo){
  if(fifo->name == 0) return -1;

  if((fifo->fd = open(fifo->name, O_RDWR | O_NONBLOCK))<0){
    return -1;
  }

  return 0;
}


/*
 * close fifo
 */
int fifo_close(struct fifo_t *fifo){

  if(close(fifo->fd)<0){
    return -1;
  }

  return 0;
}

/*
 * close fifo
 */
int fifo_free(struct fifo_t *fifo){

  pthread_mutex_destroy(&(fifo->lock));

  return 0;
}
/*
 * Read fifo with timer
 */
int fifo_read(struct fifo_t *fifo, char *buff){
  int ret;
  char buf1[1];
  int tot = 0;
  int stat_timeout = 0;
  struct timespec ts1, ts2;

  pthread_mutex_lock(&(fifo->lock));

  /* get current time */
  clock_gettime(CLOCK_REALTIME, &ts1);
  long nsec = ts1.tv_nsec + (1000000 * fifo->timermsec);
  ts1.tv_nsec = nsec % 1000000000;
  ts1.tv_sec += nsec / 1000000000;

  while(1){
    ret = read(fifo->fd, buf1, 1);

    if(ret>0){
      buff[tot] = buf1[0];
      tot += ret;
      if(buf1[0] == '\n'){
	buff[tot-1] = '\0';
	break;
      }
    }
	
    /* check timeout */
    clock_gettime(CLOCK_REALTIME, &ts2);
    if(cmp_timespec(&ts1, &ts2) <= 0){
      stat_timeout = 1;
      break;
    }
  };

  pthread_mutex_unlock(&(fifo->lock));

  /* timeout error message */
  if(stat_timeout == 1){
    sprintf(buff, "Failed to read fifo (%s) to timeout.\n",fifo->name);
    return -1;
  }
  
  return 0;
}
