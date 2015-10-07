#!/bin/sh
# 
# Copyright (c) 2012-2015 OpenLD
#          Javier Sayago <admin@lonasdigital.com>
# Contact: javilonas@esp-desarrolladores.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#DESCRIPTION=This script shows the ecm-, emm- and pid.info for some emu's
FIN="================================="
echo $FIN
echo "ecm.info:"
echo $FIN
if [ -e /tmp/ecm.info ]; then
    cat /tmp/ecm.info
else
    echo "No ecm.info found."
fi
echo ""
echo $FIN
echo "ecm1.info:"
echo $FIN
if [ -e /tmp/ecm1.info ]; then
    cat /tmp/ecm1.info
else
    echo "No ecm1.info found."
fi
echo ""
echo $FIN
echo "emm.info:"
echo $FIN
if [ -e /tmp/emm.info ]; then
    cat /tmp/emm.info
else
    echo "No emm.info found."
fi
echo ""
echo $FIN
echo "pid.info:"
echo $FIN
if [ -e /tmp/pid.info ]; then
    cat /tmp/pid.info
else
    echo "No pid.info found."
fi
echo ""
echo $FIN
echo ""
exit 0
