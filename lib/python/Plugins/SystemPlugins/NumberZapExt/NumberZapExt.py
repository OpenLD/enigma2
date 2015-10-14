################################################################################
#    Extended NumberZap Plugin for Enigma2
#    Version: 1.0-rc12 (12.04.2014 22:00)
#    Copyright (C) 2011,2012 vlamo <vlamodev@gmail.com>
#    mod Dima73
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
################################################################################

from . import _, PLUGIN_PATH
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigSubDict, ConfigInteger
from Components.FileList import FileList
from Components.Label import Label
from Components.Pixmap import Pixmap
from Tools.Directories import pathExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename, getSize
from enigma import eServiceReference, eServiceCenter, eTimer, getDesktop
from plugin import CheckTimeshift, BEHAVIOR
FIRST_BEHAVIOR = True

service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'
service_types_radio = '1:7:2:0:0:0:0:0:0:0:(type == 2) || (type == 10)'

def getActions(xmlfile, hotkeys={}):
	result = { }
	try:
		import xml.etree.cElementTree
		root = xml.etree.cElementTree.parse(xmlfile).getroot()
	except:
		root = None
	if not root is None:
		for item in root.findall('action'):
			id = item.get('id')
			if id:
				result[id] = item.attrib.copy()
				result[id]['title'] = (result[id].get('title','') or id.replace('_',' ').title()).encode('UTF-8')
				result[id]['hotkey'] = int(result[id].get('hotkey', 0)) or hotkeys.get(id, 0)
				if result[id].get('type', '') in ('screen', 'code'):
					result[id]['args'] = item.text or ''
				result[id].pop('id')
	return result

ACTIONLIST = getActions('%s/actions.xml'%(PLUGIN_PATH), eval(config.plugins.NumberZapExt.hotkeys.value))

def getServiceFromNumber(self, number, acount=True, bouquet=None, startBouquet=None):
	def searchHelper(serviceHandler, num, bouquet):
		servicelist = serviceHandler.list(bouquet)
		if not servicelist is None:
			while num:
				s = servicelist.getNext()
				if not s.valid(): break
				try:
					playable = not (s.flags & (eServiceReference.isMarker|eServiceReference.isDirectory)) or (s.flags & eServiceReference.isNumberedMarker)
				except:
					playable = not (s.flags & (eServiceReference.isMarker|eServiceReference.isDirectory))
				if playable:
					num -= 1
			if not num: return s, num
		return None, num

	if self.servicelist is None: return None
	service = None
	serviceHandler = eServiceCenter.getInstance()
	if startBouquet and bouquet and startBouquet == bouquet:
		service, number = searchHelper(serviceHandler, number, bouquet)
	elif not config.usage.multibouquet.value:
		bouquet = self.servicelist.bouquet_root
		service, number = searchHelper(serviceHandler, number, bouquet)
	elif acount and self.servicelist.getMutableList() is not None:
		bouquet = self.servicelist.getRoot()
		service, number = searchHelper(serviceHandler, number, bouquet)
	elif acount and bouquet is not None:
		service, number = searchHelper(serviceHandler, number, bouquet)
	else:
		bouquet = self.servicelist.bouquet_root
		bouquetlist = serviceHandler.list(bouquet)
		if not bouquetlist is None:
			while number:
				bouquet = bouquetlist.getNext()
				if not bouquet.valid(): break
				if bouquet.flags & eServiceReference.isDirectory:
					service, number = searchHelper(serviceHandler, number, bouquet)
					if acount: break
	return service, bouquet

