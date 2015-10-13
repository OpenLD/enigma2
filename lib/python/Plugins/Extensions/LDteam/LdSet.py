# -*- coding: ISO-8859-1 -*-

from enigma import eTimer
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen
from Components.Harddisk import harddiskmanager
from Components.config import getConfigListEntry, config, ConfigYesNo, ConfigText, ConfigSelection, ConfigNumber, ConfigSubsection, ConfigPassword, ConfigSubsection, ConfigClock, ConfigDateTime, ConfigInteger, configfile, NoSave
from Components.Sources.List import List
from Components.Sources.Progress import Progress
from Components.Console import Console
from Components.Network import iNetwork
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.Language import language
from ServiceReference import ServiceReference
from enigma import eEPGCache
from enigma import eDVBDB
from Components.ScrollLabel import ScrollLabel
from Components.Console import Console as iConsole
from time import *
from types import *
from enigma import *
import sys, traceback, re, new, os, gettext, commands, time, datetime, _enigma, enigma, Screens.Standby, subprocess, threading
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
from os import system, listdir, path, remove as os_remove, rename as os_rename, popen, getcwd, chdir
from Plugins.SystemPlugins.NetworkBrowser.NetworkBrowser import NetworkBrowser

count = 0

hddchoises = [('/media/hdd/', '/media/hdd/'), ('/media/usb/', '/media/usb/'), ('/usr/share/enigma2/', '/usr/share/enigma2/'), ('/etc/enigma2/', '/etc/enigma2/')]
config.misc.epgcachepath = ConfigSelection(default = '/etc/enigma2/', choices = hddchoises)

config.plugins.LDteam = ConfigSubsection()
config.plugins.LDteam.auto2 = ConfigSelection(default = "no", choices = [
                ("no", _("no")),
		("yes", _("yes")),
		])
config.plugins.LDteam.dropmode = ConfigSelection(default = '1', choices = [
		('1', _("free pagecache")),
		('2', _("free dentries and inodes")),
		('3', _("free pagecache, dentries and inodes")),
		])
config.plugins.LDteam.epgtime2 = ConfigClock(default = ((16*60) + 15) * 60)
config.plugins.LDteam.epgmhw2wait = ConfigNumber(default = 300 ) # 300 seconds = 5 minutes

def mountp():
	pathmp = []
	if fileExists("/proc/mounts"):
		for line in open("/proc/mounts"):
			if line.find("/dev/sd") > -1:
				pathmp.append(line.split()[1].replace('\\040', ' ') + "/")
	pathmp.append("/usr/share/enigma2/")
	return pathmp

