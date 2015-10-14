################################################################################
#    Extended NumberZap Plugin for Enigma2
#    Version: 1.0-rc12 (12.04.2014 22:00)
#    Copyright (C) 2011,2012 vlamo <vlamodev@gmail.com>
#    mod Dima73
#
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
from Components.config import config, ConfigSubsection, ConfigYesNo, \
	ConfigInteger, ConfigDirectory, ConfigText, ConfigSelection, ConfigNothing

base_keyNumberGlobal = None
base_getBouquetNumOffset = None
base_ChannelSelectionBase__init__ = None
base_InfoBarNumberZap__init__ = None
TimeshiftEnabled = False
config.plugins.NumberZapExt = ConfigSubsection()
config.plugins.NumberZapExt.enable = ConfigYesNo(default=False)
config.plugins.NumberZapExt.kdelay = ConfigInteger(3000, limits=(0,9999))	# "time to wait next keypress (milliseconds)"
# "alternative service counter in bouquets"
try:
	config.plugins.NumberZapExt.acount = config.usage.alternative_number_mode
except:
	config.plugins.NumberZapExt.acount = ConfigYesNo(default=False)
config.plugins.NumberZapExt.acount_help =  ConfigNothing()
config.plugins.NumberZapExt.picons = ConfigYesNo(default=False)		# "enable picons"
config.plugins.NumberZapExt.picondir = ConfigDirectory()		# "picons directory path"
config.plugins.NumberZapExt.hotkey = ConfigYesNo(default=False)		# "enable number hotkeys"
config.plugins.NumberZapExt.hotkeys = ConfigText('{}')
config.plugins.NumberZapExt.bouquets_enable = ConfigYesNo(default=False)	# "enable number hotkeys bouquets"
config.plugins.NumberZapExt.hotkeys_bouquets = ConfigText('[]')
config.plugins.NumberZapExt.bouquets_priority = ConfigYesNo(default=False)
config.plugins.NumberZapExt.bouquets_help =  ConfigNothing()
config.plugins.NumberZapExt.hotkeys_priority = ConfigYesNo(default=False)
config.plugins.NumberZapExt.hotkeys_confirmation = ConfigYesNo(default=True)
config.plugins.NumberZapExt.timeshift_behavior = ConfigSelection([("0", _("standart")),("1", _("always number zap")),("2", _("only seek jump if available"))], default="0")
config.plugins.NumberZapExt.key0 = ConfigYesNo(default=False)
# "check timeshift if recall service"
try:
	CheckTimeshift = config.usage.check_timeshift
except:
	CheckTimeshift = None

BEHAVIOR = config.plugins.NumberZapExt.timeshift_behavior.value

from Screens.InfoBarGenerics import InfoBarNumberZap, InfoBarPiP
from Screens.ChannelSelection import ChannelSelectionBase
from Tools.BoundFunction import boundFunction
from Components.ParentalControl import parentalControl
from Components.ActionMap import NumberActionMap
from NumberZapExt import ACTIONLIST, getServiceFromNumber, NumberZapExt, NumberZapExtSetupScreen
from enigma import eServiceReference

def actionConfirmed(self, action, retval):
	if retval:
		entry = ACTIONLIST[action]
		if entry['type'] == 'code':
			if entry['args']:
				exec entry['args'] in globals(), locals()
		elif entry['type'] == 'screen':
			screen = entry.get('screen')
			if screen:
				module = entry.get('module')
				if module:
					exec 'from ' + module + ' import ' + screen in globals(), locals()
				self.session.open(*eval(screen + ', ' + entry['args']))
		elif entry['type'] == 'setup':
			from Screens.Setup import Setup
			self.session.open(Setup, entry.get('target', ''))
		elif entry['type'] in ('menu', 'menuitem'):
			from Screens.Menu import MainMenu, mdom
			def findMenuOrItem(node, val, findwhat):
				result = None
				for x in node:
					if x.tag == 'menu':
						result = findMenuOrItem(x, val, findwhat)
					elif findwhat == 'menu' and x.tag == 'id' and x.get('val') == val:
						result = node
					elif findwhat == 'menuitem' and x.tag == 'item' and x.get('entryID') == val:
						result = x
					if not result is None: break
				return result
			
			root = mdom.getroot()
			node = findMenuOrItem(root, entry.get('target', ''), entry['type'])
			if entry['type'] == 'menu':
				self.session.open(MainMenu, node or root)
			elif not node is None:
				execstr = openstr = ''
				for x in node:
					if x.tag == 'screen':
						module = x.get("module")
						openstr = x.get("screen", module) + ", " + (x.text or "")
						execstr = module and "from Screens." + module + " import *" or ""
					elif x.tag == 'code':
						execstr = x.text
					elif x.tag == 'setup':
						execstr = "from Screens.Setup import Setup"
						openstr = "Setup, " + x.get('id')
					if execstr or openstr: break
				if execstr:
					exec execstr in globals(), locals()
				if openstr:
					self.session.open(*eval(openstr))

