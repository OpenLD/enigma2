#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##
## LiberarRAM for Enigma2
##
## Copyright (c) 2012-2016 OpenLD
##          Javier Sayago <admin@lonasdigital.com>
## Contact: javilonas@esp-desarrolladores.com
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
##########################################################################
from time import *
from types import *
import sys, commands, gettext, subprocess, threading, sys, traceback, time, datetime
from os import system, remove as os_remove, rename as os_rename, popen, getcwd, chdir
##########################################################################
print ("Liberando RAM")
commands.getstatusoutput('sync ; echo 3 > /proc/sys/vm/drop_caches')
print ("RAM Liberada Correctamente")
commands.getstatusoutput('sync ; echo 0 > /proc/sys/vm/drop_caches')
print ("De vuelta al estado normal (no libera nada)")
