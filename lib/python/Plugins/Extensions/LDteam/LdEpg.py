#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##
##
## Copyright (c) 2012-2017 OpenLD
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
from enigma import iServiceInformation, eTimer, eEPGCache, eDVBDB, eDVBCI_UI, eListboxPythonMultiContent, eListboxPythonConfigContent, gFont, loadPNG, eListboxPythonMultiContent, iServiceInformation, eEnv, getDesktop, pNavigation

from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.InputBox import InputBox
from Components.FileList import FileEntryComponent, FileList
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Sources.StaticText import StaticText
from Components.Sources.List import List
from Components.Label import Label
from Tools.BoundFunction import boundFunction
from Components.UsageConfig import InitUsageConfig
from Components.Pixmap import Pixmap, MultiPixmap
from Components.ConfigList import ConfigListScreen
from Components.Harddisk import harddiskmanager
from Components.config import getConfigListEntry, config, ConfigElement, ConfigYesNo, ConfigText, ConfigSelection, ConfigSubList, ConfigNumber, ConfigSubsection, ConfigPassword, ConfigClock, ConfigDateTime, ConfigInteger, configfile, ConfigSelectionNumber, NoSave, KEY_LEFT, KEY_RIGHT, KEY_OK
from Components.Sources.Progress import Progress
from Components.About import about
from Components.Network import iNetwork
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend, MultiContentEntryPixmapAlphaTest
from Screens.Setup import Setup, getSetupTitle
from Components.Language import language
from ServiceReference import ServiceReference
from Components.ScrollLabel import ScrollLabel
from Components.PluginList import *
from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
from Components.Console import Console as iConsole
from time import sleep
from re import search
from time import *
from types import *
from enigma import *
import sys, socket, traceback, re, new, os, gettext, commands, time, datetime, _enigma, enigma, Screens.Standby, subprocess, threading
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, SCOPE_SKIN
from os import system, listdir, path, remove as os_remove, rename as os_rename, popen, getcwd, chdir
from Plugins.SystemPlugins.NetworkBrowser.NetworkBrowser import NetworkBrowser
import NavigationInstance
import Components.UsageConfig

count = 0
hddchoises = [('/media/hdd/', '/media/hdd/'),
 ('/media/usb/', '/media/usb/'),
 ('/media/mmc1/', '/media/mmc1/'),
 ('/media/uSDextra/', '/media/uSDextra/'),
 ('/media/upnp/', '/media/upnp/'),
 ('/media/net/', '/media/net/'),
 ('/usr/share/enigma2/', '/usr/share/enigma2/'),
 ('/etc/enigma2/', '/etc/enigma2/')]
config.misc.epgcachepath = ConfigSelection(default='/etc/enigma2/', choices=hddchoises)
config.plugins.ldteam = ConfigSubsection()
config.plugins.ldteam.auto2 = ConfigSelection(default='no', choices=[('no', _('no')), ('yes', _('yes'))])
config.plugins.ldteam.dropmode = ConfigSelection(default = '1', choices = [
		('1', _("free pagecache")),
		('2', _("free dentries and inodes")),
		('3', _("free pagecache, dentries and inodes")),
		])
config.plugins.ldteam.epgtime2 = ConfigClock(default=58500)
config.plugins.ldteam.epgmhw2wait = ConfigNumber(default=350) # 350 seconds = 5,83 minutes

config.epg = ConfigSubsection()
config.epg.eit = ConfigYesNo(default = True)
config.epg.mhw = ConfigYesNo(default = True)
config.epg.freesat = ConfigYesNo(default = False)
config.epg.viasat = ConfigYesNo(default = True)
config.epg.netmed = ConfigYesNo(default = True)
config.epg.virgin = ConfigYesNo(default = False)
config.epg.saveepg = ConfigYesNo(default = True)

def EpgSettingsChanged(configElement):
	from enigma import eEPGCache
	mask = 0xffffffff
	if not config.epg.eit.value:
		mask &= ~(eEPGCache.NOWNEXT | eEPGCache.SCHEDULE | eEPGCache.SCHEDULE_OTHER)
	if not config.epg.mhw.value:
		mask &= ~eEPGCache.MHW
	if not config.epg.freesat.value:
		mask &= ~(eEPGCache.FREESAT_NOWNEXT | eEPGCache.FREESAT_SCHEDULE | eEPGCache.FREESAT_SCHEDULE_OTHER)
	if not config.epg.viasat.value:
		mask &= ~eEPGCache.VIASAT
	if not config.epg.netmed.value:
		mask &= ~(eEPGCache.NETMED_SCHEDULE | eEPGCache.NETMED_SCHEDULE_OTHER)
	if not config.epg.virgin.value:
		mask &= ~(eEPGCache.VIRGIN_NOWNEXT | eEPGCache.VIRGIN_SCHEDULE)
	eEPGCache.getInstance().setEpgSources(mask)
