#!/bin/sh
#DESCRIPTION=This script Restart Enigma2
wget -q -O - http://127.0.0.1/web/powerstate?newstate=3
echo ""
exit 0