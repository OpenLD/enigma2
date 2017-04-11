#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##
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
from Screens.Console import Console
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Components.FileList import FileEntryComponent, FileList
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Button import Button
from Components.Label import Label
from Components.config import config, ConfigElement, ConfigText, ConfigSubsection, ConfigSelection, ConfigSubList, getConfigListEntry, NoSave, KEY_LEFT, KEY_RIGHT, KEY_OK
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.ScrollLabel import ScrollLabel
from Components.Language import language
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from Components.Sources.List import List
from Components.Pixmap import Pixmap, MultiPixmap
from Components.Sources.Progress import Progress
from Components.About import about
from Components.Converter.Converter import Converter
from Components.Converter.LdExtraInfo import LdExtraInfo
from Tools.BoundFunction import boundFunction
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
from ServiceReference import ServiceReference
from Components.PluginList import *
from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
from Components.Console import Console as iConsole
from os import popen, system, listdir, chdir, getcwd, rename as os_rename, remove as os_remove
from time import *
from types import *
import sys, socket, commands, re, new, os, gettext, _enigma, enigma, subprocess, threading, sys, traceback, time, datetime
from enigma import iServiceInformation, eTimer, eDVBDB, eDVBCI_UI, eListboxPythonStringContent, eListboxPythonConfigContent, gFont, loadPNG, eListboxPythonMultiContent, iServiceInformation, iPlayableService, eDVBFrontendParametersSatellite
from Components.Element import cached
from Components.Converter.Poll import Poll

