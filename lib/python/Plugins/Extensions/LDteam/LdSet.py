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
 ('/media/uSDextra/', '/media/uSDextra/'),
 ('/usr/share/enigma2/', '/usr/share/enigma2/'),
 ('/etc/enigma2/', '/etc/enigma2/')]
config.misc.epgcachepath = ConfigSelection(default='/etc/enigma2/', choices=hddchoises)
config.plugins.LDteam = ConfigSubsection()
config.plugins.LDteam.auto2 = ConfigSelection(default='no', choices=[('no', _('no')), ('yes', _('yes'))])
config.plugins.LDteam.dropmode = ConfigSelection(default='3', choices=[('1', _('free pagecache')), ('2', _('free dentries and inodes')), ('3', _('free pagecache, dentries and inodes'))])
config.plugins.LDteam.epgtime2 = ConfigClock(default=58500)
config.plugins.LDteam.epgmhw2wait = ConfigNumber(default=350) # 350 seconds = 5,83 minutes

config.epg = ConfigSubsection()
config.epg.eit = ConfigYesNo(default = True)
config.epg.mhw = ConfigYesNo(default = True)
config.epg.freesat = ConfigYesNo(default = True)
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


class LDSettings(Screen):
	skin = """
<screen name="LDSettings" position="70,35" size="1150,650">
<ePixmap position="700,10" zPosition="1" size="450,700" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/menu/fondo.png" alphatest="blend" transparent="1" />
<widget source="list" render="Listbox" position="15,10" size="660,650" scrollbarMode="showOnDemand">
<convert type="TemplatedMultiContent">
{"template": [
MultiContentEntryText(pos = (60, 1), size = (300, 40), flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),
MultiContentEntryPixmapAlphaTest(pos = (4, 2), size = (40, 40), png = 1),
],
"fonts": [gFont("Regular", 24)],
"itemHeight": 40
}
</convert>
</widget>
</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self['list'] = List(self.list)
		self.updateList()
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
		 'back': self.close})

	def openSetup(self, dialog):
		self.session.openWithCallback(self.menuClosed, Setup, dialog)

	def menuClosed(self, *res):
		pass

	def KeyOk(self):
		self.sel = self['list'].getCurrent()
		self.sel = self.sel[2]
		if self.sel == 0:
			from Plugins.Extensions.LDteam.MountManager import HddMount
			self.session.open(HddMount)
		elif self.sel == 1:
			from Plugins.Extensions.LDteam.LdFormat import LD_UsbFormat
			self.session.open(LD_UsbFormat)
		elif self.sel == 2:
			from Plugins.Extensions.LDteam.LdSwapManager import Swap
			self.session.open(Swap)
		elif self.sel == 3:
			self.openSetup('userinterface')
		elif self.sel == 4:
			from Screens.NcamInfo import NcamInfoMenu
			self.session.open(NcamInfoMenu)
		elif self.sel == 5:
			from Screens.OScamInfo import OscamInfoMenu
			self.session.open(OscamInfoMenu)
		elif self.sel == 6:
			self.session.open(LDepg)
		elif self.sel == 7:
			from Screens.Recordings import RecordingSettings
			self.session.open(RecordingSettings)
		elif self.sel == 8:
			from Plugins.SystemPlugins.Satfinder.plugin import Satfinder
			self.session.open(Satfinder)
		elif self.sel == 9:
			self.openSetup('autolanguagesetup')
		elif self.sel == 10:
			self.openSetup('usage')
		elif self.sel == 11:
			self.session.open(LDmemoria)
		elif self.sel == 12:
			from Screens.CronTimer import CronTimers
			self.session.open(CronTimers)
		elif self.sel == 13:
			from Plugins.Extensions.LDteam.LdRestartNetwork import RestartNetwork
			self.session.open(RestartNetwork)
		elif self.sel == 14:
			from Screens.CCcamInfo import CCcamInfoMain
			self.session.open(CCcamInfoMain)
		else:
			self.noYet()

	def noYet(self):
		nobox = self.session.open(MessageBox, 'Funcion Todavia no disponible', MessageBox.TYPE_INFO)
		nobox.setTitle(_('Info'))

	def updateList(self):
		self.list = []
		mypath = '/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/'
		mypixmap = mypath + 'crond.png'
		png = LoadPixmap(mypixmap)
		if config.osd.language.value == 'es_ES':
			name = _('Administrador Cron')
		else:
			name = _('CronManager')
		idx = 12
		res = (name, png, idx)
		self.list.append(res)
		mypixmap = mypath + 'Harddisk.png'
		png = LoadPixmap(mypixmap)
		if config.osd.language.value == 'es_ES':
			name = _('Admin de montajes')
		else:
			name = _('Mount Manager')
		idx = 0
		res = (name, png, idx)
		self.list.append(res)
		mypixmap = mypath + 'Usb.png'
		png = LoadPixmap(mypixmap)
		if config.osd.language.value == 'es_ES':
			name = _('Formatear USB')
		else:
			name = _('Usb Format Wizard')
		idx = 1
		res = (name, png, idx)
		self.list.append(res)
		mypixmap = mypath + 'SwapManager.png'
		png = LoadPixmap(mypixmap)
		if config.osd.language.value == 'es_ES':
			name = _('Memoria Swap')
		else:
			name = _('Swap File settings')
		idx = 2
		res = (name, png, idx)
		self.list.append(res)
		mypixmap = mypath + 'Epg_setup.png'
		png = LoadPixmap(mypixmap)
		if config.osd.language.value == 'es_ES':
			name = _('Ajustes de EPG')
		else:
			name = _('Epg settings')
		idx = 6
		res = (name, png, idx)
		self.list.append(res)
		mypixmap = mypath + 'AV_Setup.png'
		png = LoadPixmap(mypixmap)
		if config.osd.language.value == 'es_ES':
			name = _('Opciones Osd')
		else:
			name = _('Osd settings')
		idx = 3
		res = (name, png, idx)
		self.list.append(res)
		mypixmap = mypath + 'Ajustes_grabar.png'
		png = LoadPixmap(mypixmap)
		if config.osd.language.value == 'es_ES':
			name = _('Ajustes de grabacion')
		else:
			name = _('Record settings')
		idx = 7
		res = (name, png, idx)
		self.list.append(res)
		mypixmap = mypath + 'Tuner_Setup.png'
		png = LoadPixmap(mypixmap)
		name = _('Satfinder')
		idx = 8
		res = (name, png, idx)
		self.list.append(res)
		mypixmap = mypath + 'Conf_idiomas.png'
		png = LoadPixmap(mypixmap)
		if config.osd.language.value == 'es_ES':
			name = _('Auto configuracion idioma')
		else:
			name = _('Auto language settings')
		idx = 9
		res = (name, png, idx)
		self.list.append(res)
		mypixmap = mypath + 'Ajustes_http.png'
		png = LoadPixmap(mypixmap)
		if config.osd.language.value == 'es_ES':
			name = _('Ajustes Http stream')
		else:
			name = _('Http stream settings')
		idx = 10
		res = (name, png, idx)
		self.list.append(res)
		mypixmap = mypath + 'Module.png'
		png = LoadPixmap(mypixmap)
		if config.osd.language.value == 'es_ES':
			name = _('Liberar RAM')
		else:
			name = _('Liberate RAM')
		idx = 11
		res = (name, png, idx)
		self.list.append(res)
		mypixmap = mypath + 'Network.png'
		png = LoadPixmap(mypixmap)
		if config.osd.language.value == 'es_ES':
			name = _('Reiniciar RED')
		else:
			name = _('Reset Network')
		idx = 13
		res = (name, png, idx)
		self.list.append(res)
		mypixmap = mypath + 'Module.png'
		png = LoadPixmap(mypixmap)
		name = 'CCcamInfo'
		idx = 14
		res = (name, png, idx)
		self.list.append(res)
		mypixmap = mypath + 'Module.png'
		png = LoadPixmap(mypixmap)
		name = 'NcamInfo'
		idx = 4
		res = (name, png, idx)
		self.list.append(res)
		mypixmap = mypath + 'Module.png'
		png = LoadPixmap(mypixmap)
		name = 'OScamInfo'
		idx = 5
		res = (name, png, idx)
		self.list.append(res)
		self['list'].list = self.list


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
		self['progress'].setRange(int(config.plugins.LDteam.epgmhw2wait.value - 5))
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
		if count > config.plugins.LDteam.epgmhw2wait.value:
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

class LDepg(Screen, ConfigListScreen):
	skin = """
	<screen name="LDepg" position="center,center" size="1150,650">
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
		 'ColorActions'], {'blue': self.mhw,
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
			self.list.append(getConfigListEntry(_('Tiempo Duracion en Portada'), config.plugins.LDteam.epgmhw2wait))
		else:
			self.list.append(getConfigListEntry(_('Time at title page'), config.plugins.LDteam.epgmhw2wait))
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
		config.plugins.LDteam.epgmhw2wait.save()
		config.epg.save()
		config.epg.maxdays.save()
		configfile.save()
		self.mbox = self.session.open(MessageBox, _('configuration is saved'), MessageBox.TYPE_INFO, timeout=4)
		return

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


class LDmemoria(ConfigListScreen, Screen):
	skin = """
<screen name="LDmemoria" position="center,160" size="750,370" title="Liberar Memoria">
	<eLabel position="30,220" size="690,2" backgroundColor="#aaaaaa" />
	<widget position="15,10" size="720,200" name="config" scrollbarMode="showOnDemand" />
	<ePixmap position="10,358" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" alphatest="blend" />
	<widget source="key_red" render="Label" position="10,328" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<ePixmap position="175,358" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green150x30.png" alphatest="blend" />
	<widget source="key_green" render="Label" position="175,328" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<ePixmap position="340,358" zPosition="1" size="195,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/yellow150x30.png" alphatest="blend" />
	<widget source="key_yellow" render="Label" position="340,328" zPosition="2" size="195,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="MemoryLabel" render="Label" position="55,235" size="150,22" font="Regular; 20" halign="right" foregroundColor="#aaaaaa" />
	<widget source="memTotal" render="Label" position="220,235" zPosition="2" size="450,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="bufCache" render="Label" position="220,260" zPosition="2" size="450,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.list = []
		self.iConsole = iConsole()
		self['key_red'] = StaticText(_('Close'))
		self['key_green'] = StaticText(_('Save'))
		self['key_yellow'] = StaticText(_('Liberar'))
		self['memTotal'] = StaticText()
		self['bufCache'] = StaticText()
		self['MemoryLabel'] = StaticText(_('Memory:'))
		self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'EPGSelectActions'], {'red': self.cancel,
		 'cancel': self.cancel,
		 'green': self.save_values,
		 'yellow': self.ClearNow,
		 'ok': self.save_values}, -2)
		self.list.append(getConfigListEntry(_('Select free memory mode'), config.plugins.LDteam.dropmode))
		ConfigListScreen.__init__(self, self.list)
		self.onShow.append(self.Title)

	def Title(self):
		self.setTitle(_('Free memory'))
		self.infomem()

	def cancel(self):
		for i in self['config'].list:
			i[1].cancel()

		self.close()

	def infomem(self):
		memtotal = memfree = buffers = cached = ''
		persent = 0
		if fileExists('/proc/meminfo'):
			for line in open('/proc/meminfo'):
				if 'MemTotal:' in line:
					memtotal = line.split()[1]
				elif 'MemFree:' in line:
					memfree = line.split()[1]
				elif 'Buffers:' in line:
					buffers = line.split()[1]
				elif 'Cached:' in line:
					cached = line.split()[1]

			if '' is not memtotal and '' is not memfree:
				persent = int(memfree) / (int(memtotal) / 100)
			self['memTotal'].text = _('Total: %s Kb  Free: %s Kb (%s %%)') % (memtotal, memfree, persent)
			self['bufCache'].text = _('Buffers: %s Kb  Cached: %s Kb') % (buffers, cached)

	def save_values(self):
		for i in self['config'].list:
			i[1].save()

		configfile.save()
		self.mbox = self.session.open(MessageBox, _('configuration is saved'), MessageBox.TYPE_INFO, timeout=4)

	def ClearNow(self):
		self.iConsole.ePopen('sync ; echo %s > /proc/sys/vm/drop_caches' % config.plugins.LDteam.dropmode.value, self.Finish)

	def Finish(self, result, retval, extra_args):
		if retval is 0:
			self.mbox = self.session.open(MessageBox, _('Cache flushed'), MessageBox.TYPE_INFO, timeout=4)
		else:
			self.mbox = self.session.open(MessageBox, _('error...'), MessageBox.TYPE_INFO, timeout=4)
		self.infomem()


class LdNetBrowser(Screen):
	skin = """
	<screen position="center,center" size="800,520" title="OpenLD - Seleccione la interfaz de red">
		<widget source="list" render="Listbox" position="10,10" size="780,460" scrollbarMode="showOnDemand" >
			<convert type="StringList" />
		</widget>
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" position="200,480" size="150,30" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/yellow150x30.png" position="440,480" size="150,30" alphatest="on" />
		<widget name="key_red" position="200,482" zPosition="1" size="150,25" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_yellow" position="440,482" zPosition="1" size="150,25" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self['key_red'] = Label(_('Select'))
		self['key_yellow'] = Label(_('Close'))
		self.list = []
		self['list'] = List(self.list)
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.selectInte,
		 'back': self.close,
		 'red': self.selectInte,
		 'yellow': self.close})
		self.list = []
		self.adapters = [ (iNetwork.getFriendlyAdapterName(x), x) for x in iNetwork.getAdapterList() ]
		for x in self.adapters:
			res = (x[0], x[1])
			self.list.append(res)

		self['list'].list = self.list

	def selectInte(self):
		mysel = self['list'].getCurrent()
		if mysel:
			inter = mysel[1]
			self.session.open(NetworkBrowser, inter, '/usr/lib/enigma2/python/Plugins/SystemPlugins/NetworkBrowser')