def zapToNumber(self, number, bouquet, startBouquet, checkParentalControl=True, ref=None):
	if checkParentalControl:
		service, bouquet = getServiceFromNumber(self, number, config.plugins.NumberZapExt.acount.value, bouquet, startBouquet)
	else:
		service = ref
	if not service is None:
		if not checkParentalControl or parentalControl.isServicePlayable(service, boundFunction(zapToNumber, self, number, bouquet, startBouquet, checkParentalControl=False)):
			try:
				if CheckTimeshift is not None and TimeshiftEnabled and config.usage.check_timeshift.value and not self.servicelist.dopipzap:
					oldref = self.session.nav.getCurrentlyPlayingServiceReference()
					if oldref and oldref != service:
						ref = service
						self.checkTimeshiftRunning(boundFunction(self.numberZapCheckTimeshiftCallback, number, bouquet, startBouquet, checkParentalControl, ref))
						return
			except:
				pass
			if self.servicelist.getRoot() != bouquet:
				self.servicelist.clearPath()
				if self.servicelist.bouquet_root != bouquet:
					self.servicelist.enterPath(self.servicelist.bouquet_root)
				self.servicelist.enterPath(bouquet)
			self.servicelist.setCurrentSelection(service)
			try:
				if not self.servicelist.dopipzap:
					self.session.nav.playService(service, checkParentalControl=False)
				self.servicelist.zap(enable_pipzap=True, checkParentalControl=False)
				self.servicelist.correctChannelNumber()
				self.servicelist.startRoot = None
			except:
				self.servicelist.zap()

def numberEntered(self, retval, arg=None, startBouquet=None):
	if retval > 0:
		if isinstance(arg, eServiceReference) and (startBouquet is None or arg != startBouquet):
			OpenBouquetByRef(self, arg)
		elif isinstance(arg, str):
			if config.plugins.NumberZapExt.hotkeys_confirmation.value:
				from Screens.MessageBox import MessageBox
				self.session.openWithCallback(boundFunction(actionConfirmed, self, arg), MessageBox, _("Really run %s now?")%(_(ACTIONLIST[arg]['title'])), type=MessageBox.TYPE_YESNO, timeout=10, default=True)
			else:
				actionConfirmed(self, arg, True)
		else:
			zapToNumber(self, retval, arg, startBouquet)

def OpenBouquetByRef(self, bouquet):
	if isinstance(bouquet, eServiceReference):
		if self.servicelist.getRoot() != bouquet:
			self.servicelist.clearPath()
			if self.servicelist.bouquet_root != bouquet:
				self.servicelist.enterPath(self.servicelist.bouquet_root)
			self.servicelist.enterPath(bouquet)
		self.session.execDialog(self.servicelist)

def recallCheckTimeshiftCallback(self, answer):
	if answer:
		try:
			self.servicelist.recallPrevService()
		except:
			pass

def numberZapCheckTimeshiftCallback(self, number, bouquet, startBouquet, checkParentalControl, ref, answer):
	global TimeshiftEnabled
	TimeshiftEnabled = False
	if answer:
		try:
			zapToNumber(self, number, bouquet, startBouquet, checkParentalControl, ref)
		except:
			pass

def keyNumberGlobal(self, number):
	#print "%s number key!!!" % number
	global TimeshiftEnabled
	TimeshiftEnabled = False
	numzapext = config.plugins.NumberZapExt.enable.value
	if not numzapext or (number == 0 and not config.plugins.NumberZapExt.key0.value):
			base_keyNumberGlobal(self, number)
	elif numzapext and number == 0 and CheckTimeshift is not None and config.plugins.NumberZapExt.key0.value:
		if isinstance(self, InfoBarPiP) and self.pipHandles0Action():
			base_keyNumberGlobal(self, number)
		else:
			hlen = self.servicelist and len(self.servicelist.history)
			if hlen and hlen > 1:
				try:
					self.checkTimeshiftRunning(self.recallCheckTimeshiftCallback)
				except:
					base_keyNumberGlobal(self, number)
			else:
				base_keyNumberGlobal(self, number)
	elif numzapext and number > 0:
		numzap = True
		timeshift_behavior = config.plugins.NumberZapExt.timeshift_behavior.value
		try:
			if self.has_key("TimeshiftActions") and self.timeshiftEnabled():
				TimeshiftEnabled = True
				if timeshift_behavior == "0":
					ts = self.getTimeshift()
					if ts and ts.isTimeshiftActive():
						numzap = False
				elif timeshift_behavior == "2":
					numzap = False
		except:
			if self.has_key("TimeshiftActions") and self.timeshift_enabled:
				TimeshiftEnabled = True
				if timeshift_behavior == "0":
					ts = self.getTimeshift()
					if ts and ts.isTimeshiftActive():
						numzap = False
				elif timeshift_behavior == "2":
					numzap = False
		if numzap:
			self.session.openWithCallback(boundFunction(numberEntered, self), NumberZapExt, number, self.servicelist)

