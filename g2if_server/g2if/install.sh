#!/bin/bash

echo "Build client..."
make g2if_client
echo "Try build server..."
make # This will fail if ImageStreamIO is missing
echo ""
echo "Continuing..."
make install-client
make install

make clean
