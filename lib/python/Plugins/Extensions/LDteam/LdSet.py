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
from Components.ConfigList import ConfigList, ConfigListScreen
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

config.plugins.LDteam = ConfigSubsection()
config.plugins.LDteam.dropmode = ConfigSelection(default='3', choices=[('1', _('free pagecache')), ('2', _('free dentries and inodes')), ('3', _('free pagecache, dentries and inodes'))])

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
			from Plugins.Extensions.LDteam.LdEparted import Ceparted
			self.session.open(Ceparted)
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
			self.session.open(LdEpgPanel)
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
		mypixmap = mypath + 'Harddisk.png'
		png = LoadPixmap(mypixmap)
		name = _('eParted')

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
		if os.path.exists("/etc/CCcam.cfg"):
			res = (name, png, idx)
			self.list.append(res)
			mypixmap = mypath + 'Module.png'
			png = LoadPixmap(mypixmap)
			name = 'CCcamInfo'
			idx = 14
		if os.path.exists("/var/tuxbox/config/ncam.conf"):
			res = (name, png, idx)
			self.list.append(res)
			mypixmap = mypath + 'Module.png'
			png = LoadPixmap(mypixmap)
			name = 'NcamInfo'
			idx = 4
		if os.path.exists("/var/tuxbox/config/oscam.conf"):
			res = (name, png, idx)
			self.list.append(res)
			mypixmap = mypath + 'Module.png'
			png = LoadPixmap(mypixmap)
			name = 'OScamInfo'
			idx = 5
		res = (name, png, idx)
		self.list.append(res)
		self['list'].list = self.list

class LdEpgPanel(Screen):
	skin = """
	<screen position="center,center" size="600,400" title="OpenLD EPG Panel">
		<widget source="list" render="Listbox" position="20,20" size="560,360" font="Regular;28" itemHeight="40"  scrollbarMode="showOnDemand" >
			<convert type="StringList" />
		</widget>
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)

		flist = [("EPGSettings"),
		("EPGSearch"),
		("EPGRefresh"),
		("Movistar+ (MHW2)"),
		("CrossEPG"),
		("EPGImport")]
		self["list"] = List(flist)

		self['key_red'] = StaticText(_('Close'))
		self["setupActions"] = ActionMap(["SetupActions", "WizardActions", "TimerEditActions", "ColorActions"],
		{
			"ok": self.KeyOk,
			"red": self.cancel,
			"back": self.close

		})

	def KeyOk(self):
		sel = self["list"].getCurrent()
		if sel:
			if sel == "EPGSettings":
				from Screens.Setup import Setup
				self.session.open(Setup, "epgsettings")
			elif sel == "EPGSearch":
				from Plugins.Extensions.EPGSearch.EPGSearch import EPGSearch as epgsearch
				self.session.open(epgsearch)
			elif sel == "EPGRefresh":
				if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/EPGRefresh/plugin.pyo"):
					from Plugins.Extensions.EPGRefresh.EPGRefreshConfiguration import EPGRefreshConfiguration
					self.session.open(EPGRefreshConfiguration)
				else:
					self.session.open(MessageBox, _("Sorry! EPGRefresh - It not installed"), MessageBox.TYPE_INFO, timeout = 5)
			elif sel == "Movistar+ (MHW2)":
				from Plugins.Extensions.LDteam.LdEpg import LDepgScreen
				self.session.open(LDepgScreen)
			elif sel == "CrossEPG":
				if os.path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/CrossEPG/plugin.pyo"):
					from Plugins.SystemPlugins.CrossEPG.crossepg_main import crossepg_main
					crossepg_main.setup(self.session)
				else:
					self.session.open(MessageBox, _("Sorry! CrossEPG - It not installed"), MessageBox.TYPE_INFO, timeout = 5)
			elif sel == "EPGImport":
				if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/EPGImport/plugin.pyo"):
					from Plugins.Extensions.EPGImport.plugin import EPGImportConfig
					self.session.open(EPGImportConfig)
				else:
					self.session.open(MessageBox, _("Sorry! EPGImport - It not installed"), MessageBox.TYPE_INFO, timeout = 5)

	def cancel(self):
		for i in self['config'].list:
			i[1].cancel()

		self.close(False)

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
		self['setupActions'] = ActionMap(['SetupActions', 'OkCancelActions', 'ColorActions', 'DirectionActions'], {'red': self.cancel,
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