class LDBluePanel(Screen):
	skin = """
<screen name="LDBluePanel" position="center,center" size="1150,650">
<ePixmap position="700,10" zPosition="1" size="450,700" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/menu/fondo.png" alphatest="blend" transparent="1" />
<widget source="global.CurrentTime" render="Label" position="35,10" size="500,24" font="Regular; 21" foregroundColor="#FFFFFF" halign="left" transparent="1" zPosition="5">
		<convert type="ClockToText">>Format%H:%M:%S</convert>
</widget>
<widget source="session.CurrentService" render="Label" position="256,25" size="240,24" font="Regular; 15" backgroundColor="transpBlack" halign="left" transparent="1" zPosition="5">
		<convert type="LdExtraInfo">CryptoNameCaid</convert>
</widget>
<widget source="session.CurrentService" render="Label" position="352,25" size="240,24" font="Regular; 15" backgroundColor="transpBlack" halign="left" transparent="1" zPosition="5">
		<convert type="LdExtraInfo">E-C-N</convert>
</widget>
<widget source="session.FrontendInfo" render="FixedLabel" text="DVB-S" position="195,25" size="240,24" font="Regular; 15" backgroundColor="transpBlack" transparent="1" halign="left">
<convert type="FrontendInfo">TYPE</convert>
<convert type="ValueRange">0,0</convert>
<convert type="ConditionalShowHide" />
</widget>
<widget source="session.FrontendInfo" render="FixedLabel" text="DVB-S2" position="195,25" size="240,24" font="Regular; 15" backgroundColor="transpBlack" transparent="1" halign="left">
<convert type="FrontendInfo">TYPE</convert>
<convert type="ValueRange">0,0</convert>
<convert type="ConditionalShowHide" />
</widget>
<widget source="session.FrontendInfo" render="FixedLabel" text="DVB-C" position="195,25" size="240,24" font="Regular; 15" backgroundColor="transpBlack" transparent="1" halign="left">
<convert type="FrontendInfo">TYPE</convert>
<convert type="ValueRange">1,1</convert>
<convert type="ConditionalShowHide" />
</widget>
<widget source="session.FrontendInfo" render="FixedLabel" text="DVB-T" position="195,25" size="240,24" font="Regular; 15" backgroundColor="transpBlack" transparent="1" halign="left">
<convert type="FrontendInfo">TYPE</convert>
<convert type="ValueRange">2,2</convert>
<convert type="ConditionalShowHide" />
</widget>
<widget source="session.FrontendInfo" render="FixedLabel" text="DVB-T2" position="195,25" size="240,24" font="Regular; 15" backgroundColor="transpBlack" transparent="1" halign="left">
<convert type="FrontendInfo">TYPE</convert>
<convert type="ValueRange">2,2</convert>
<convert type="ConditionalShowHide" />
</widget>
<widget source="session.FrontendInfo" render="FixedLabel" text="ATSC" position="195,25" size="240,24" font="Regular; 15" backgroundColor="transpBlack" transparent="1" halign="left">
<convert type="FrontendInfo">TYPE</convert>
<convert type="ValueRange">3,3</convert>
<convert type="ConditionalShowHide" />
</widget>
<widget source="session.CurrentService" render="FixedLabel" text="IPTV" position="195,25" size="240,24" font="Regular; 15" backgroundColor="transpBlack" transparent="1" halign="left">
<convert type="ServiceInfo">IsStream</convert>
<convert type="ConditionalShowHide" />
</widget>
<ePixmap position="25,55" size="510,255" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/menu/bp_deko.png" zPosition="1" alphatest="on" />
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" position="30,590" size="150,30" alphatest="on" />
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green150x30.png" position="200,590" size="150,30" alphatest="on" />
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/yellow150x30.png" position="370,590" size="150,30" alphatest="on" />
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/blue150x30.png" position="543,590" size="150,30" alphatest="on" />
<widget name="key_red" position="30,594" zPosition="1" size="150,25" font="Regular; 18" halign="center" backgroundColor="red" transparent="1" />
<widget name="key_green" position="200,594" zPosition="1" size="150,25" font="Regular; 18" halign="center" backgroundColor="green" transparent="1" />
<widget name="key_yellow" position="370,594" zPosition="1" size="150,25" font="Regular; 18" halign="center" backgroundColor="yellow" transparent="1" />
<widget name="key_blue" position="543,594" zPosition="1" size="150,25" font="Regular; 18" halign="center" backgroundColor="blue" transparent="1" />
<widget name="lab1" position="190,80" size="235,25" font="Regular; 18" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget name="list" position="35,116" size="320,25" zPosition="2" scrollbarMode="showOnDemand" foregroundColor="#BDBDBD" backgroundColor="transpBlack" transparent="1" />
<widget name="lab2" position="35,149" size="120,25" font="Regular; 19" halign="left" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget name="Ilab0" position="35,149" size="245,25" font="Regular; 19" halign="left" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget name="activecam" position="166,149" size="245,25" font="Regular; 19" halign="left" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget name="Ilab1" position="40,183" size="340,25" font="Regular; 18" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget name="Ilab2" position="40,208" size="340,25" font="Regular; 18" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget name="Ilab3" position="40,233" size="340,25" font="Regular; 18" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget name="Ilab4" position="40,258" size="340,25" font="Regular; 18" zPosition="2" backgroundColor="transpBlack" transparent="1" />
<widget source="session.CurrentService" render="Label" position="40,293" size="505,380" font="Regular; 16" halign="left" backgroundColor="transpBlack" transparent="1" zPosition="2">
		<convert type="LdExtraInfo">Ecmtext</convert>
</widget>
<widget source="session.CurrentService" render="Label" position="40,415" size="505,380" font="Regular; 14" halign="left" backgroundColor="transpBlack" transparent="1" zPosition="2">
		<convert type="LdExtraInfo">PIDtext</convert>
</widget>
<widget source="session.CurrentService" render="Label" position="40,490" size="505,380" font="Regular; 13" halign="left" backgroundColor="transpBlack" transparent="1" zPosition="2">
		<convert type="LdExtraInfo">InfoPeer</convert>
</widget>
</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self['key_green'] = Label(_("Plugins"))
		self['key_red'] = Label(_("Daemons"))
		self['key_yellow'] = Label(_("Info"))
		self['key_blue'] = Label(_("Settings"))
		self['lab1'] = Label()
		self['lab2'] = Label()
		if config.osd.language.value == 'es_ES':
			self['Ilab0'] = Label(_('CAM Activa: '))
		else:
			self['Ilab0'] = Label(_('CAM Active: '))
		self['Ilab1'] = Label()
		self['Ilab2'] = Label()
		self['Ilab3'] = Label()
		self['Ilab4'] = Label()
		self['activecam'] = Label()
		self.emlist = []
		self.populate_List()
		self['list'] = MenuList(self.emlist)
		totcam = str(len(self.emlist))
		if config.osd.language.value == 'es_ES':
			self['lab1'].setText(totcam + '   ' + _('CAMs Instalada'))
		else:
			self['lab1'].setText(totcam + '   ' + _('CAMs Installed'))
		self.onShow.append(self.updateBP)
		self['myactions'] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions'], {'ok': self.keyOk,
		 'cancel': self.close,
		 'green': self.keyGreen,
		 'red': self.keyRed,
		 'yellow': self.keyYellow,
		 'blue': self.keyBlue}, -1)

	def populate_List(self):
		self.camnames = {}
		cams = listdir('/usr/camscript')
		for fil in cams:
			if fil.find('Ncam_') != -1:
				f = open('/usr/camscript/' + fil, 'r')
				for line in f.readlines():
					if line.find('CAMNAME=') != -1:
						line = line.strip()
						name = line[9:-1]
						self.emlist.append(name)
						self.camnames[name] = '/usr/camscript/' + fil

				f.close()

		if fileExists('/etc/LdCamConf') == False:
			out = open('/etc/LdCamConf', 'w')
			out.write('deldefault|/usr/camscript/Ncam_Ci.sh\n')
			out.close()

	def updateBP(self):
		name = 'N/A'
		provider = 'N/A'
		aspect = 'N/A'
		videosize = 'N/A'
		myserviceinfo = ''
		myservice = self.session.nav.getCurrentService()
		if myservice is not None:
			myserviceinfo = myservice.info()
			if self.session.nav.getCurrentlyPlayingServiceReference():
				name = ServiceReference(self.session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
			provider = self.getServiceInfoValue(iServiceInformation.sProvider, myserviceinfo)
			aspect = self.getServiceInfoValue(iServiceInformation.sAspect, myserviceinfo)
			if aspect in (1, 2, 5, 6, 9, 10, 13, 14):
				aspect = '4:3'
			else:
				aspect = '16:9'
			if myserviceinfo:
				width = myserviceinfo and myserviceinfo.getInfo(iServiceInformation.sVideoWidth) or -1
				height = myserviceinfo and myserviceinfo.getInfo(iServiceInformation.sVideoHeight) or -1
				if width != -1 and height != -1:
					videosize = '%dx%d' % (width, height)
		self['Ilab1'].setText(_('Name: ') + name)
		self['Ilab2'].setText(_('Provider: ') + provider)
		self['Ilab3'].setText(_('Aspect Ratio: ') + aspect)
		self['Ilab4'].setText(_('Videosize: ') + videosize)
		self.defaultcam = '/usr/camscript/Ncam_Ci.sh'
		f = open('/etc/LdCamConf', 'r')
		for line in f.readlines():
			parts = line.strip().split('|')
			if parts[0] == 'deldefault':
				self.defaultcam = parts[1]

		f.close()
		self.defCamname = 'Common Interface'
		for c in self.camnames.keys():
			if self.camnames[c] == self.defaultcam:
				self.defCamname = c

		pos = 0
		for x in self.emlist:
			if x == self.defCamname:
				self['list'].moveToIndex(pos)
				break
			pos += 1

		self['activecam'].setText(self.defCamname)

	def getServiceInfoValue(self, what, myserviceinfo):
		if myserviceinfo is None:
			return ''
		else:
			v = myserviceinfo.getInfo(what)
			if v == -2:
				v = myserviceinfo.getInfoString(what)
			elif v == -1:
				v = 'N/A'
			return v

	def keyOk(self):
		self.sel = self['list'].getCurrent()
		self.newcam = self.camnames[self.sel]
		inme = open('/etc/LdCamConf', 'r')
		out = open('/etc/LdCamConf.tmp', 'w')
		for line in inme.readlines():
			if line.find('deldefault') == 0:
				line = 'deldefault|' + self.newcam + '\n'
			out.write(line)

		out.close()
		inme.close()
		os_rename('/etc/LdCamConf.tmp', '/etc/LdCamConf')
		out = open('/etc/CurrentLdCamName', 'w')
		out.write(self.sel)
		out.close()
		cmd = 'cp -f ' + self.newcam + ' /usr/bin/StartLdCam'
		system(cmd)
		cmd = 'STOP_CAMD,' + self.defaultcam
		self.sendtoLd_sock(cmd)
		self.session.openWithCallback(self.keyOk2, startstopCam, self.defCamname, _('Stopping'))

	def keyOk2(self):
		os.system('/usr/bin/StartLdCam stop 2>/dev/null')
		cmd = 'NEW_CAMD,' + self.newcam
		self.sendtoLd_sock(cmd)
		oldcam = self.camnames[self.sel]
		self.session.openWithCallback(self.myclose, startstopCam, self.sel, _('Starting'))

	def sendtoLd_sock(self, data):
		client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		if fileExists('/tmp/OpenLD.socket'):
			try:
				client_socket.connect('/tmp/OpenLD.socket')
			except:
				pass
		else:
			os.system('start-stop-daemon -S -b -x /usr/bin/openldsocker 2>/dev/null')
			os.system('/etc/init.d/openldsocker stop 2>/dev/null')
			os.system('/etc/init.d/openldsocker start 2>/dev/null')
			self.session.open(MessageBox, _("We have not found OpenLD.socket and we have generated the new temporay Socket..."), MessageBox.TYPE_INFO, timeout = 8)
			client_socket.connect('/tmp/OpenLD.socket')
		client_socket.send(data)
		client_socket.close()

	def keyBlue(self):
		from LdSet import LDSettings
		self.session.open(LDSettings)

	def keyGreen(self):
		from Plugins.Extensions.LDteam.LdPlugin import LDPluginPanel
		self.session.open(LDPluginPanel)

	def keyRed(self):
		from LdServ import LDServices
		self.session.open(LDServices)

	def keyYellow(self):
		from LdAbout import LdsysInfo
		self.session.open(LdsysInfo)

	def myclose(self):
		self.close()


class startstopCam(Screen):
	skin = """
	<screen position="center,center" size="360,200">
		<widget name="lab1" position="10,10" halign="center" size="340,180" zPosition="1" font="Regular;20" valign="center" backgroundColor="transpBlack" transparent="1"/>
		<widget name="connect" position="0,0" size="484,250" zPosition="-1" transparent="1" />
	</screen>"""

	def __init__(self, session, name, what):
		Screen.__init__(self, session)
		msg = _('Please wait ') + '%s\n %s ...' % (what, name)
		self['connect'] = MultiPixmap()
		self['lab1'] = Label(msg)
		self.delay = 800
		if what == _('Starting'):
			self.delay = 3000
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.end)
		self.onShow.append(self.startShow)

	def startShow(self):
		self.activityTimer.start(self.delay)

	def end(self):
		self.activityTimer.stop()
		del self.activityTimer
		self.close()

class LDBp:

	def __init__(self):
		self['LDBp'] = ActionMap(['InfobarExtensions'], {'LDBpshow': self.showLDBp})

	def showLDBp(self):
		self.session.openWithCallback(self.callNabAction, LDBluePanel)

	def callNabAction(self, *args):
		if len(args):
			actionmap, context, action = args
			actionmap.action(context, action)