class DirectoryBrowser(Screen):
	skin = """<screen name="DirectoryBrowser" position="center,center" size="520,440" title=" " >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="curdir" render="Label" position="5,50" size="510,20"  font="Regular;20" halign="left" valign="center" backgroundColor="background" transparent="1" noWrap="1" />
			<widget name="filelist" position="5,80" size="510,345" scrollbarMode="showOnDemand" />
		</screen>"""
	
	def __init__(self, session, curdir, matchingPattern=None):
		Screen.__init__(self, session)

		self["Title"].setText(_("Directory browser"))
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["curdir"] = StaticText(_("current:  %s")%(curdir or ''))

		self.filelist = FileList(curdir, matchingPattern=matchingPattern, enableWrapAround=True)
		self.filelist.onSelectionChanged.append(self.__selChanged)
		self["filelist"] = self.filelist

		self["FilelistActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"green": self.keyGreen,
				"red": self.keyRed,
				"ok": self.keyOk,
				"cancel": self.keyRed
			})
		self.onLayoutFinish.append(self.__layoutFinished)

	def __layoutFinished(self):
		pass

	def getCurrentSelected(self):
		dirname = self.filelist.getCurrentDirectory()
		filename = self.filelist.getFilename()
		if not filename and not dirname:
			cur = ''
		elif not filename:
			cur = dirname
		elif not dirname:
			cur = filename
		else:
			if not self.filelist.canDescent() or len(filename) <= len(dirname):
				cur = dirname
			else:
				cur = filename
		return cur or ''

	def __selChanged(self):
		self["curdir"].setText(_("current:  %s")%(self.getCurrentSelected()))

	def keyOk(self):
		if self.filelist.canDescent():
			self.filelist.descent()

	def keyGreen(self):
		self.close(self.getCurrentSelected())

	def keyRed(self):
		self.close(False)

