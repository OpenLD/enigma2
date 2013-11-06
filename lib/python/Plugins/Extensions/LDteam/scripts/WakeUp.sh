#!/bin/sh
#DESCRIPTION=This script WakeUp the box
wget -q -O - http://127.0.0.1/web/powerstate?newstate=4
echo ""
exit 0