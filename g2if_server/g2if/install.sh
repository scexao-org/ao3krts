#!/bin/bash

make
make install

rm g2if_server
rm g2if_client
rm ./*.o

cd device
make clean
