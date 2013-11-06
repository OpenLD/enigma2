#!/bin/sh
#DESCRIPTION=This script will show you the performance of your internet-connection
echo "Ping google.es:"
ping -c 1 www.google.es
echo "*****************************"
echo "Ping google.com:"
ping -c 1 www.google.com
echo "*****************************"
echo ""
exit 0
