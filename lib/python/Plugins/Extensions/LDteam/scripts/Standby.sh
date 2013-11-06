#!/bin/sh
#DESCRIPTION=Script Stanby
wget -q -O - http://127.0.0.1/web/powerstate?newstate=5
echo ""
exit 0