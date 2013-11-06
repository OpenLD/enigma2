#!/bin/sh
#DESCRIPTION=This script Reboot the box
wget -q -O - http://127.0.0.1/web/powerstate?newstate=2
echo ""
exit 0