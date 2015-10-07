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
#DESCRIPTION=Script Liberar Memoria
echo ''
echo ''
echo ''
echo 'Vamos a comprobar la memoria actual disponible'
echo ''
echo ''
echo '******************************************************************************'
echo '            Memoria Actual, Antes de Liberar y Optimizar la Memoria RAM'
echo '------------------------------------------------------------------------------'
echo ''
free
echo ''
echo '******************************************************************************'
echo ''
echo 'Preparandose para liberar la Memoria RAM'
echo ''
echo ''
echo ''
echo ''
echo ''
echo ''
echo 'Optimizando Memoria RAM'
echo ''
echo ''
echo ''
sync
sleep 2 
echo 3 > /proc/sys/vm/drop_caches
echo ''
echo ''
echo ''
echo '******************************************************************************'
echo '            Memoria Actual, Despues de Liberar y Optimizar la Memoria RAM'
echo '------------------------------------------------------------------------------'
echo ''
free
echo ''
echo '******************************************************************************'
echo ''
echo ''
echo ''
echo ''
echo 'RAM liberada y Optimizada ;)'
sleep 1
echo ''
echo 'Script realizado por Team LD para https://www.lonasdigital.com'
echo 'No olvides Visitarnos ;)'
echo ''

exit 0