class NumberZapExt(Screen):
	if getDesktop(0).size().width() >= 1280:
		skin = """<screen name="NumberZapExt" position="center,center" size="600,160" title=" ">
				<widget name="chPicon" position="475,10"  size="100,60" alphatest="on" />
				<widget name="number"  position="5,35"    size="190,30" halign="right" font="Regular;26" />
				<widget name="chNum"   position="210,35"  size="240,30" halign="left"  font="Regular;26" />
				<widget name="channel" position="5,75"    size="190,30" halign="right" font="Regular;26" />
				<widget name="chName"  position="210,75"  size="375,30" halign="left"  font="Regular;24" noWrap="1" />
				<widget name="bouquet" position="5,115"   size="190,30" halign="right" font="Regular;26" />
				<widget name="chBouq"  position="210,115" size="375,30" halign="left"  font="Regular;24" noWrap="1" />
			</screen>"""
	else:
		skin = """<screen name="NumberZapExt" position="center,center" size="350,145" title=" ">
				<widget name="chPicon" position="273,7"   size="70,53"  alphatest="on" />
				<widget name="number"  position="5,35"    size="110,25" halign="right" font="Regular;23" />
				<widget name="chNum"   position="130,35"  size="130,25" halign="left"  font="Regular;23" />
				<widget name="channel" position="5,70"    size="110,25" halign="right" font="Regular;23" />
				<widget name="chName"  position="130,70"  size="215,25" halign="left"  font="Regular;21" noWrap="1" />
				<widget name="bouquet" position="5,105"   size="110,25" halign="right" font="Regular;23" />
				<widget name="chBouq"  position="130,105" size="215,25" halign="left"  font="Regular;21" noWrap="1" />
			</screen>"""

	def __init__(self, session, number, servicelist=None):
		Screen.__init__(self, session)
		self.digits = 4
		self.field = str(number)
		self.servicelist = servicelist
		self.acount = config.plugins.NumberZapExt.acount.value
		self.startBouquet = None
		self.bouquets = None
		if self.servicelist is not None:
			self.bouquets = self.servicelist.getBouquetList()
		else:
			self.bouquets = None
		self.BouquetsPriority = False
		if config.plugins.NumberZapExt.bouquets_enable.value:
			if config.usage.multibouquet.value:
				self.bouquet_root_tv = eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet')
				self.bouquet_root_radio = eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.radio" ORDER BY bouquet')
			else:
				self.bouquet_root_tv = eServiceReference('%s FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet'%(service_types_tv))
				self.bouquet_root_radio = eServiceReference('%s FROM BOUQUET "userbouquet.favourites.radio" ORDER BY bouquet'%(service_types_radio))
			self.Bouquetlist = self.getBouquetlist(self.bouquet_root_tv) + self.getBouquetlist(self.bouquet_root_radio)
			self.hotkeys_bouquets = eval(config.plugins.NumberZapExt.hotkeys_bouquets.value)
		self.kdelay = config.plugins.NumberZapExt.kdelay.value
		self.bouqSelDlg = None
		self.bouquet = None
		self.action = ''
		self.bouquet_action = None
		self.defpicon = None
		if config.plugins.NumberZapExt.picons.value:
			for scope, path in [(SCOPE_CURRENT_SKIN, "picon_default.png"), (SCOPE_SKIN_IMAGE, "skin_default/picon_default.png")]:
				tmp = resolveFilename(scope, path)
				if pathExists(tmp) and getSize(tmp):
					self.defpicon = tmp
					break

		self["Title"].setText(_("Service"))
		self["number"]  = Label(_("Number:"))
		self["channel"] = Label(_("Channel:"))
		self["bouquet"] = Label(_("Bouquet:"))
		self["chNum"]   = Label()
		self["chName"]  = Label()
		self["chBouq"]  = Label()
		self["chPicon"] = Pixmap()
		self["actions"] = NumberActionMap([ "ShortcutActions", "SetupActions", "MenuActions"],
			{
				"red": self.keyRed,
				"cancel": self.quit,
				"ok": self.keyOK,
				"green": self.keyGreen,
				"yellow": self.keyYellow,
				"blue": self.keyBlue,
				"menu": self.keyMenu,
				"1": self.keyNumberGlobal,
				"2": self.keyNumberGlobal,
				"3": self.keyNumberGlobal,
				"4": self.keyNumberGlobal,
				"5": self.keyNumberGlobal,
				"6": self.keyNumberGlobal,
				"7": self.keyNumberGlobal,
				"8": self.keyNumberGlobal,
				"9": self.keyNumberGlobal,
				"0": self.keyNumberGlobal
			})
		self.Timer = eTimer()
		self.Timer.callback.append(self.keyOK)
		self.onFirstExecBegin.append(self.__onStart)

	def __onStart(self):
		if self.servicelist is None: self.quit()
		if config.plugins.NumberZapExt.acount.value and self.servicelist.getMutableList() is None:
			if not self.bouquets: self.quit()
			if len(self.bouquets) == 1:
				self.bouquetSelected(self.bouquets[0][1])
			else:
				from Screens.ChannelSelection import BouquetSelector
				self.bouqSelDlg = self.session.openWithCallback(self.bouquetSelectorClosed, BouquetSelector, self.bouquets, self.bouquetSelected, enableWrapAround=True)
		else:
			self.printLabels()
			self.startTimer()

	def getBouquetlist(self, root):
		bouquets = [ ]
		serviceHandler = eServiceCenter.getInstance()
		if config.usage.multibouquet.value:
			bouquetlist = serviceHandler.list(root)
			if bouquetlist:
				while True:
					s = bouquetlist.getNext()
					if not s.valid(): break
					if s.flags & eServiceReference.isDirectory:
						info = serviceHandler.info(s)
						if info: bouquets.append((info.getName(s), s))
		else:
			info = serviceHandler.info(root)
			if info:
				bouquets.append((info.getName(root), root))
		return bouquets

	def keyMenu(self):
		if config.plugins.NumberZapExt.bouquets_enable.value and not config.plugins.NumberZapExt.bouquets_priority.value:
			self.BouquetsPriority = True
			self.printLabels()
			self.startTimer()

	def keyRed(self):
		if self.acount and self.startBouquet is None and self.bouquets is not None and len(self.bouquets) > 3:
			self.startBouquet = self.bouquets[3][1]
			self.bouquetSelected(self.bouquets[3][1])

	def keyGreen(self):
		if self.acount and self.startBouquet is None and self.bouquets is not None and len(self.bouquets) > 2:
			self.startBouquet = self.bouquets[2][1]
			self.bouquetSelected(self.bouquets[2][1])

	def keyYellow(self):
		if self.acount and self.startBouquet is None and self.bouquets is not None and len(self.bouquets) > 1:
			self.startBouquet = self.bouquets[1][1]
			self.bouquetSelected(self.bouquets[1][1])

	def keyBlue(self):
		if self.acount and self.startBouquet is None and self.bouquets is not None and len(self.bouquets) > 1:
			self.startBouquet = self.bouquets[0][1]
			self.bouquetSelected(self.bouquets[0][1])

	def bouquetSelectorClosed(self, retval):
		if retval is False:
			self.quit()
		else:
			self.bouqSelDlg = None

	def bouquetSelected(self, bouquet):
		if self.bouqSelDlg:
			self.bouqSelDlg.close(True)
		self.bouquet = bouquet
		if self.startBouquet is None:
			self.startBouquet = self.bouquet
		self.printLabels()
		self.startTimer()

	def startTimer(self):
		self.Timer.stop()
		if self.kdelay:
			self.Timer.start(self.kdelay, True)

	def printLabels(self):
		self.bouquet_action = None
		bouquet_name = None
		self.action = ''
		hotkeys_priority = config.plugins.NumberZapExt.hotkeys_priority.value
		bouquets_priority = config.plugins.NumberZapExt.bouquets_priority.value or self.BouquetsPriority
		if hotkeys_priority or bouquets_priority:
			if bouquets_priority:
				bouquet_name, self.bouquet_action = self.getHotkeyBouquets(int(self.field))
			if self.bouquet_action is not None:
				name = _("%s" % (bouquet_name or ''))
				channel = _("Bouquet:")
				bouquet = bqname = ""
				service = None
			elif hotkeys_priority:
				self.action = self.getHotkeyAction(int(self.field))
				if self.action:
					name = _(ACTIONLIST[self.action]['title'])
					channel = _("Action:")
					bouquet = bqname = ""
					service = None
				else:
					channel = _("Channel:")
					bouquet = _("Bouquet:")
					service, name, bqname = self.getNameFromNumber(int(self.field))
					if name == 'N/A': name = _("invalid channel number")
			else:
				channel = _("Channel:")
				bouquet = _("Bouquet:")
				service, name, bqname = self.getNameFromNumber(int(self.field))
				if name == 'N/A':
					if not service is None:
						name = _("service not found")
					else:
						name = _("invalid channel number")
						self.action = self.getHotkeyAction(int(self.field))
						if self.action:
							name = _(ACTIONLIST[self.action]['title'])
							channel = _("Action:")
							bouquet = bqname = ""
							service = None
		else:
			channel = _("Channel:")
			bouquet = _("Bouquet:")
			service, name, bqname = self.getNameFromNumber(int(self.field))
			if name == 'N/A':
				if not service is None:
					name = _("service not found")
				else:
					name = _("invalid channel number")
					bouquet_name, self.bouquet_action = self.getHotkeyBouquets(int(self.field))
					if self.bouquet_action is not None:
						name = _("%s" % (bouquet_name or ''))
						channel = _("Bouquet:")
						bouquet = bqname = ""
						service = None
					else:
						self.action = self.getHotkeyAction(int(self.field))
						if self.action:
							name = _(ACTIONLIST[self.action]['title'])
							channel = _("Action:")
							bouquet = bqname = ""
							service = None
		self["chNum"].setText(self.field)
		self["channel"].setText(channel)
		self["bouquet"].setText(bouquet)
		self["chName"].setText(name)
		self["chBouq"].setText(bqname)
		if config.plugins.NumberZapExt.picons.value:
			pngname = self.defpicon
			if service:
				sname = ':'.join(service.toString().split(':')[:11])
				pos = sname.rfind(':')
				if pos != -1:
					sname = sname[:pos].rstrip(':').replace(':','_')
					sname = config.plugins.NumberZapExt.picondir.value + sname + '.png'
					if pathExists(sname):
						pngname = sname
				self["chPicon"].instance.setScale(1)
				self["chPicon"].instance.setPixmapFromFile(pngname)
			else:
				self["chPicon"].instance.setPixmap(None)

	def quit(self):
		self.Timer.stop()
		self.close(0, None, None)

	def keyOK(self):
		self.Timer.stop()
		self.close(int(self["chNum"].getText()), self.bouquet_action or self.action or self.bouquet, self.startBouquet)

	def keyNumberGlobal(self, number):
		self.startBouquet = None
		self.BouquetsPriority = False
		self.bouquet = None
		self.startTimer()
		l = len(self.field)
		if l < self.digits:
			l += 1
			self.field += str(number)
			self.printLabels()
		elif self.kdelay:
			self.keyOK()

	def getNameFromNumber(self, number):
		name = 'N/A'
		bqname = 'N/A'
		service, bouquet = getServiceFromNumber(self, number, acount=self.acount, bouquet=self.bouquet, startBouquet=self.startBouquet)
		if not service is None:
			serviceHandler = eServiceCenter.getInstance()
			info = serviceHandler.info(service)
			name = info and info.getName(service) or 'N/A'
			if bouquet and bouquet.valid():
				info = serviceHandler.info(bouquet)
				bqname = info and info.getName(bouquet)
		return service, name, bqname

	def getHotkeyAction(self, number):
		if config.plugins.NumberZapExt.hotkey.value:
			for (key,val) in ACTIONLIST.items():
				if val.get('hotkey',-1) == number:
					return key
		return ''

	def getHotkeyBouquets(self, number):
		if config.plugins.NumberZapExt.bouquets_enable.value:
			for i in range(len(self.Bouquetlist)):
				if i in range(len(self.hotkeys_bouquets)):
					key = self.hotkeys_bouquets[i]
					if key == number:
						num = i - 1
						try:
							bouquet_ref = self.Bouquetlist[num][1] and self.Bouquetlist[num][1].toString()
						except:
							bouquet_ref = None
						if self.servicelist is not None and bouquet_ref is not None:
							if ('.%s"' % config.servicelist.lastmode.value) in str(bouquet_ref):
								return self.Bouquetlist[num][0], self.Bouquetlist[num][1]
		return None, None