def _(txt):
	t = gettext.dgettext("messages", txt)
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
		self["list"] = List(self.list)
		self.updateList()
		
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.KeyOk,
			"back": self.close

		})
		
	def KeyOk(self):
		self.sel = self["list"].getCurrent()
		self.sel = self.sel[2]
		
		if self.sel == 0:
			from Plugins.Extensions.LDteam.LdDeviceManager import DeviceManager
			self.session.open(DeviceManager)
		elif self.sel == 1:
			from Plugins.Extensions.LDteam.Ldsundtek import SundtekControlCenter
			self.session.open(SundtekControlCenter)
		elif self.sel == 2:
			from Plugins.Extensions.LDteam.LdFormat import LD_UsbFormat
			self.session.open(LD_UsbFormat)
		elif self.sel == 3:
			from Plugins.Extensions.LDteam.LdSwapManager import Swap
			self.session.open(Swap)
		elif self.sel == 4:
			self.session.open(LdSetupOSD3)
		elif self.sel == 5:
			from Screens.CCcamInfo import CCcamInfoMain
			self.session.open(CCcamInfoMain)
		elif self.sel == 6:
			from Screens.OScamInfo import OscamInfoMenu
			self.session.open(OscamInfoMenu)
		elif self.sel == 7:
			self.session.open(LDepg)
		elif self.sel == 8:
			self.session.open(LdSetupRecord)
		elif self.sel == 9:
			from Screens.Recordings import RecordingSettings
			self.session.open(RecordingSettings)
		elif self.sel == 10:
			self.session.open(LdSetupAutolanguage)
		elif self.sel == 11:
			self.session.open(LdSetupHttpStream)
		elif self.sel == 13:
			self.session.open(LDmemoria)
		elif self.sel == 14:
			from Screens.CronTimer import CronTimers
			self.session.open(CronTimers)
		elif self.sel == 15:
			from Plugins.Extensions.LDteam.LdRestartNetwork import RestartNetwork
			self.session.open(RestartNetwork)
		else:
			self.noYet()
			
	def noYet(self):
		nobox = self.session.open(MessageBox, "Funcion Todavia no disponible", MessageBox.TYPE_INFO)
		nobox.setTitle(_("Info"))
	
		
	def updateList(self):
		self.list = [ ]
		mypath = "/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/"

		mypixmap = mypath + "crond.png"
		png = LoadPixmap(mypixmap)
		name = "CronManager"
		idx = 14
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Harddisk.png"
		png = LoadPixmap(mypixmap)
		name = "Admin Dispositivos"
		idx = 0
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Usb.png"
		png = LoadPixmap(mypixmap)
		name = "Formatear USB"
		idx = 2
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "SwapManager.png"
		png = LoadPixmap(mypixmap)
		name = "Memoria Swap"
		idx = 3
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "SundtekControlCenter.png"
		png = LoadPixmap(mypixmap)
		name = "Soundtek Center"
		idx = 1
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Epg_setup.png"
		png = LoadPixmap(mypixmap)
		name = "Opciones EPG"
		idx = 7
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "AV_Setup.png"
		png = LoadPixmap(mypixmap)
		name = "Opciones Osd"
		idx = 4
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Ajustes_grabar.png"
		png = LoadPixmap(mypixmap)
		name = "Ajustes de grabacion"
		idx = 8
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "folder.png"
		png = LoadPixmap(mypixmap)
		name = "Ruta de grabacion"
		idx = 9
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Conf_idiomas.png"
		png = LoadPixmap(mypixmap)
		name = "Auto configuracion idioma"
		idx = 10
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Ajustes_http.png"
		png = LoadPixmap(mypixmap)
		name = "Ajustes Http stream"
		idx = 11
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Module.png"
		png = LoadPixmap(mypixmap)
		name = "Liberar memoria"
		idx = 13
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Network.png"
		png = LoadPixmap(mypixmap)
		name = "Reiniciar RED"
		idx = 15
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Module.png"
		png = LoadPixmap(mypixmap)
		name = "CCcamInfo"
		idx = 5
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Module.png"
		png = LoadPixmap(mypixmap)
		name = "OScamInfo"
		idx = 6
		res = (name, png, idx)
		self.list.append(res)

		self["list"].list = self.list

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
                self['srclabel'] = Label(_("Por favor Espere, Actualizando Epg"))
                self.setTitle(_("Update EPG"))
                self["progress"] = Progress(int(count))
                self['progress'].setRange(int(config.plugins.LDteam.epgmhw2wait.value-5))
                self.session = session
                self.ctimer = enigma.eTimer()
                count = 0
                self.ctimer.callback.append(self.__run)
                self.ctimer.start(1000,0)
  
        def __run(self):
                global count
                count += 1
                print ("%s Epg Downloaded") % count
                self['progress'].setValue(count)
                if count > config.plugins.LDteam.epgmhw2wait.value:
                        self.ctimer.stop()
                        self.session.nav.playService(eServiceReference(config.tv.lastservice.value))
                        rDialog.stopDialog(self.session)
                        self.mbox = self.session.open(MessageBox,(_("Epg Actualizado")), MessageBox.TYPE_INFO, timeout = 5 )
                        self.close()
pdialog = ""

