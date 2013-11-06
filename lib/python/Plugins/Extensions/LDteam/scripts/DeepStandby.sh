#!/bin/sh
#DESCRIPTION=Script Shoutdown
wget -q -O - http://127.0.0.1/web/powerstate?newstate=1
echo ""
exit 0