#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##############################################################################
#                          <<< Tuner Server >>>
#
#                      2012 meo <lupomeo@hotmail.com>
#
#  This file is open source software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License version 2 as
#               published by the Free Software Foundation.
#
#                    Modified for OE-Allinace by rossi2000
#
##############################################################################
#
# This plugin implement the Tuner Server feature included.
# Author: meo / rossi2000
# Please Respect credits
#
# Adapted by Javilonas for OpenLD (Blue Panel)
# Last Updated: 17/04/2016
##############################################################################

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.InputBox import InputBox
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.ConfigList import ConfigListScreen
from Components.Harddisk import harddiskmanager
from Components.config import getConfigListEntry, config, ConfigElement, ConfigYesNo, ConfigText, ConfigSelection, ConfigSubList, ConfigNumber, ConfigSubsection, ConfigPassword, ConfigSubsection, ConfigClock, ConfigDateTime, ConfigInteger, configfile, NoSave, KEY_LEFT, KEY_RIGHT, KEY_OK
from Components.Label import Label
from Components.Network import iNetwork
from Components.Language import language
from Tools.Directories import fileExists, resolveFilename
from enigma import eServiceCenter, eServiceReference, eTimer
from shutil import rmtree, move, copy
import os

class TunerServer(Screen):
	if config.osd.language.value == 'es_ES':
		skin = """
		<screen position="center,center" size="905,610" >
			<widget name="lab1" position="5,2" size="890,490" font="Regular;19" transparent="0"/>
			<widget name="lab2" position="45,500" size="300,30" font="Regular;20" valign="center" halign="right" transparent="0"/>
			<widget name="labstop" position="355,500" size="260,30" font="Regular;20" valign="center" halign="center" backgroundColor="red"/>
			<widget name="labrun" position="355,500" size="260,30" zPosition="1" font="Regular;20" valign="center" halign="center" backgroundColor="green"/>
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" position="125,550" size="150,40" alphatest="on"/>
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green150x30.png" position="365,550" size="150,40" alphatest="on"/>
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/yellow150x30.png" position="600,550" size="150,40" alphatest="on" />
			<widget name="key_red" position="125,545" zPosition="1" size="150,40" font="Regular;19" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>
			<widget name="key_green" position="365,545" zPosition="1" size="150,40" font="Regular;19" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
			<widget name="key_yellow" position="600,545" zPosition="1" size="150,40" font="Regular;19" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		</screen>"""

		def __init__(self, session):
			Screen.__init__(self, session)
			Screen.setTitle(self, _('Tuner Server OpenLD'))
			mytext = """
Este plugin va a crear un servidor del sintonizador incluido (vTuner). Podremos compartir los sintonizadores de este receptor con otro STB, PC u otro dispositivo compatible existente dentro de su red local.
El servidor va a construir una lista de canales virtuales en el directorio /media/hdd/tuner de este receptor (necesita estar mapeada la ruta /media/hdd/tuner para que funcione).
Una vez construido el servidor, podremos acceder al/los sintonizador/es de este receptor desde los clientes existentes en la LAN interna utilizando NFS, CIFS, UPnP o cualquier otro punto de montaje de red.\n
IMPORTANTE!! El sintonizador del servidor (este receptor) tiene que estar disponible. Esto significa que si usted sólo tiene un sintonizador en su receptor, solo vas a transmitir el canal que está viendo (o cualquier canal que elijas si el receptor lo tienes en standby).
Recuerde seleccionar la pista de audio correcta en los ajustes de audio si no hay audio o el idioma no es el correcto en el streaming.\n
NOTA: El servidor se construye, sobre la base de su IP interna actual y la lista de canales actual de este receptor. Si cambia de IP (DHCP ACTIVO) o la lista de canales se actualiza, vas a tener que reconstruir la base de datos del servidor nuevamente.\n
			"""
			self['lab1'] = Label(_(mytext))
			self['lab2'] = Label(_('Estado actual:'))
			self['labstop'] = Label(_('Servidor Inactivo'))
			self['labrun'] = Label(_('Servidor Activo'))
			self['key_red'] = Label(_('Construir'))
			self['key_green'] = Label(_('Inhabilitar'))
			self['key_yellow'] = Label(_('Close'))
			self.my_serv_active = False
			self.ip = '0.0.0.0'
			self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close,
			 'back': self.close,
			 'red': self.ServStart,
			 'green': self.ServStop,
			 'yellow': self.close})
			self.activityTimer = eTimer()
			self.activityTimer.timeout.get().append(self.doServStart)
			self.onClose.append(self.delTimer)
			self.onLayoutFinish.append(self.updateServ)

	else:
		skin = """
		<screen position="center,center" size="905,610" >
			<widget name="lab1" position="5,2" size="890,490" font="Regular;19" transparent="0"/>
			<widget name="lab2" position="45,500" size="300,30" font="Regular;20" valign="center" halign="right" transparent="0"/>
			<widget name="labstop" position="355,500" size="260,30" font="Regular;20" valign="center" halign="center" backgroundColor="red"/>
			<widget name="labrun" position="355,500" size="260,30" zPosition="1" font="Regular;20" valign="center" halign="center" backgroundColor="green"/>
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" position="125,550" size="150,40" alphatest="on"/>
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green150x30.png" position="365,550" size="150,40" alphatest="on"/>
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/yellow150x30.png" position="600,550" size="150,40" alphatest="on" />
			<widget name="key_red" position="125,545" zPosition="1" size="150,40" font="Regular;19" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>
			<widget name="key_green" position="365,545" zPosition="1" size="150,40" font="Regular;19" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
			<widget name="key_yellow" position="600,545" zPosition="1" size="150,40" font="Regular;19" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		</screen>"""

		def __init__(self, session):
			Screen.__init__(self, session)
			Screen.setTitle(self, _('Tuner Server OpenLD'))
			mytext = """
This plugin implements the Tuner Server feature included. It will allow you to share the tuners of this box with another STB, PC and/or another compatible device in your home network.
The server will build a virtual channels list in the folder /media/hdd/tuner on this box.
You can access the tuner(s) of this box from clients on your internal lan using nfs, cifs, UPnP or any other network mountpoint.\n
The tuner of the server (this box) has to be avaliable. This means that if you have ony one tuner in your box you can only stream the channel you are viewing (or any channel you choose if your box is in standby).
Remember to select the correct audio track in the audio menu if there is no audio or the wrong language is streaming.\n
NOTE: The server is built, based on your current ip and the current channel list of this box. If you change your ip or your channel list is updated, you will need to rebuild the server database.
			"""
			self['lab1'] = Label(_(mytext))
			self['lab2'] = Label(_('Current Status:'))
			self['labstop'] = Label(_('Server Disabled'))
			self['labrun'] = Label(_('Server Enabled'))
			self['key_red'] = Label(_('Build'))
			self['key_green'] = Label(_('Disable'))
			self['key_yellow'] = Label(_('Close'))
			self.my_serv_active = False
			self.ip = '0.0.0.0'
			self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close,
			 'back': self.close,
			 'red': self.ServStart,
			 'green': self.ServStop,
			 'yellow': self.close})
			self.activityTimer = eTimer()
			self.activityTimer.timeout.get().append(self.doServStart)
			self.onClose.append(self.delTimer)
			self.onLayoutFinish.append(self.updateServ)

	def ServStart(self):
		if os.path.ismount('/media/hdd'):
			if config.osd.language.value == 'es_ES':
				self['lab1'].setText(_('Construyendo el servidor\nPor favor espere ...'))
				self.activityTimer.start(10)
			else:
				self['lab1'].setText(_('Your server is now building\nPlease wait ...'))
				self.activityTimer.start(10)
		else:
			self.session.open(MessageBox, _("Sorry, but you need to have a device mounted at '/media/hdd'"), MessageBox.TYPE_INFO, timeout=5)

	def doServStart(self):
		self.activityTimer.stop()
		if os.path.exists('/media/hdd/tuner'):
			rmtree('/media/hdd/tuner')
		ifaces = iNetwork.getConfiguredAdapters()
		for iface in ifaces:
			ip = iNetwork.getAdapterAttribute(iface, 'ip')
			ipm = '%d.%d.%d.%d' % (ip[0],
			 ip[1],
			 ip[2],
			 ip[3])
			if ipm != '0.0.0.0':
				self.ip = ipm

		os.mkdir('/media/hdd/tuner', 0755)
		s_type = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'
		serviceHandler = eServiceCenter.getInstance()
		services = serviceHandler.list(eServiceReference('%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet' % s_type))
		bouquets = services and services.getContent('SN', True)
		count = 1
		for bouquet in bouquets:
			self.poPulate(bouquet, count)
			count += 1

		if config.osd.language.value == 'es_ES':
			mytext = "Servidor disponible en IP %s\nPara acceder a los sintonizadores de este receptor puedes conectarte desde la LAN o UPnP.\n\n1) Para conectar desde la LAN tienes que montar el directorio /media/hdd de este receptor en el directorio del receptor cliente /media/hdd. Una vez realizado todo esto, ya puedes acceder a la lista de canales del servidor desde el receptor cliente en Media player -> Disco duro -> tuner.\n\n2) Para conectar via UPnP necesitas un servidor UPnP que pueda gestionar archivos .m3u como MediaTomb." % (self.ip)
			self['lab1'].setText(_(mytext))
		else:
			mytext = "Server avaliable on ip %s\nTo access this box's tuners you can connect via Lan or UPnP.\n\n1) To connect via lan you have to mount the /media/hdd folder of this box in the client /media/hdd folder. Then you can access the tuners server channel list from the client Media player -> Harddisk -> tuner.\n\n2) To connect via UPnP you need an UPnP server that can manage .m3u files like Mediatomb." % (self.ip)
			self['lab1'].setText(_(mytext))
		self.session.open(MessageBox, _('Build Complete!'), MessageBox.TYPE_INFO, timeout=5)
		self.updateServ()

	def poPulate(self, bouquet, count):
		n = '%03d_' % count
		name = n + self.cleanName(bouquet[1])
		path = '/media/hdd/tuner/' + name
		os.mkdir(path, 0755)
		serviceHandler = eServiceCenter.getInstance()
		services = serviceHandler.list(eServiceReference(bouquet[0]))
		channels = services and services.getContent('SN', True)
		count2 = 1
		for channel in channels:
			if not int(channel[0].split(':')[1]) & 64:
				n2 = '%03d_' % count2
				filename = path + '/' + n2 + self.cleanName(channel[1]) + '.m3u'
				try:
					out = open(filename, 'w')
				except:
					continue

				out.write('#EXTM3U\n')
				out.write('#EXTINF:-1,' + channel[1] + '\n')
				out.write('http://' + self.ip + ':8001/' + channel[0] + '\n\n')
				out.close()
				count2 += 1

	def cleanName(self, name):
		name = name.replace(' ', '_')
		name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
		name = name.replace('.', '_')
		name = name.replace('<', '')
		name = name.replace('<', '')
		name = name.replace('/', '')
		return name

	def ServStop(self):
		if self.my_serv_active == True:
			if config.osd.language.value == 'es_ES':
				self['lab1'].setText(_('El servidor ha sido eliminado\nPor favor pulse exit para salir.'))
			else:
				self['lab1'].setText(_('The server has been removed\nPlease press exit button to close.'))
		if os.path.exists('/media/hdd/tuner'):
			rmtree('/media/hdd/tuner')
		mybox = self.session.open(MessageBox, _('Tuner Server Disabled.'), MessageBox.TYPE_INFO, timeout=5)
		mybox.setTitle(_('Info'))
		self.updateServ()
		self.session.open(MessageBox, _('Server now disabled!'), MessageBox.TYPE_INFO, timeout=5)

	def updateServ(self):
		self['labrun'].hide()
		self['labstop'].hide()
		self.my_serv_active = False
		if os.path.isdir('/media/hdd/tuner'):
			self.my_serv_active = True
			self['labstop'].hide()
			self['labrun'].show()
		else:
			self['labstop'].show()
			self['labrun'].hide()

	def delTimer(self):
		del self.activityTimer


def settings(menuid, **kwargs):
	if menuid == 'network':
		return [(_('Tuner Server setup'),
		 main,
		 'tuner_server_setup',
		 None)]
	else:
		return []


def main(session, **kwargs):
	session.open(TunerServer)