config.epg.eit.addNotifier(EpgSettingsChanged)
config.epg.mhw.addNotifier(EpgSettingsChanged)
config.epg.freesat.addNotifier(EpgSettingsChanged)
config.epg.viasat.addNotifier(EpgSettingsChanged)
config.epg.netmed.addNotifier(EpgSettingsChanged)
config.epg.virgin.addNotifier(EpgSettingsChanged)

config.epg.maxdays = ConfigSelectionNumber(min = 1, max = 365, stepwidth = 1, default = 3, wraparound = True)
def EpgmaxdaysChanged(configElement):
	from enigma import eEPGCache
	eEPGCache.getInstance().setEpgmaxdays(config.epg.maxdays.getValue())
config.epg.maxdays.addNotifier(EpgmaxdaysChanged)

config.epg.histminutes = ConfigSelectionNumber(min = 0, max = 120, stepwidth = 15, default = 0, wraparound = True)
def EpgHistorySecondsChanged(configElement):
	eEPGCache.getInstance().setEpgHistorySeconds(config.epg.histminutes.value*60)
config.epg.histminutes.addNotifier(EpgHistorySecondsChanged)

def mountp():
	pathmp = []
	if fileExists('/proc/mounts'):
		for line in open('/proc/mounts'):
			if line.find('/dev/sd') > -1:
				pathmp.append(line.split()[1].replace('\\040', ' ') + '/')

	pathmp.append('/usr/share/enigma2/')
	return pathmp

