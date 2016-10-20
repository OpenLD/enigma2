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
#DESCRIPTION=Script Info Sistema
echo ''
echo ''
echo '****************************************'
echo '               Uptime'
echo '----------------------------------------'
echo ''
uptime
echo ''
sleep 2
echo ''
echo '****************************************'
echo '                RAM: '
echo '----------------------------------------'
echo ''
free
echo ''
sleep 2
echo ''
echo '****************************************'
echo '                HDD: '
echo '----------------------------------------'
echo ''
df
echo ''
sleep 2
echo ''
echo '****************************************'
echo '              NETWORK: '
echo '----------------------------------------'
echo ''
netstat | grep tcp
netstat | grep unix
echo ''
ifconfig
echo ''
echo ''

exit 0
