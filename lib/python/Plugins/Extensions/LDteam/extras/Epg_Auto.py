#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##
## Epg_Auto for Enigma2
##
## Copyright (c) 2012-2015 OpenLD
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
from time import sleep
from threading import Thread
from random import random
import os, sys, commands, gettext, subprocess, threading, sys, traceback, time, datetime
from os import system, remove as os_remove, rename as os_rename, popen, getcwd, chdir
##########################################################################
class ProgressBar(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()

    def run(self):
        event = self.event  # make local
        while not event.is_set():
            for i in range(100):  # Porcentaje disponible
                time.sleep(2)  # sleep por 2 segundo
                sys.stdout.write("\r%d%%" % i)
                sys.stdout.flush()
            event.wait(2)  # pausar por 2 segundo
        sys.stdout.write("\n")

    def stop(self):
        self.event.set()

# Liberamos RAM por si acaso :p
print ("Liberando RAM")
commands.getstatusoutput('sync ; echo 3 > /proc/sys/vm/drop_caches')
print ("RAM Liberada Correctamente")

# Recargamos los bouquets para actualizar el listado
print ("Recargando Bouquets")
commands.getstatusoutput('nohup wget -q -O - http://127.0.0.1/web/getservices > /dev/null')
print ("Cambio al canal guia")
commands.getstatusoutput('nohup wget -q -O - http://127.0.0.1/web/zap?sRef=1:0:1:75A9:422:1:C00000:0:0:0:&title=Iniciando%20EPG > /dev/null')
commands.getstatusoutput('sleep 3 > /dev/null')
print ("Iniciando Canal Portada")
commands.getstatusoutput('nohup wget -q -O - http://127.0.0.1/web/zap?sRef=1:0:1:75C6:422:1:C00000:0:0:0:&title=Actualizando%20EPG > /dev/null')
commands.getstatusoutput('sleep 3 > /dev/null')

# Se avisa por pantalla que esto puede llevar un tiempo...
commands.getstatusoutput('nohup wget -O /dev/null -q "http://127.0.0.1/web/message?text=ESTE%20PROCESO%20PUEDE%20TARDAR%20UN%20TIEMPOo&type=2&timeout=10"')
commands.getstatusoutput('sleep 3 > /dev/null')

print ("Actualizando EPG... (Primer Pase)")
# Se inicia la barra de progreso
progress_bar = ProgressBar()
progress_bar.start()
# Termina la barra de progreso
commands.getstatusoutput('nohup wget -O /dev/null -q "http://127.0.0.1/web/message?text=Actualizando%20EPG%0APor%20Favor%20no%20toque%20nada%20y%20espere%0APRIMER%20PASE&type=2&timeout=199"')
progress_bar.stop()
progress_bar.join()
commands.getstatusoutput('sleep 1 > /dev/null')

print ("Actualizando EPG... (Segundo Pase)")
# Se inicia la barra de progreso
progress_bar = ProgressBar()
progress_bar.start()
commands.getstatusoutput('nohup wget -O /dev/null -q "http://127.0.0.1/web/message?text=Actualizando%20EPG%0APor%20Favor%20no%20toque%20nada%20y%20espere%0ASEGUNDO%20PASE&type=2&timeout=199"')
# Termina la barra de progreso
progress_bar.stop()
progress_bar.join()
commands.getstatusoutput('sleep 1 > /dev/null')

print ("Actualizando EPG... (Tercer Pase)")
progress_bar = ProgressBar()
progress_bar.start()
# Termina la barra de progreso
commands.getstatusoutput('nohup wget -O /dev/null -q "http://127.0.0.1/web/message?text=Actualizando%20EPG%0APor%20Favor%20no%20toque%20nada%20y%20espere%0ATERCER%20PASE&type=2&timeout=199"')
progress_bar.stop()
progress_bar.join()
commands.getstatusoutput('sleep 1 > /dev/null')

print ("EPG Actualizado")
print ("Cambio al Canal 1")
commands.getstatusoutput('nohup wget -q -O - http://127.0.0.1/web/zap?sRef=1:0:19:7863:41A:1:C00000:0:0:0: > /dev/null')
# Recargamos los bouquets para actualizar el listado
print ("Recargando Bouquets")
commands.getstatusoutput('nohup wget -q -O - http://127.0.0.1/web/getservices > /dev/null')
commands.getstatusoutput('killall -9 wget > /dev/null')

# Liberamos RAM para asegurarnos
print ("Liberando RAM")
commands.getstatusoutput('sync ; echo 3 > /proc/sys/vm/drop_caches')
print ("RAM Liberada Correctamente")
