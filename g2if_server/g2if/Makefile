# Makefile

CC	= gcc

CFLAGS	= -Wall -Wno-unused-result -O0 -std=gnu99 -I$(COMMON) -I$(DEVICE) -fPIC -I/usr/local/milk/include
LIBS	= -lm -lpthread -lrt -lgsl -lgslcblas -lcfitsio -L/usr/local/milk/lib
LISIO   = -lImageStreamIO

RPATHFLAG = -Wl,-rpath /usr/local/milk/lib

COMMON	= ../common
DEVICE	= device

PREFIX	= .

PROGRAMS = g2if_server g2if_client
SCRIPTS = g2if_start g2if_stop g2if_restart
OBJECTS = $(COMMON)/alias.o $(COMMON)/comm.o $(COMMON)/conf.o \
	$(COMMON)/device.o $(COMMON)/log.o $(COMMON)/poll.o $(COMMON)/server.o \
	$(COMMON)/socket.o $(COMMON)/stringx.o \
	$(COMMON)/tlock.o $(COMMON)/tpool.o $(COMMON)/libtrack.o $(COMMON)/tool.o \
	$(DEVICE)/howfs.o $(DEVICE)/howfs_cmd.o $(DEVICE)/howfs_conf.o \
	$(DEVICE)/lowfs.o $(DEVICE)/lowfs_cmd.o $(DEVICE)/lowfs_conf.o \
	$(DEVICE)/entshut.o $(DEVICE)/entshut_cmd.o $(DEVICE)/entshut_conf.o \
	$(DEVICE)/shms.o $(DEVICE)/shms_cmd.o $(DEVICE)/shms_conf.o \
	$(DEVICE)/adf.o $(DEVICE)/adf_cmd.o $(DEVICE)/adf_conf.o \
	$(DEVICE)/loop.o $(DEVICE)/loop_cmd.o $(DEVICE)/loop_conf.o \
	$(DEVICE)/gain.o $(DEVICE)/gain_cmd.o $(DEVICE)/gain_conf.o \
	$(DEVICE)/status.o $(DEVICE)/status_cmd.o $(DEVICE)/status_conf.o \
	$(DEVICE)/dm.o $(DEVICE)/dm_cmd.o $(DEVICE)/dm_conf.o \
	$(DEVICE)/tt.o $(DEVICE)/tt_cmd.o $(DEVICE)/tt_conf.o \
	$(DEVICE)/wtt.o $(DEVICE)/wtt_cmd.o $(DEVICE)/wtt_conf.o \
	$(DEVICE)/apdsafe.o $(DEVICE)/apdsafe_cmd.o $(DEVICE)/apdsafe_conf.o \
	$(DEVICE)/cmtx.o $(DEVICE)/cmtx_cmd.o $(DEVICE)/cmtx_conf.o \
	$(DEVICE)/fifo_func.o

.PHONY: all install install-server install-client clean depend

all: g2if_server g2if_client

server: g2if_server

client: g2if_client

install: install-server install-client

install-server: server
	mkdir -p $(PREFIX)/bin
	install -s -m 755 g2if_server $(PREFIX)/bin
	(cd $(PREFIX)/bin; \
		ln -sf g2if_client gain; \
		ln -sf g2if_client loop; \
		ln -sf g2if_client dm; \
		ln -sf g2if_client tt; \
		ln -sf g2if_client wtt; \
		ln -sf g2if_client cmtx; \
		ln -sf g2if_client status; \
		ln -sf g2if_client apdsafe; \
	)



install-client: client
	mkdir -p $(PREFIX)/bin
	install -s -m 755 g2if_client $(PREFIX)/bin

clean:
	rm -f $(OBJECTS) $(PROGRAMS) *.log *.status *.pid *.o

depend:
	$(CC) $(CFLAGS) -MM *.c > Makefile.depend

g2if_server: g2if_server.o $(OBJECTS)
	$(CC) $(CFLAGS) $(RPATHFLAG) -o $@ $^ $(LIBS) $(LISIO)

g2if_client: g2if_client.o $(COMMON)/socket.o $(COMMON)/stringx.o $(COMMON)/tool.o $(COMMON)/log.o
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

-include Makefile.depend