class runDialog():
        def __init__(self):
                self.dialog = None

        def startDialog(self, session):
                global pdialog
                pdialog = session.instantiateDialog(Ttimer)
                pdialog.show()
 
        def stopDialog(self, session):
                global pdialog
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
		
		self.setTitle(_("EPG Options"))
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_blue"] = StaticText(_("ver log"))
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))
		self["key_yellow"] = StaticText(_("Update"))
		self["setupActions"] = ActionMap(["SetupActions", "WizardActions", "TimerEditActions", "ColorActions"],
		
		{
			"blue": self.mhw,
			"red": self.cancel,
			"cancel": self.cancel,
			"yellow": self.downepg,
			"green": self.save,
			"ok": self.save
		}, -2)

		self.list.append(getConfigListEntry(_("Enable EIT EPG"), config.epg.eit))
		self.list.append(getConfigListEntry(_("Enable MHW EPG"), config.epg.mhw))
		self.list.append(getConfigListEntry(_("Enable FreeSat EPG"), config.epg.freesat))
		self.list.append(getConfigListEntry(_("Enable ViaSat EPG"), config.epg.viasat))
		self.list.append(getConfigListEntry(_("Enable Netmed EPG"), config.epg.netmed))
		self.list.append(getConfigListEntry(_("Enable Virgin EPG"), config.epg.virgin))
		self.list.append(getConfigListEntry(_("Ruta donde almacenar el epg.dat"), config.misc.epgcachepath))
		self.list.append(getConfigListEntry(_("Maximum number of days in EPG"), config.epg.maxdays))
		self.list.append(getConfigListEntry(_("Maintain old EPG data for"), config.epg.histminutes))
		self.list.append(getConfigListEntry(_("Tiempo Duracion en Portada"), config.plugins.LDteam.epgmhw2wait))
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	
	def zapTo(self, reftozap):
	        self.session.nav.playService(eServiceReference(reftozap))

	def downepg(self):
	        global count
	        recordings = self.session.nav.getRecordings()
	        rec_time = self.session.nav.RecordTimer.getNextRecordingTime()
	        mytime = time.time()
	        try:
	                if not recordings  or (rec_time > 0 and rec_time - mytime() < 360):
	                        channel = "1:0:1:75C6:422:1:C00000:0:0:0:"
	                        self.zapTo(channel)
	                        ## Crea y muestra la barra de dialogo
	                        diag = runDialog()
	                        diag.startDialog(self.session)                        
                        else:
                                self.mbox = self.session.open(MessageBox,(_("EPG Download Cancelled - Recording active")), MessageBox.TYPE_INFO, timeout = 5 )
                except:
                        print ("Error download mhw2 epg, record active?")

	def mhw(self):
		self.session.open(Viewmhw)

	def cancel(self):
		for i in self["config"].list:
			i[1].cancel()
		self.close(False)
		
	def save(self):
		config.misc.epgcache_filename.value = ("%sepg.dat" % config.misc.epgcachepath.value)
		config.misc.epgcache_filename.save()
		config.misc.epgcachepath.save()
		config.plugins.LDteam.epgmhw2wait.save()
		configfile.save()
		self.mbox = self.session.open(MessageBox,(_("configuration is saved")), MessageBox.TYPE_INFO, timeout = 4 )
		
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
		self.setTitle(_("View mhw2equiv.conf (/tmp/mhw_Log.epg)"))
		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions"],
		{
			"cancel": self.exit,
			"back": self.exit,
			"red": self.exit,
			})
		self["key_red"] = StaticText(_("Close"))
		self["text"] = ScrollLabel("")
		self.viewmhw2()
		
	def exit(self):
		self.close()
		
	def viewmhw2(self):
		list = ''
		if fileExists("/tmp/mhw_Log.epg"):
			for line in open("/tmp/mhw_Log.epg"):
				list += line
		self["text"].setText(list)
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"],
			{
			"cancel": self.close,
			"up": self["text"].pageUp,
			"left": self["text"].pageUp,
			"down": self["text"].pageDown,
			"right": self["text"].pageDown,
			},
			-1)

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
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))
		self["key_yellow"] = StaticText(_("Liberar"))
		self["memTotal"] = StaticText()
		self["bufCache"] = StaticText()
		self["MemoryLabel"] = StaticText(_("Memory:"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "EPGSelectActions"],
		{
			"red": self.cancel,
			"cancel": self.cancel,
			"green": self.save_values,
			"yellow": self.ClearNow,
			"ok": self.save_values
		}, -2)
		self.list.append(getConfigListEntry(_("Elija modo liberar memoria"), config.plugins.LDteam.dropmode))
		ConfigListScreen.__init__(self, self.list)
		self.onShow.append(self.Title)
		
	def Title(self):
		self.setTitle(_("Liberar memoria"))
		self.infomem()

	def cancel(self):
		for i in self["config"].list:
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
			self["memTotal"].text = _("Total: %s Kb  Free: %s Kb (%s %%)") % (memtotal, memfree, persent)
			self["bufCache"].text = _("Buffers: %s Kb  Cached: %s Kb") % (buffers, cached)
	
	def save_values(self):
		for i in self["config"].list:
			i[1].save()
		configfile.save()
		self.mbox = self.session.open(MessageBox,(_("configuration is saved")), MessageBox.TYPE_INFO, timeout = 4 )

	def ClearNow(self):
		self.iConsole.ePopen("sync ; echo %s > /proc/sys/vm/drop_caches" % config.plugins.LDteam.dropmode.value, self.Finish)
		
	def Finish(self, result, retval, extra_args):
		if retval is 0:
			self.mbox = self.session.open(MessageBox,(_("Cache flushed")), MessageBox.TYPE_INFO, timeout = 4 )
		else:
			self.mbox = self.session.open(MessageBox,(_("error...")), MessageBox.TYPE_INFO, timeout = 4 )
		self.infomem()

