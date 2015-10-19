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
#-------------------------------------------------------------------
# EPG
# Movistar+ (Spanish)
# Astra 19.2
#
#-------------------------------------------------------------------
# Cambiar al canal portada
CHANNEL=1:0:1:75C6:422:1:C00000:0:0:0:
# Cambiar al canal 1
CHANNEL2=1:0:19:7863:41A:1:C00000:0:0:0:
# Cambiar al canal guia
CHANNEL3=1:0:1:75A9:422:1:C00000:0:0:0:
echo "Recargando Bouquets"
wget -q -O - http://127.0.0.1/web/getservices > /dev/null
echo "Cambio al canal guia"
wget -q -O - http://127.0.0.1/web/zap?sRef=$CHANNEL3&title=Iniciando%20EPG > /dev/null
sleep 3 > /dev/null
echo "Iniciando Canal Portada"
wget -q -O - http://127.0.0.1/web/zap?sRef=$CHANNEL&title=Actualizando%20EPG > /dev/null
sleep 3 > /dev/null
echo "Actualizando EPG..."
wget -O /dev/null -q "http://127.0.0.1/web/message?text=Actualizando%20EPG%0APor%20Favor%20no%20toque%20nada%20y%20espere&type=2&timeout=300"
sleep 300 > /dev/null
echo "EPG Actualizado"
echo "Cambio al Canal 1"
wget -q -O - http://127.0.0.1/web/zap?sRef=$CHANNEL2 > /dev/null
echo "Recargando Bouquets"
wget -q -O - http://127.0.0.1/web/getservices > /dev/null
killall -9 wget > /dev/null
exit 0