def _(txt):
	t = gettext.dgettext('messages', txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

class Ttimer(Screen):
	skin = """<screen name="Ttimer" position="center,center" zPosition="10" size="1280,720" title="Actualizacion EPG" backgroundColor="black" flags="wfNoBorder">
					<widget name="srclabel" font="Regular; 15" position="424,614" zPosition="2" valign="center" halign="center" size="500,30" foregroundColor="white" backgroundColor="black" transparent="0" />
					<widget source="progress" render="Progress" position="322,677" foregroundColor="white" size="700,20" borderWidth="1" borderColor="grey" backgroundColor="black" />

 <widget source="session.VideoPicture" render="Pig" position="center,center" size="975,475" backgroundColor="transparent" zPosition="-1" transparent="0" />
 <widget source="Title" transparent="1" render="Label" zPosition="2" valign="center" halign="left" position="100,70" size="800,50" font="Regular; 30" backgroundColor="black" foregroundColor="white" noWrap="1" />
</screen>"""

	def __init__(self, session):
		global count
		self.skin = Ttimer.skin
		Screen.__init__(self, session)
		if config.osd.language.value == 'es_ES':
			self['srclabel'] = Label(_('Por favor Espere, Actualizando Epg'))
		else:
			self['srclabel'] = Label(_('Please wait, Updating Epg'))
		if config.osd.language.value == 'es_ES':
			self.setTitle(_('Actualizando EPG'))
		else:
			self.setTitle(_('Update EPG'))
		self['progress'] = Progress(int(count))
		self['progress'].setRange(int(config.plugins.ldteam.epgmhw2wait.value - 5))
		self.session = session
		self.ctimer = enigma.eTimer()
		count = 0
		self.ctimer.callback.append(self.__run)
		self.ctimer.start(1000, 0)

	def __run(self):
		global count
		count += 1
		print '%s Epg Downloaded' % count
		self['progress'].setValue(count)
		if count > config.plugins.ldteam.epgmhw2wait.value:
			self.ctimer.stop()
			self.session.nav.playService(eServiceReference(config.tv.lastservice.value))
			rDialog.stopDialog(self.session)
			epgcache = new.instancemethod(_enigma.eEPGCache_load, None, eEPGCache)
			epgcache = eEPGCache.getInstance().save()
			if config.osd.language.value == 'es_ES':
				self.mbox = self.session.open(MessageBox, _('Epg Actualizado'), MessageBox.TYPE_INFO, timeout=5)
			else:
				self.mbox = self.session.open(MessageBox, _('Updated Epg'), MessageBox.TYPE_INFO, timeout=5)
			from Screens.Standby import inStandby
			if inStandby:
				self.session.nav.stopService()
			self.close()
		return


pdialog = ''

class runDialog:

	def __init__(self):
		self.dialog = None
		return

	def startDialog(self, session):
		global pdialog
		pdialog = session.instantiateDialog(Ttimer)
		pdialog.show()

	def stopDialog(self, session):
		pdialog.hide()


rDialog = runDialog()

class LDepgScreen(Screen, ConfigListScreen):
	skin = """
	<screen name="LDepgScreen" position="center,center" size="1150,650">
<ePixmap position="700,10" zPosition="1" size="450,700" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/menu/fondo.png" alphatest="blend" transparent="1" />
<widget source="global.CurrentTime" render="Label" position="35,10" size="500,24" font="Regular;22" foregroundColor="#FFFFFF" halign="left" transparent="1" zPosition="5">
		<convert type="ClockToText">>Format%H:%M:%S</convert>
	</widget>
  <widget position="15,50" size="680,420" name="config" scrollbarMode="showOnDemand" />
  <ePixmap position="30,590" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" alphatest="blend" />
  <widget source="key_red" render="Label" position="30,590" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
  <ePixmap position="200,590" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green150x30.png" alphatest="blend" />
<ePixmap position="370,590" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/yellow150x30.png" alphatest="blend" />
<ePixmap position="540,590" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/blue150x30.png" alphatest="blend" />
<widget source="key_blue" render="Label" position="540,590" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
  <widget source="key_green" render="Label" position="200,590" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<widget source="key_yellow" render="Label" position="370,590" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
  </screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		if config.osd.language.value == 'es_ES':
			self.setTitle(_('Opciones EPG'))
		else:
			self.setTitle(_('EPG Options'))
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		if config.osd.language.value == 'es_ES':
			self['key_blue'] = StaticText(_('Ver log'))
		else:
			self['key_blue'] = StaticText(_('Show log'))
		if config.osd.language.value == 'es_ES':
			self['key_red'] = StaticText(_('Cerrar'))
		else:
			self['key_red'] = StaticText(_('Close'))
		if config.osd.language.value == 'es_ES':
			self['key_green'] = StaticText(_('Guardar'))
		else:
			self['key_green'] = StaticText(_('Save'))
		if config.osd.language.value == 'es_ES':
			self['key_yellow'] = StaticText(_('Actualizar'))
		else:
			self['key_yellow'] = StaticText(_('Update'))
		self['setupActions'] = ActionMap(['SetupActions',
		 'WizardActions',
		 'TimerEditActions',
		 'ColorActions'], {
		 'blue': self.mhw,
		 'red': self.cancel,
		 'cancel': self.cancel,
		 'yellow': self.downepg,
		 'green': self.save,
		 'ok': self.save}, -2)
		if config.osd.language.value == 'es_ES':
			self.list.append(getConfigListEntry(_('Ruta donde almacenar el epg.dat'), config.misc.epgcachepath))
		else:
			self.list.append(getConfigListEntry(_('The path where stored epg.dat'), config.misc.epgcachepath))
		if config.osd.language.value == 'es_ES':
			self.list.append(getConfigListEntry(_('Habilitar EIT EPG'), config.epg.eit))
		else:
			self.list.append(getConfigListEntry(_('Enable EIT EPG'), config.epg.eit))
		if config.osd.language.value == 'es_ES':
			self.list.append(getConfigListEntry(_('Habilitar MHW EPG'), config.epg.mhw))
		else:
			self.list.append(getConfigListEntry(_('Enable MHW EPG'), config.epg.mhw))
		if config.osd.language.value == 'es_ES':
			self.list.append(getConfigListEntry(_('Habilitar Freesat EPG'), config.epg.freesat))
		else:
			self.list.append(getConfigListEntry(_('Enable freesat EPG'), config.epg.freesat))
		if config.osd.language.value == 'es_ES':
			self.list.append(getConfigListEntry(_('Habilitar ViaSat EPG'), config.epg.viasat))
		else:
			self.list.append(getConfigListEntry(_('Enable ViaSat EPG'), config.epg.viasat))
		if config.osd.language.value == 'es_ES':
			self.list.append(getConfigListEntry(_('Habilitar Netmed EPG'), config.epg.netmed))
		else:
			self.list.append(getConfigListEntry(_('Enable Netmed EPG'), config.epg.netmed))
		if config.osd.language.value == 'es_ES':
			self.list.append(getConfigListEntry(_('Habilitar Virgin EPG'), config.epg.virgin))
		else:
			self.list.append(getConfigListEntry(_('Enable Virgin EPG'), config.epg.virgin))
		if config.osd.language.value == 'es_ES':
			self.list.append(getConfigListEntry(_('Numero Maximo de dias en EPG'), config.epg.maxdays))
		else:
			self.list.append(getConfigListEntry(_('Maximum number of days in EPG'), config.epg.maxdays))
		if config.osd.language.value == 'es_ES':
			self.list.append(getConfigListEntry(_('Conservar los datos antiguos del EPG'), config.epg.histminutes))
		else:
			self.list.append(getConfigListEntry(_('Maintain old EPG data for'), config.epg.histminutes))
		if config.osd.language.value == 'es_ES':
			self.list.append(getConfigListEntry(_('Tiempo Duracion en Portada'), config.plugins.ldteam.epgmhw2wait))
		else:
			self.list.append(getConfigListEntry(_('Time at title page'), config.plugins.ldteam.epgmhw2wait))
		self['config'].list = self.list
		self['config'].l.setList(self.list)

	def zapTo(self, reftozap):
		self.session.nav.playService(eServiceReference(reftozap))

	def downepg(self):
		recordings = self.session.nav.getRecordings()
		rec_time = self.session.nav.RecordTimer.getNextRecordingTime()
		mytime = time.time()
		try:
			if not recordings or rec_time > 0 and rec_time - mytime() < 360:
				channel = '1:0:1:75C6:422:1:C00000:0:0:0:'
				self.zapTo(channel)
				diag = runDialog()
				diag.startDialog(self.session)
			else:
				self.mbox = self.session.open(MessageBox, _('EPG Download Cancelled - Recording active'), MessageBox.TYPE_INFO, timeout=5)
		except:
			print 'Error download mhw2 epg, record active?'

	def mhw(self):
		self.session.open(Viewmhw)

	def cancel(self):
		for i in self['config'].list:
			i[1].cancel()

		self.close(False)

	def save(self):
		config.misc.epgcache_filename.value = '%sepg.dat' % config.misc.epgcachepath.value
		config.misc.epgcache_filename.save()
		config.misc.epgcachepath.save()
		epgcache = new.instancemethod(_enigma.eEPGCache_save, None, eEPGCache)
		epgcache = eEPGCache.getInstance().save()
		config.plugins.ldteam.epgmhw2wait.save()
		config.epg.save()
		config.epg.maxdays.save()
		configfile.save()
		self.mbox = self.session.open(MessageBox, _('configuration is saved'), MessageBox.TYPE_INFO, timeout=4)

	def restart(self):
		self.session.open(TryQuitMainloop, 3)


class Viewmhw(Screen):
	skin = """
<screen name="Viewmhw" position="center,80" size="1170,600" title="View mhw2equiv.conf (/etc/mhw2equiv.conf">
	<ePixmap position="20,590" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" alphatest="blend" />
	<widget source="key_red" render="Label" position="20,560" zPosition="2" size="170,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget name="text" position="20,10" size="1130,542" font="Console;22" />
</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_('View mhw2equiv.conf (/tmp/mhw_Log.epg)'))
		self['shortcuts'] = ActionMap(['ShortcutActions', 'WizardActions'], {'cancel': self.exit,
		 'back': self.exit,
		 'red': self.exit})
		self['key_red'] = StaticText(_('Close'))
		self['text'] = ScrollLabel('')
		self.viewmhw2()

	def exit(self):
		self.close()

	def viewmhw2(self):
		list = ''
		if fileExists('/tmp/mhw_Log.epg'):
			for line in open('/tmp/mhw_Log.epg'):
				list += line

		self['text'].setText(list)
		self['actions'] = ActionMap(['OkCancelActions', 'DirectionActions'], {'cancel': self.close,
		 'up': self['text'].pageUp,
		 'left': self['text'].pageUp,
		 'down': self['text'].pageDown,
		 'right': self['text'].pageDown}, -1)
