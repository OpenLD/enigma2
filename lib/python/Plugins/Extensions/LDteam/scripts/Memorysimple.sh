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
#DESCRIPTION=Script Memorysimple
memtotal=`cat /proc/meminfo | grep "MemTotal:" | sed -e 's/MemTotal://g' | sed -e 's/\ kB//g' | sed -e 's/^[ \t]*//'`
memfree=`cat /proc/meminfo | grep "MemFree:" | sed -e 's/MemFree://g' | sed -e 's/\ kB//g' | sed -e 's/^[ \t]*//'`
buffers=`cat /proc/meminfo | grep "Buffers" | sed -e 's/Buffers://g' | sed -e 's/\ kB//g' | sed -e 's/^[ \t]*//'`
cached=`cat /proc/meminfo | grep -m 1 "Cached:" | sed -e 's/Cached://g' | sed -e 's/\ kB//g' | sed -e 's/^[ \t]*//'`
swapcached=`cat /proc/meminfo | grep "SwapCached:" | sed -e 's/SwapCached://g' | sed -e 's/\ kB//g' | sed -e 's/^[ \t]*//'`
swaptotal=`cat /proc/meminfo | grep "SwapTotal:" | sed -e 's/SwapTotal://g' | sed -e 's/\ kB//g' | sed -e 's/^[ \t]*//'`
swapfree=`cat /proc/meminfo | grep "SwapFree" | sed -e 's/SwapFree://g' | sed -e 's/\ kB//g' | sed -e 's/^[ \t]*//'`
meminuse=$(($memtotal - $memfree))
memused=$(($memtotal - $memfree - $cached - $buffers))
swapused=$(($swaptotal - $swapfree))
avblmemory=$(($memfree + $buffers + $cached))
avblmemorywswap=$(($memfree + $buffers + $cached + $swapfree))
echo "	Total	Used	Free"
echo ""
echo "mem: 	$memtotal kB	$meminuse kB	$memfree kB"
echo "-/+BufCaches		$memused kB	$avblmemory kB"
if [ "$swaptotal" -gt 0 ] ; then
echo "swap:	$swaptotal kB	$swapused kB	$swapfree kB"
echo ""
echo "The avbl memory for applications = $avblmemorywswap kB"
else
echo ""
echo "The avbl memory for applications = $avblmemory kB"
fi
echo ""

#end
