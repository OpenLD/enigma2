#!/bin/sh
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
echo 'Script realizado por Team LD para http://www.lonasdigital.com'
echo 'No olvides Visitarnos ;)'
echo ''

exit 0