class NumberZapExtSetupScreen(Screen, ConfigListScreen):
	def __init__(self, session, actionlist):
		Screen.__init__(self, session)
		self.skinName = ["NumberZapExtSetup", "Setup"]
		self.setup_title = _("Extended NumberZap Setup")
		self.actionlist = actionlist

		self["key_green"] = StaticText(_("Save"))
		self["key_red"] = StaticText(_("Cancel"))
		self["actions"] = NumberActionMap(["SetupActions"],
		{
			"cancel": self.keyRed,	# KEY_RED, KEY_EXIT
			"ok": self.keyOk,	# KEY_OK
			"save": self.keyGreen,	# KEY_GREEN
		}, -1)

		ConfigListScreen.__init__(self, [])
		if config.usage.multibouquet.value:
			self.bouquet_root_tv = eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet')
			self.bouquet_root_radio = eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.radio" ORDER BY bouquet')
		else:
			self.bouquet_root_tv = eServiceReference('%s FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet'%(service_types_tv))
			self.bouquet_root_radio = eServiceReference('%s FROM BOUQUET "userbouquet.favourites.radio" ORDER BY bouquet'%(service_types_radio))
		self.Bouquetlist = self.getBouquetList(self.bouquet_root_tv) + self.getBouquetList(self.bouquet_root_radio)
		self.prev_hotkeys_bouquets = eval(config.plugins.NumberZapExt.hotkeys_bouquets.value)
		self.initConfig()
		self.createSetup()
		self.onClose.append(self.__closed)
		self.onLayoutFinish.append(self.__layoutFinished)

	def __closed(self):
		pass

	def __layoutFinished(self):
		self.setTitle(self.setup_title)

	def getBouquetList(self, root):
		bouquets = [ ]
		serviceHandler = eServiceCenter.getInstance()
		if config.usage.multibouquet.value:
			bouquetlist = serviceHandler.list(root)
			if bouquetlist:
				while True:
					s = bouquetlist.getNext()
					if not s.valid(): break
					if s.flags & eServiceReference.isDirectory:
						info = serviceHandler.info(s)
						if info: bouquets.append((info.getName(s), s))
		else:
			info = serviceHandler.info(root)
			if info:
				bouquets.append((info.getName(root), root))
		return bouquets

	def initConfig(self):
		def getPrevValues(section):
			res = { }
			for (key,val) in section.content.items.items():
				if isinstance(val, ConfigSubsection):
					res[key] = getPrevValues(val)
				else:
					res[key] = val.value
			return res
		
		self.NZE = config.plugins.NumberZapExt
		self.prev_values = getPrevValues(self.NZE)
		self.cfg_enable = getConfigListEntry(_("Enable extended number zap"), self.NZE.enable)
		self.cfg_kdelay = getConfigListEntry(_("Time to wait next keypress (milliseconds)"), self.NZE.kdelay)
		self.cfg_acount = getConfigListEntry(_("Alternative service counter in bouquets"), self.NZE.acount)
		self.cfg_acounthelp = getConfigListEntry(_("<< Press colors keys (the first four bouquets) >>"), self.NZE.acount_help)
		self.cfg_timeshift_behavior = getConfigListEntry(_("Behavior when timeshift is enabled"), self.NZE.timeshift_behavior)
		self.cfg_key0 = getConfigListEntry(_("Check timeshift of 0 key in recall service"), self.NZE.key0)
		self.cfg_picons = getConfigListEntry(_("Enable picons"), self.NZE.picons)
		self.cfg_picondir = getConfigListEntry(_("Picons directory (press OK)"), self.NZE.picondir)
		self.cfg_hotkey = getConfigListEntry(_("Enable number hotkeys"), self.NZE.hotkey)
		self.cfg_hotkey_bouquets = getConfigListEntry(_("Enable bouquets hotkeys"), self.NZE.bouquets_enable)
		self.cfg_bouquets_priority = getConfigListEntry(_("Hotkey bouquets have priority"), self.NZE.bouquets_priority)
		self.cfg_bouquets_help = getConfigListEntry(_("<< Press menu key (for priority bouquets) >>"), self.NZE.bouquets_help)
		self.action = ConfigSubDict()
		for key,val in self.actionlist.items():
			self.action[key] = ConfigInteger(default=val['hotkey'], limits=(0,9999))
		self.BouquetsKey = ConfigSubDict()
		for i in range(len(self.Bouquetlist)):
			val = 0
			if i in range(len(self.prev_hotkeys_bouquets)):
				val = self.prev_hotkeys_bouquets[i]
			self.BouquetsKey[i] = ConfigInteger(default=val, limits=(0,9999))

	def createSetup(self):
		list = [ self.cfg_enable ]
		if self.NZE.enable.value:
			list.append(self.cfg_kdelay)
			list.append(self.cfg_acount)
			if self.NZE.acount.value:
				list.append(self.cfg_acounthelp)
			list.append(self.cfg_timeshift_behavior)
			if CheckTimeshift is not None:
				list.append(self.cfg_key0)
			list.append(self.cfg_picons)
			if self.NZE.picons.value:
				list.append(self.cfg_picondir)
			list.append(self.cfg_hotkey_bouquets)
			if self.NZE.bouquets_enable.value:
				list.append(self.cfg_bouquets_priority)
				if not self.NZE.bouquets_priority.value:
					list.append(self.cfg_bouquets_help)
				num = 0
				for bouquet in self.Bouquetlist:
					num += 1
					for i in range(len(self.Bouquetlist)):
						if num == i:
							list.append(getConfigListEntry(bouquet[0], self.BouquetsKey[i]))
			list.append(self.cfg_hotkey)
			if self.NZE.hotkey.value:
				list.append(getConfigListEntry(_("Hotkey action have priority"), self.NZE.hotkeys_priority))
				list.append(getConfigListEntry(_("Confirmation on hotkey action"), self.NZE.hotkeys_confirmation))
				for key,val in sorted(self.actionlist.items(), key=lambda x: int(x[1].get('weight', 0))):
					list.append(getConfigListEntry(_(val['title']), self.action[key]))
		self["config"].list = list
		self["config"].l.setList(list)

	def newConfig(self):
		cur = self["config"].getCurrent()
		if cur in (self.cfg_enable, self.cfg_hotkey, self.cfg_picons, self.cfg_timeshift_behavior, self.cfg_acount, self.cfg_hotkey_bouquets, self.cfg_bouquets_priority):
			self.createSetup()
		elif cur == self.cfg_picondir:
			self.keyOk()

	def keyOk(self):
		cur = self["config"].getCurrent()
		if cur == self.cfg_picondir:
			self.session.openWithCallback(self.directoryBrowserClosed, DirectoryBrowser, self.NZE.picondir.value, "^.*\.png")

	def directoryBrowserClosed(self, path):
		if path != False:
			self.NZE.picondir.setValue(path)

	def keyRed(self):
		def setPrevValues(section, values):
			for (key,val) in section.content.items.items():
				value = values.get(key, None)
				if value is not None:
					if isinstance(val, ConfigSubsection):
						setPrevValues(val, value)
					else:
						val.value = value
		setPrevValues(self.NZE, self.prev_values)
		for key,val in self.actionlist.items():
			if self.action[key].value != val['hotkey']:
				self.action[key].value = val['hotkey']
		for i in range(len(self.Bouquetlist)):
			num = 0
			if i in range(len(self.prev_hotkeys_bouquets)):
				num = self.prev_hotkeys_bouquets[i]
			self.BouquetsKey[i].value = num
		self.keyGreen()

	def keyGreen(self):
		global FIRST_BEHAVIOR
		if not self.NZE.enable.value:
			self.NZE.acount.value = False
			self.NZE.timeshift_behavior.value = "0"
		if CheckTimeshift is None:
			self.NZE.key0.value = False
		self.NZE.save()
		tmp = dict()
		for key,val in self.actionlist.items():
			if self.action[key].value != val['hotkey']:
				self.actionlist[key]['hotkey'] = self.action[key].value
			if self.actionlist[key]['hotkey'] != 0:
				tmp[key] = self.actionlist[key]['hotkey']
		config.plugins.NumberZapExt.hotkeys.value = repr(tmp)
		config.plugins.NumberZapExt.hotkeys.save()
		setup_key = []
		for i in range(len(self.Bouquetlist)):
			setup_key.append((self.BouquetsKey[i].value))
		config.plugins.NumberZapExt.hotkeys_bouquets.value = str(setup_key)
		config.plugins.NumberZapExt.hotkeys_bouquets.save()
		need_restart = False
		cur_val = self.NZE.timeshift_behavior.value
		if BEHAVIOR == "1":
			if FIRST_BEHAVIOR and BEHAVIOR != cur_val:
				need_restart = True
		elif BEHAVIOR in ("0", "2"):
			if cur_val == "1" and BEHAVIOR != cur_val and FIRST_BEHAVIOR:
				need_restart = True
		if need_restart:
			open_list = [
				(_("No (do not remind)"), "notremind"),
				(_("Restart GUI"), "restart"),
				(_("No (close)"), "no"),
			]
			self.session.openWithCallback(self.restartGuiNow, ChoiceBox, title= _("GUI needs a restart to apply changes 'Behavior when timeshift is enabled'.\nRestart the GUI now?"), list = open_list)
		else:
			del self.action
			self.close()

	def restartGuiNow(self, ret):
		ret = ret and ret[1]
		if ret:
			if ret == "no":
				del self.action
				self.close()
			elif ret == "notremind":
				global FIRST_BEHAVIOR
				FIRST_BEHAVIOR = False
				del self.action
				self.close()
			elif ret == "restart":
				del self.action
				self.session.open(TryQuitMainloop, 3)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.newConfig()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.newConfig()