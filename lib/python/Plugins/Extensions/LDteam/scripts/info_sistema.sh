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
echo 'Voy a Informarle sobre el estado de su Receptor Sat'
echo ''
echo 'Por favor, espere un momento....'
echo ''
sleep 4
echo ''
echo '******************************************************************************'
echo '                 Tiempo Conectado y Consumo de la CPU'
echo '------------------------------------------------------------------------------'
echo ''
uptime
echo ''
echo '******************************************************************************'
echo ''
sleep 2
echo ''
echo '******************************************************************************'
echo '                      Consumo de la Memoria RAM: '
echo '------------------------------------------------------------------------------'
echo ''
free
echo ''
echo '******************************************************************************'
echo ''
sleep 2
echo ''
echo '******************************************************************************'
echo '                         Uso del Disco Duro: '
echo '------------------------------------------------------------------------------'
echo ''
df
echo ''
echo '******************************************************************************'
echo ''
sleep 2
echo ''
echo '******************************************************************************'
echo '                     Informacion y Conexiones de RED: '
echo '------------------------------------------------------------------------------'
echo ''
echo 'ATENCION!! - Esto Puede tardar un poco, por favor, aguarde un minuto.'
echo ''
netstat | grep tcp
netstat | grep unix
echo ''
ifconfig
echo ''
echo '******************************************************************************'
echo ''
sleep 1
echo ''
echo ''
echo ''
echo 'Script realizado por Team LD para http://www.lonasdigital.com'
echo 'No olvides Visitarnos ;)'
echo ''

exit 0


