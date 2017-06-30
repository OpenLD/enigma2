#!/bin/sh
# 
# Copyright (c) 2012-2017 OpenLD
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
#DESCRIPTION=Script download_settings
if [ -e /tmp/master.zip ]; then
	rm -rf /tmp/master.zip 2>/dev/null
fi
if [ -e /tmp/enigma2-plugin-settings-defaultsatld-master/ ]; then
	rm -R /tmp/enigma2-plugin-settings-defaultsatld-master/ 2>/dev/null
fi
cd /tmp/
wget https://github.com/OpenLD/enigma2-plugin-settings-defaultsatld/archive/master.zip
unzip master.zip
cp enigma2-plugin-settings-defaultsatld-master/etc/enigma2/*.tv /etc/enigma2/
cp enigma2-plugin-settings-defaultsatld-master/etc/enigma2/*.radio /etc/enigma2/
cp enigma2-plugin-settings-defaultsatld-master/etc/enigma2/lamedb /etc/enigma2/
cp enigma2-plugin-settings-defaultsatld-master/etc/enigma2/lamedb5 /etc/enigma2/
cp enigma2-plugin-settings-defaultsatld-master/etc/enigma2/blacklist /etc/enigma2/
cp enigma2-plugin-settings-defaultsatld-master/etc/enigma2/whitelist /etc/enigma2/
cd /
cd /tmp/
rm master.zip
rm -R enigma2-plugin-settings-defaultsatld-master/
sync && sleep 1
wget -qO - http://127.0.0.1/web/servicelistreload?mode=0
sync && sleep 1
wget -q -O - http://127.0.0.1/web/getservices