def OpenSetupPlugin(self):
	OpenSetup(self.session)

def getBouquetNumOffset(self, bouquet):
	if config.plugins.NumberZapExt.acount.value:
		return 0
	else:
		return base_getBouquetNumOffset(self, bouquet)

def altCountChanged(self, configElement):
	try:
		if config.usage.alternative_number_mode == configElement:
			return
	except:
		service = self.getCurrentSelection()
		self.setRoot(self.getRoot())
		self.setCurrentSelection(service)

def InfoBarNumberZapExt__init__(self):
	behavior = config.plugins.NumberZapExt.timeshift_behavior.value
	num = 0
	if behavior == "1":
		num = -1
	self["NumberActions"] = NumberActionMap( [ "NumberActions"],
		{
			"1": self.keyNumberGlobal,
			"2": self.keyNumberGlobal,
			"3": self.keyNumberGlobal,
			"4": self.keyNumberGlobal,
			"5": self.keyNumberGlobal,
			"6": self.keyNumberGlobal,
			"7": self.keyNumberGlobal,
			"8": self.keyNumberGlobal,
			"9": self.keyNumberGlobal,
			"0": self.keyNumberGlobal,
		}, prio=num)
	#if behavior == "1":
	#	self["NumberActions"].setEnabled(True)

def ChannelSelectionBase__init__(self, session):
	config.plugins.NumberZapExt.acount.addNotifier(self.altCountChanged, False)
	base_ChannelSelectionBase__init__(self, session)

def StartMainSession(session, **kwargs):
	global base_getBouquetNumOffset, base_keyNumberGlobal, base_ChannelSelectionBase__init__, base_InfoBarNumberZap__init__
	if base_getBouquetNumOffset is None:
		base_getBouquetNumOffset = ChannelSelectionBase.getBouquetNumOffset
		ChannelSelectionBase.getBouquetNumOffset = getBouquetNumOffset
	if base_ChannelSelectionBase__init__ is None:
		base_ChannelSelectionBase__init__ = ChannelSelectionBase.__init__
		ChannelSelectionBase.__init__ = ChannelSelectionBase__init__
		ChannelSelectionBase.altCountChanged = altCountChanged
	if base_InfoBarNumberZap__init__ is None:
		base_InfoBarNumberZap__init__ = InfoBarNumberZap.__init__
		InfoBarNumberZap.__init__ = InfoBarNumberZapExt__init__
	if base_keyNumberGlobal is None:
		base_keyNumberGlobal = InfoBarNumberZap.keyNumberGlobal
		InfoBarNumberZap.keyNumberGlobal = keyNumberGlobal
		InfoBarNumberZap.recallCheckTimeshiftCallback = recallCheckTimeshiftCallback
		InfoBarNumberZap.numberZapCheckTimeshiftCallback = numberZapCheckTimeshiftCallback
		InfoBarNumberZap.OpenSetupPlugin = OpenSetupPlugin
		InfoBarNumberZap.OpenBouquetByRef = OpenBouquetByRef

def OpenSetup(session, **kwargs):
	session.open(NumberZapExtSetupScreen, ACTIONLIST)

def StartSetup(menuid, **kwargs):
	if menuid == "system":
		return [(_("Extended NumberZap"), OpenSetup, "numzapext_setup", None)]
	else:
		return []

def Plugins(**kwargs):
	from Plugins.Plugin import PluginDescriptor
	return [PluginDescriptor(name="Extended NumberZap", description=_("Extended NumberZap addon"), where = PluginDescriptor.WHERE_SESSIONSTART, fnc = StartMainSession),
		PluginDescriptor(name="Extended NumberZap", description=_("Extended NumberZap addon"), where = PluginDescriptor.WHERE_MENU, fnc = StartSetup)]