class LdSetupOSD3(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="700,500" title="OpenLD - Opciones Osd">
		<widget name="config" position="10,10" size="680,430" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" position="140,450" size="150,30" alphatest="on" />
		<widget name="key_red" position="140,450" zPosition="1" size="150,25" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />
		<ePixmap position="420,450" size="150,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green150x30.png" alphatest="on" zPosition="1" />
		<widget name="key_green" position="420,450" zPosition="2" size="150,25" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.keyCancel,
			"back": self.keyCancel,
			"green": self.keySave,

		}, -2)
				
		self.list.append(getConfigListEntry(_("Infobar timeout"), config.usage.infobar_timeout))
		self.list.append(getConfigListEntry(_("Show second infobar"), config.usage.show_second_infobar))
		self.list.append(getConfigListEntry(_("Show event-progress in channel selection"), config.usage.show_event_progress_in_servicelist))
		self.list.append(getConfigListEntry(_("Show channel numbers in channel selection"), config.usage.show_channel_numbers_in_servicelist))
		self.list.append(getConfigListEntry(_("Show infobar on channel change"), config.usage.show_infobar_on_zap))
		self.list.append(getConfigListEntry(_("Show infobar on skip forward/backward"), config.usage.show_infobar_on_skip))
		self.list.append(getConfigListEntry(_("Show infobar on event change"), config.usage.show_infobar_on_event_change))
		self.list.append(getConfigListEntry(_("Hide zap errors"), config.usage.hide_zap_errors))
		self.list.append(getConfigListEntry(_("Hide CI messages"), config.usage.hide_ci_messages))
		self.list.append(getConfigListEntry(_("Show crypto info in infobar"), config.usage.show_cryptoinfo))
		self.list.append(getConfigListEntry(_("Swap SNR in db with SNR in percentage on OSD"), config.usage.swap_snr_on_osd))
		self.list.append(getConfigListEntry(_("Show EIT now/next in infobar"), config.usage.show_eit_nownext))
		
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keySave(self):
		for x in self["config"].list:
			x[1].save()
		self.close()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()

class LdSetupRecord(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="700,500" title="OpenLD - Ajustes de grabacion">
		<widget name="config" position="10,10" size="680,430" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" position="140,450" size="150,30" alphatest="on" />
		<widget name="key_red" position="140,450" zPosition="1" size="150,25" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />
		<ePixmap position="420,450" size="150,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green150x30.png" alphatest="on" zPosition="1" />
		<widget name="key_green" position="420,450" zPosition="2" size="150,25" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.keyCancel,
			"back": self.keyCancel,
			"green": self.keySave,

		}, -2)
		
		self.list.append(getConfigListEntry(_("Recordings always have priority"), config.recording.asktozap))
		self.list.append(getConfigListEntry(_("Margin before record (minutes)"), config.recording.margin_before))
		self.list.append(getConfigListEntry(_("Margin after record"), config.recording.margin_after))
		self.list.append(getConfigListEntry(_("Show Message when Recording starts"), config.usage.show_message_when_recording_starts))
		self.list.append(getConfigListEntry(_("Load Length of Movies in Movielist"), config.usage.load_length_of_movies_in_moviellist))
		self.list.append(getConfigListEntry(_("Show status icons in Movielist"), config.usage.show_icons_in_movielist))
		
		self.list.append(getConfigListEntry(_("Behavior when a movie is started"), config.usage.on_movie_start))
		self.list.append(getConfigListEntry(_("Behavior when a movie is stopped"), config.usage.on_movie_stop))
		self.list.append(getConfigListEntry(_("Behavior when a movie reaches the end"), config.usage.on_movie_eof))
		self.list.append(getConfigListEntry(_("Behavior of 'pause' when paused"), config.seek.on_pause))
		self.list.append(getConfigListEntry(_("Custom skip time for '1'/'3'-keys"), config.seek.selfdefined_13))
		self.list.append(getConfigListEntry(_("Custom skip time for '4'/'6'-keys"), config.seek.selfdefined_46))
		self.list.append(getConfigListEntry(_("Custom skip time for '7'/'9'-keys"), config.seek.selfdefined_79))
		self.list.append(getConfigListEntry(_("Fast Forward speeds"), config.seek.speeds_forward))
		self.list.append(getConfigListEntry(_("Rewind speeds"), config.seek.speeds_backward))
		self.list.append(getConfigListEntry(_("Slow Motion speeds"), config.seek.speeds_slowmotion))
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keySave(self):
		for x in self["config"].list:
			x[1].save()
		self.close()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()
	
