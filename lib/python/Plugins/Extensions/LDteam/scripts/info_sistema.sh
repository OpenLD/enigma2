#!/bin/sh
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


