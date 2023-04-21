# Makefile for device handlers

CC	= gcc

COMMON	= ../../common

CFLAGS	= -Wall -Wno-unused-result -O0 -std=gnu99 -I$(COMMON) -I/usr/local/milk/include
LIBS	= -lpthread -lrt -lm -lcfitsio -L/usr/local/milk/lib -lImageStreamIO


objects = howfs.o howfs_cmd.o howfs_conf.o \
	  lowfs.o lowfs_cmd.o lowfs_conf.o \
	  entshut.o entshut_cmd.o entshut_conf.o \
	  shms.o shms_cmd.o shms_conf.o	\
          adf.o adf_cmd.o adf_conf.o \
          loop.o loop_cmd.o loop_conf.o \
          gain.o gain_cmd.o gain_conf.o \
          status.o status_cmd.o status_conf.o \
          dm.o dm_cmd.o dm_conf.o \
          tt.o tt_cmd.o tt_conf.o \
          wtt.o wtt_cmd.o wtt_conf.o \
          apdsafe.o apdsafe_cmd.o apdsafe_conf.o \
	  cmtx.o cmtx_cmd.o cmtx_conf.o \
	  fifo_func.o

.PHONY: all clean depend

all: $(objects)

clean:
	rm -f *.o

depend:
	$(CC) $(CFLAGS) -MM *.c > Makefile.depend

client: client.o socket.o
	$(CC) $(CFLAGS) -o $@ $^

-include Makefile.depend