class LdSetupAutolanguage(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="700,500" title="OpenLD - Auto configuracion idioma">
		<widget name="config" position="10,10" size="680,430" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" position="140,450" size="150,30" alphatest="on" />
		<widget name="key_red" position="140,452" zPosition="1" size="150,25" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />
		<ePixmap position="420,450" size="150,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green150x30.png" alphatest="on" zPosition="1" />
		<widget name="key_green" position="420,452" zPosition="2" size="150,25" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.keyCancel,
			"back": self.keyCancel,
			"green": self.keySave,

		}, -2)
						
		self.list.append(getConfigListEntry(_("Audio language selection 1"), config.autolanguage.audio_autoselect1))
		self.list.append(getConfigListEntry(_("Audio language selection 2"), config.autolanguage.audio_autoselect2))
		self.list.append(getConfigListEntry(_("Audio language selection 3"), config.autolanguage.audio_autoselect3))
		self.list.append(getConfigListEntry(_("Audio language selection 4"), config.autolanguage.audio_autoselect4))
		self.list.append(getConfigListEntry(_("Prefer AC3"), config.autolanguage.audio_defaultac3))
		self.list.append(getConfigListEntry(_("Prefer audio stream stored by service"), config.autolanguage.audio_usecache))
		self.list.append(getConfigListEntry(_("Subtitle language selection 1"), config.autolanguage.subtitle_autoselect1))
		self.list.append(getConfigListEntry(_("Subtitle language selection 2"), config.autolanguage.subtitle_autoselect2))
		self.list.append(getConfigListEntry(_("Subtitle language selection 3"), config.autolanguage.subtitle_autoselect3))
		self.list.append(getConfigListEntry(_("Subtitle language selection 4"), config.autolanguage.subtitle_autoselect4))
		self.list.append(getConfigListEntry(_("Allow Subtitle equals Audio mask"), config.autolanguage.equal_languages))
		self.list.append(getConfigListEntry(_("Allow hearing impaired subtitles"), config.autolanguage.subtitle_hearingimpaired))
		self.list.append(getConfigListEntry(_("Prefer hearing impaired subtitles"), config.autolanguage.subtitle_defaultimpaired))
		self.list.append(getConfigListEntry(_("Prefer DVB-grafical subtitles"), config.autolanguage.subtitle_defaultdvb))
		self.list.append(getConfigListEntry(_("Prefer subtitle stored by service"), config.autolanguage.subtitle_usecache))
		self.list.append(getConfigListEntry(_("EPG language selection 1"), config.autolanguage.audio_epglanguage))
		self.list.append(getConfigListEntry(_("EPG language selection 2"), config.autolanguage.audio_epglanguage_alternative))
		
		
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keySave(self):
		for x in self["config"].list:
			x[1].save()
		self.close()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()
		
class LdSetupHttpStream(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="700,500" title="OpenLD - Ajustes Http stream">
		<widget name="config" position="10,10" size="680,430" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/red150x30.png" position="140,450" size="150,30" alphatest="on" />
		<widget name="key_red" position="140,452" zPosition="1" size="150,25" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />
		<ePixmap position="420,450" size="150,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/buttons/green150x30.png" alphatest="on" zPosition="1" />
		<widget name="key_green" position="420,452" zPosition="2" size="150,25" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.keyCancel,
			"back": self.keyCancel,
			"green": self.keySave,

		}, -2)
						
		self.list.append(getConfigListEntry(_("Include EIT in http streams"), config.streaming.stream_eit))
		self.list.append(getConfigListEntry(_("Include AIT in http streams"), config.streaming.stream_ait))
		self.list.append(getConfigListEntry(_("Include ECM in http streams"), config.streaming.stream_ecm))
		self.list.append(getConfigListEntry(_("Descramble http streams"), config.streaming.descramble))
		
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keySave(self):
		for x in self["config"].list:
			x[1].save()
		self.close()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()
		

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
		
		self["key_red"] = Label(_("Select"))
		self["key_yellow"] = Label(_("Close"))
		
		self.list = []
		self["list"] = List(self.list)
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.selectInte,
			"back": self.close,
			"red": self.selectInte,
			"yellow": self.close
		})
		
		self.list = [ ]
		self.adapters = [(iNetwork.getFriendlyAdapterName(x),x) for x in iNetwork.getAdapterList()]
		for x in self.adapters:
			res = (x[0], x[1])
			self.list.append(res)

		self["list"].list = self.list
		
	def selectInte(self):
		mysel = self["list"].getCurrent()
		if mysel:
			inter = mysel[1]
			self.session.open(NetworkBrowser, inter, "/usr/lib/enigma2/python/Plugins/SystemPlugins/NetworkBrowser")
