# Makefile for common-use functions

CC		= gcc
CFLAGS	= -Wall -O2 -std=gnu99 -fPIC
LIBS	= -lpthread -lrt -lcfitsio

programs = client
objects = alias.o client.o comm.o conf.o device.o image.o log.o poll.o \
	server.o socket.o stage.o stringx.o tlock.o tpool.o libtrack.o tool.o

.PHONY: all clean depend

all: $(objects)

clean:
	rm -f *.o $(programs)

depend:
	$(CC) $(CFLAGS) -MM *.c > Makefile.depend

client: client.o socket.o
	$(CC) $(CFLAGS) -o $@ $^

include Makefile.depend
