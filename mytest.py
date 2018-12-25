import sys, os
from time import strftime, time, localtime, mktime

try:
	reload(sys)
	sys.setdefaultencoding('utf-8')
except:
	pass

if os.path.isfile("/usr/lib/enigma2/python/enigma.zip"):
	sys.path.append("/usr/lib/enigma2/python/enigma.zip")

from Tools.Profile import profile, profile_final
profile("PYTHON_START")

import Tools.RedirectOutput
from boxbranding import getBoxType, getBrandOEM, getImageCodeName, getImageType, getImageVersion, getImageBuild, getMachineBuild
print "----------------------------"
print "[Image Type] %s" % getImageType()
print "[Image Version] %s" % getImageVersion()
print "[Image Build] %s" % getImageBuild()
print "[Image CodeName] %s" % getImageCodeName()
print "----------------------------"

import enigma
import eConsoleImpl
import eBaseImpl
enigma.eTimer = eBaseImpl.eTimer
enigma.eSocketNotifier = eBaseImpl.eSocketNotifier
enigma.eConsoleAppContainer = eConsoleImpl.eConsoleAppContainer

print "Init Import modules for test"
from enigma import eTimer

from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.config import config, configfile, ConfigSubsection, getConfigListEntry, ConfigSelectionNumber, ConfigSelection, ConfigSlider, ConfigYesNo, NoSave, ConfigNumber, ConfigText
from Components.ConfigList import ConfigListScreen
from Tools.Directories import fileExists
print "End Import modules for test"

boxtype = getBoxType()

#if os.path.isfile("/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/plugin.pyo") and boxtype in ('dm7080','dm820','dm520','dm525','dm900'):
#	import pyo_patcher

from traceback import print_exc

profile("SimpleSummary")
from Screens import InfoBar
from Screens.SimpleSummary import SimpleSummary

from sys import stdout, exc_info

profile("Bouquets")
from Components.config import config, configfile, ConfigText, ConfigYesNo, ConfigInteger, NoSave, ConfigSelection
config.misc.load_unlinked_userbouquets = ConfigYesNo(default=True)
def setLoadUnlinkedUserbouquets(configElement):
	enigma.eDVBDB.getInstance().setLoadUnlinkedUserbouquets(configElement.value)
config.misc.load_unlinked_userbouquets.addNotifier(setLoadUnlinkedUserbouquets)
enigma.eDVBDB.getInstance().reloadBouquets()

profile("ParentalControl")
import Components.ParentalControl
Components.ParentalControl.InitParentalControl()

profile("LOAD:Navigation")
from Navigation import Navigation

profile("LOAD:skin")
from skin import readSkin

profile("LOAD:Tools")
from Tools.Directories import InitFallbackFiles, resolveFilename, SCOPE_PLUGINS, SCOPE_ACTIVE_SKIN, SCOPE_CURRENT_SKIN, SCOPE_CONFIG
from Components.config import config, configfile, ConfigText, ConfigYesNo, ConfigInteger, ConfigSelection, NoSave
import Components.RecordingConfig
InitFallbackFiles()

profile("config.misc")
config.misc.boxtype = ConfigText(default = boxtype)
config.misc.blackradiopic = ConfigText(default = resolveFilename(SCOPE_ACTIVE_SKIN, "black.mvi"))
radiopic = resolveFilename(SCOPE_ACTIVE_SKIN, "radio.mvi")
if os.path.exists(resolveFilename(SCOPE_CONFIG, "radio.mvi")):
	radiopic = resolveFilename(SCOPE_CONFIG, "radio.mvi")
config.misc.radiopic = ConfigText(default = radiopic)
#config.misc.isNextRecordTimerAfterEventActionAuto = ConfigYesNo(default=False)
#config.misc.isNextPowerTimerAfterEventActionAuto = ConfigYesNo(default=False)
config.misc.nextWakeup = ConfigText(default = "-1,-1,-1,0,0,-1,0")	#last shutdown time, wakeup time, timer begins, set by (0=rectimer,1=zaptimer, 2=powertimer or 3=plugin), go in standby, next rectimer, force rectimer
config.misc.SyncTimeUsing = ConfigSelection(default = "0", choices = [("0", "Transponder Time"), ("1", _("NTP"))])
config.misc.NTPserver = ConfigSelection(default = "pool.ntp.org", choices = [
		("pool.ntp.org",_("Global")),
		("ao.pool.ntp.org",_("Angola")),
		("mg.pool.ntp.org",_("Madagascar")),
		("za.pool.ntp.org",_("South Africa")),
		("tz.pool.ntp.org",_("Tanzania")),
		("bd.pool.ntp.org",_("Bangladesh")),
		("cn.pool.ntp.org",_("China")),
		("hk.pool.ntp.org",_("Hong Kong")),
		("in.pool.ntp.org",_("India")),
		("id.pool.ntp.org",_("Indonesia")),
		("ir.pool.ntp.org",_("Iran")),
		("jp.pool.ntp.org",_("Japan")),
		("kz.pool.ntp.org",_("Kazakhstan")),
		("kr.pool.ntp.org",_("Korea")),
		("my.pool.ntp.org",_("Malaysia")),
		("pk.pool.ntp.org",_("Pakistan")),
		("ph.pool.ntp.org",_("Philippines")),
		("sg.pool.ntp.org",_("Singapore")),
		("tw.pool.ntp.org",_("Taiwan")),
		("th.pool.ntp.org",_("Thailand")),
		("tr.pool.ntp.org",_("Turkey")),
		("ae.pool.ntp.org",_("United Arab Emirates")),
		("uz.pool.ntp.org",_("Uzbekistan")),
		("vn.pool.ntp.org",_("Vietnam")),
		("at.pool.ntp.org",_("Austria")),
		("by.pool.ntp.org",_("Belarus")),
		("be.pool.ntp.org",_("Belgium")),
		("bg.pool.ntp.org",_("Bulgaria")),
		("cz.pool.ntp.org",_("Czech Republic")),
		("dk.pool.ntp.org",_("Denmark")),
		("ee.pool.ntp.org",_("Estonia")),
		("fi.pool.ntp.org",_("Finland")),
		("fr.pool.ntp.org",_("France")),
		("de.pool.ntp.org",_("Germany")),
		("gr.pool.ntp.org",_("Greece")),
		("hu.pool.ntp.org",_("Hungary")),
		("ie.pool.ntp.org",_("Ireland")),
		("it.pool.ntp.org",_("Italy")),
		("lv.pool.ntp.org",_("Latvia")),
		("lt.pool.ntp.org",_("Lithuania")),
		("lu.pool.ntp.org",_("Luxembourg")),
		("mk.pool.ntp.org",_("Macedonia")),
		("md.pool.ntp.org",_("Moldova")),
		("nl.pool.ntp.org",_("Netherlands")),
		("no.pool.ntp.org",_("Norway")),
		("pl.pool.ntp.org",_("Poland")),
		("pt.pool.ntp.org",_("Portugal")),
		("ro.pool.ntp.org",_("Romania")),
		("ru.pool.ntp.org",_("Russian Federation")),
		("sk.pool.ntp.org",_("Slovakia")),
		("si.pool.ntp.org",_("Slovenia")),
		("es.pool.ntp.org",_("Spain")),
		("se.pool.ntp.org",_("Sweden")),
		("ch.pool.ntp.org",_("Switzerland")),
		("ua.pool.ntp.org",_("Ukraine")),
		("uk.pool.ntp.org",_("United Kingdom")),
		("bs.pool.ntp.org",_("Bahamas")),
		("ca.pool.ntp.org",_("Canada")),
		("gt.pool.ntp.org",_("Guatemala")),
		("mx.pool.ntp.org",_("Mexico")),
		("pa.pool.ntp.org",_("Panama")),
		("us.pool.ntp.org",_("United States")),
		("au.pool.ntp.org",_("Australia")),
		("nz.pool.ntp.org",_("New Zealand")),
		("ar.pool.ntp.org",_("Argentina")),
		("br.pool.ntp.org",_("Brazil")),
		("cl.pool.ntp.org",_("Chile")),
		])

config.misc.startCounter = ConfigInteger(default=0) # number of e2 starts...
config.misc.standbyCounter = NoSave(ConfigInteger(default=0)) # number of standby
config.misc.DeepStandby = NoSave(ConfigYesNo(default=False)) # detect deepstandby
config.misc.RestartUI = ConfigYesNo(default=False) # detect user interface restart
config.misc.epgcache_filename = ConfigText(default = "/hdd/epg.dat")

def setEPGCachePath(configElement):
	enigma.eEPGCache.getInstance().setCacheFile(configElement.value)

#demo code for use of standby enter leave callbacks
#def leaveStandby():
#	print "!!!!!!!!!!!!!!!!!leave standby"

#def standbyCountChanged(configelement):
#	print "!!!!!!!!!!!!!!!!!enter standby num", configelement.value
#	from Screens.Standby import inStandby
#	inStandby.onClose.append(leaveStandby)

#config.misc.standbyCounter.addNotifier(standbyCountChanged, initial_call = False)
####################################################

def useSyncUsingChanged(configElement):
	if config.misc.SyncTimeUsing.value == "0":
		print "[Time By]: Transponder"
		enigma.eDVBLocalTimeHandler.getInstance().setUseDVBTime(True)
		enigma.eEPGCache.getInstance().timeUpdated()
	else:
		print "[Time By]: NTP"
		enigma.eDVBLocalTimeHandler.getInstance().setUseDVBTime(False)
		enigma.eEPGCache.getInstance().timeUpdated()
config.misc.SyncTimeUsing.addNotifier(useSyncUsingChanged)

def NTPserverChanged(configElement):
	f = open("/etc/default/ntpdate", "w")
	f.write('NTPSERVERS="' + config.misc.NTPserver.value + '"')
	f.close()
	os.chmod("/etc/default/ntpdate", 0755)
	from Components.Console import Console
	Console = Console()
	Console.ePopen('/usr/bin/ntpdate-sync')
config.misc.NTPserver.addNotifier(NTPserverChanged, immediate_feedback = False)
config.misc.NTPserver.callNotifiersOnSaveAndCancel = True

profile("Twisted")
try:
	import e2reactor
	e2reactor.install()

	from twisted.internet import reactor

	def runReactor():
		reactor.run(installSignalHandlers=False)
except ImportError:
	print "twisted not available"
	def runReactor():
		enigma.runMainloop()

profile("LOAD:Plugin")

# initialize autorun plugins and plugin menu entries
from Components.PluginComponent import plugins

profile("LOAD:Wizard")
from Screens.StartWizard import *
import Screens.Rc
from Tools.BoundFunction import boundFunction
from Plugins.Plugin import PluginDescriptor

profile("misc")
had = dict()

def dump(dir, p = ""):
	if isinstance(dir, dict):
		for (entry, val) in dir.items():
			dump(val, p + "(dict)/" + entry)
	if hasattr(dir, "__dict__"):
		for name, value in dir.__dict__.items():
			if str(value) not in had:
				had[str(value)] = 1
				dump(value, p + "/" + str(name))
			else:
				print p + "/" + str(name) + ":" + str(dir.__class__) + "(cycle)"
	else:
		print p + ":" + str(dir)

# + ":" + str(dir.__class__)

# display

profile("LOAD:ScreenGlobals")
from Screens.Globals import Globals
from Screens.SessionGlobals import SessionGlobals
from Screens.Screen import Screen

profile("Screen")
Screen.global_screen = Globals()

# Session.open:
# * push current active dialog ('current_dialog') onto stack
# * call execEnd for this dialog
#   * clear in_exec flag
#   * hide screen
# * instantiate new dialog into 'current_dialog'
#   * create screens, components
#   * read, apply skin
#   * create GUI for screen
# * call execBegin for new dialog
#   * set in_exec
#   * show gui screen
#   * call components' / screen's onExecBegin
# ... screen is active, until it calls 'close'...
# Session.close:
# * assert in_exec
# * save return value
# * start deferred close handler ('onClose')
# * execEnd
#   * clear in_exec
#   * hide screen
# .. a moment later:
# Session.doClose:
# * destroy screen

class Session:
	def __init__(self, desktop = None, summary_desktop = None, navigation = None):
		self.desktop = desktop
		self.summary_desktop = summary_desktop
		self.nav = navigation
		self.delay_timer = enigma.eTimer()
		self.delay_timer.callback.append(self.processDelay)

		self.current_dialog = None

		self.dialog_stack = [ ]
		self.summary_stack = [ ]
		self.summary = None

		self.in_exec = False

		self.screen = SessionGlobals(self)

		##### hack for Openwebif - Create folders & symlink
		from enigma import eEnv
		from Tools.Directories import fileExists
		import os
		origwebifpath = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/WebInterface')
		hookpath = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenWebif/pluginshook.src')
		if not os.path.islink(origwebifpath + "/WebChilds/Toplevel.py") and os.path.exists(hookpath):
			print "[OpenWebif] hooking original webif plugins"

			cleanuplist = [
				"/__init__.py",
				"/__init__.pyo",
				"/__init__.pyc",
				"/WebChilds/__init__.py",
				"/WebChilds/__init__.pyo",
				"/WebChilds/__init__.pyc",
				"/WebChilds/External/__init__.py",
				"/WebChilds/External/__init__.pyo",
				"/WebChilds/External/__init__.pyc",
				"/WebChilds/Toplevel.py",
				"/WebChilds/Toplevel.pyo"
				"/WebChilds/Toplevel.pyc"
			]

			for cleanupfile in cleanuplist:
				if fileExists(origwebifpath + cleanupfile):
					os.remove(origwebifpath + cleanupfile)

			if not os.path.exists(origwebifpath + "/WebChilds/External"):
				os.makedirs(origwebifpath + "/WebChilds/External")
			open(origwebifpath + "/__init__.py", "w").close()
			open(origwebifpath + "/WebChilds/__init__.py", "w").close()
			open(origwebifpath + "/WebChilds/External/__init__.py", "w").close()

			os.symlink(hookpath, origwebifpath + "/WebChilds/Toplevel.py")
		##########################################################

		for p in plugins.getPlugins(PluginDescriptor.WHERE_SESSIONSTART):
			try:
				p(reason=0, session=self)
			except:
				print "Plugin raised exception at WHERE_SESSIONSTART"
				import traceback
				traceback.print_exc()

	def processDelay(self):
		callback = self.current_dialog.callback

		retval = self.current_dialog.returnValue

		if self.current_dialog.isTmp:
			self.current_dialog.doClose()
#			dump(self.current_dialog)
			del self.current_dialog
		else:
			del self.current_dialog.callback

		## hack for ready eDVBLocalTimeHandler
		# Thanks morser and OpenSPA: https://github.com/OpenSPA/dvbapp/commit/b8af9e056062a3f7765e6709dc9a3ae434b70fcb
		##
		enigma.eDVBLocalTimeHandler.getInstance().syncDVBTime()

		self.popCurrent()
		if callback is not None:
			callback(*retval)

	def execBegin(self, first=True, do_show = True):
		assert not self.in_exec
		self.in_exec = True
		c = self.current_dialog

		# when this is an execbegin after a execend of a "higher" dialog,
		# popSummary already did the right thing.
		if first:
			self.instantiateSummaryDialog(c)

		c.saveKeyboardMode()
		c.execBegin()

		# when execBegin opened a new dialog, don't bother showing the old one.
		if c == self.current_dialog and do_show:
			c.show()

	def execEnd(self, last=True):
		assert self.in_exec
		self.in_exec = False

		self.current_dialog.execEnd()
		self.current_dialog.restoreKeyboardMode()
		self.current_dialog.hide()

		if last and self.summary:
			self.current_dialog.removeSummary(self.summary)
			self.popSummary()

	def instantiateDialog(self, screen, *arguments, **kwargs):
		return self.doInstantiateDialog(screen, arguments, kwargs, self.desktop)

	def deleteDialog(self, screen):
		screen.hide()
		screen.doClose()

	def deleteDialogWithCallback(self, callback, screen, *retval):
		screen.hide()
		screen.doClose()
		if callback is not None:
			callback(*retval)

	def instantiateSummaryDialog(self, screen, **kwargs):
		if self.summary_desktop is not None:
			self.pushSummary()
			summary = screen.createSummary() or SimpleSummary
			arguments = (screen,)
			self.summary = self.doInstantiateDialog(summary, arguments, kwargs, self.summary_desktop)
			self.summary.show()
			screen.addSummary(self.summary)

	def doInstantiateDialog(self, screen, arguments, kwargs, desktop):
		# create dialog
		dlg = screen(self, *arguments, **kwargs)
		if dlg is None:
			return
		# read skin data
		readSkin(dlg, None, dlg.skinName, desktop)
		# create GUI view of this dialog
		dlg.setDesktop(desktop)
		dlg.applySkin()
		return dlg

	def pushCurrent(self):
		if self.current_dialog is not None:
			self.dialog_stack.append((self.current_dialog, self.current_dialog.shown))
			self.execEnd(last=False)

	def popCurrent(self):
		if self.dialog_stack:
			(self.current_dialog, do_show) = self.dialog_stack.pop()
			self.execBegin(first=False, do_show=do_show)
		else:
			self.current_dialog = None

	def execDialog(self, dialog):
		self.pushCurrent()
		self.current_dialog = dialog
		self.current_dialog.isTmp = False
		self.current_dialog.callback = None # would cause re-entrancy problems.
		self.execBegin()

	def openWithCallback(self, callback, screen, *arguments, **kwargs):
		dlg = self.open(screen, *arguments, **kwargs)
		dlg.callback = callback
		return dlg

	def open(self, screen, *arguments, **kwargs):
		if self.dialog_stack and not self.in_exec:
			raise RuntimeError("modal open are allowed only from a screen which is modal!")
			# ...unless it's the very first screen.

		self.pushCurrent()
		dlg = self.current_dialog = self.instantiateDialog(screen, *arguments, **kwargs)
		dlg.isTmp = True
		dlg.callback = None
		self.execBegin()
		return dlg

	def close(self, screen, *retval):
		if not self.in_exec:
			print "close after exec!"
			return

		# be sure that the close is for the right dialog!
		# if it's not, you probably closed after another dialog
		# was opened. this can happen if you open a dialog
		# onExecBegin, and forget to do this only once.
		# after close of the top dialog, the underlying will
		# gain focus again (for a short time), thus triggering
		# the onExec, which opens the dialog again, closing the loop.
		assert screen == self.current_dialog

		self.current_dialog.returnValue = retval
		self.delay_timer.start(0, 1)
		self.execEnd()

	def pushSummary(self):
		if self.summary is not None:
			self.summary.hide()
			self.summary_stack.append(self.summary)
			self.summary = None

	def popSummary(self):
		if self.summary is not None:
			self.summary.doClose()
		if not self.summary_stack:
			self.summary = None
		else:
			self.summary = self.summary_stack.pop()
		if self.summary is not None:
			self.summary.show()

profile("Standby,PowerKey")
import Screens.Standby
from Screens.Menu import MainMenu, mdom
from GlobalActions import globalActionMap

class PowerKey:
	""" PowerKey stuff - handles the powerkey press and powerkey release actions"""

	def __init__(self, session):
		self.session = session
		globalActionMap.actions["power_down"]=self.powerdown
		globalActionMap.actions["power_up"]=self.powerup
		globalActionMap.actions["power_long"]=self.powerlong
		globalActionMap.actions["deepstandby"]=self.shutdown # frontpanel long power button press
		globalActionMap.actions["discrete_off"]=self.standby
		globalActionMap.actions["sleeptimer"]=self.openSleepTimer
		globalActionMap.actions["powertimer_standby"]=self.sleepStandby
		globalActionMap.actions["powertimer_deepstandby"]=self.sleepDeepStandby
		self.standbyblocked = 1

	def MenuClosed(self, *val):
		self.session.infobar = None

	def shutdown(self):
		recordings = self.session.nav.getRecordingsCheckBeforeActivateDeepStandby()
		if recordings:
			from Screens.MessageBox import MessageBox
			self.session.openWithCallback(self.gotoStandby,MessageBox,_("Recording(s) are in progress or coming up in few seconds!\nEntering standby, after recording the box will shutdown."), type = MessageBox.TYPE_INFO, close_on_any_key = True, timeout = 10)
		elif not Screens.Standby.inTryQuitMainloop and self.session.current_dialog and self.session.current_dialog.ALLOW_SUSPEND:
			self.session.open(Screens.Standby.TryQuitMainloop, 1)

	def powerlong(self):
		if Screens.Standby.inTryQuitMainloop or (self.session.current_dialog and not self.session.current_dialog.ALLOW_SUSPEND):
			return
		self.doAction(action = config.usage.on_long_powerpress.value)

	def doAction(self, action):
		if Screens.Standby.TVinStandby:
			Screens.Standby.setTVstate('on')
			return

		self.standbyblocked = 1
		if action == "shutdown":
			self.shutdown()
		elif action == "show_menu":
			print "Show shutdown Menu"
			root = mdom.getroot()
			for x in root.findall("menu"):
				y = x.find("id")
				if y is not None:
					id = y.get("val")
					if id and id == "shutdown":
						self.session.infobar = self
						menu_screen = self.session.openWithCallback(self.MenuClosed, MainMenu, x)
						menu_screen.setTitle(_("Standby / restart"))
						return
		elif action == "standby":
			try:
				config.hdmicec.control_tv_standby_skipnow.setValue(False)
			except:
				pass # no HdmiCec
			self.standby()
		elif action == "standby_noTVshutdown":
			try:
				config.hdmicec.control_tv_standby_skipnow.setValue(True)
			except:
				pass # no HdmiCec
			self.standby()
		elif action == "powertimerStandby":
			val = 3
			self.setSleepTimer(val)
		elif action == "powertimerDeepStandby":
			val = 4
			self.setSleepTimer(val)
		elif action == "sleeptimer":
			self.openSleepTimer()

	def powerdown(self):
		self.standbyblocked = 0

	def powerup(self):
		if self.standbyblocked == 0:
			self.doAction(action = config.usage.on_short_powerpress.value)

	def gotoStandby(self, ret):
		self.standby()

	def standby(self):
		if not Screens.Standby.inStandby and self.session.current_dialog and self.session.current_dialog.ALLOW_SUSPEND and self.session.in_exec:
			self.session.open(Screens.Standby.Standby)

	def openSleepTimer(self):
		from Screens.SleepTimerEdit import SleepTimerEdit
		self.session.open(SleepTimerEdit)

	def setSleepTimer(self, val):
		from PowerTimer import PowerTimerEntry
		sleeptime = 15
		data = (int(time() + 60), int(time() + 120))
		self.addSleepTimer(PowerTimerEntry(checkOldTimers = True, *data, timerType = val, autosleepdelay = sleeptime))

	def addSleepTimer(self, timer):
		from Screens.PowerTimerEntry import TimerEntry
		self.session.openWithCallback(self.finishedAdd, TimerEntry, timer)

	def finishedAdd(self, answer):
		if answer[0]:
			entry = answer[1]
			simulTimerList = self.session.nav.PowerTimer.record(entry)

	def sleepStandby(self):
		self.doAction(action = "powertimerStandby")

	def sleepDeepStandby(self):
		self.doAction(action = "powertimerDeepStandby")

profile("Scart")
from Screens.Scart import Scart

class AutoScartControl:
	def __init__(self, session):
		self.force = False
		self.current_vcr_sb = enigma.eAVSwitch.getInstance().getVCRSlowBlanking()
		if self.current_vcr_sb and config.av.vcrswitch.value:
			self.scartDialog = session.instantiateDialog(Scart, True)
		else:
			self.scartDialog = session.instantiateDialog(Scart, False)
		config.av.vcrswitch.addNotifier(self.recheckVCRSb)
		enigma.eAVSwitch.getInstance().vcr_sb_notifier.get().append(self.VCRSbChanged)

	def recheckVCRSb(self, configElement):
		self.VCRSbChanged(self.current_vcr_sb)

	def VCRSbChanged(self, value):
		#print "vcr sb changed to", value
		self.current_vcr_sb = value
		if config.av.vcrswitch.value or value > 2:
			if value:
				self.scartDialog.showMessageBox()
			else:
				self.scartDialog.switchToTV()

profile("Load:CI")
from Screens.Ci import CiHandler

profile("Load:VolumeControl")
from Components.VolumeControl import VolumeControl

profile("Load:StackTracePrinter")
from Components.StackTrace import StackTracePrinter
StackTracePrinterInst = StackTracePrinter()

from time import time, localtime, strftime
from Tools.StbHardware import setFPWakeuptime, setRTCtime

def autorestoreLoop():
	# Check if auto restore settings fails, just start the wizard (avoid a endless loop)
	count = 0
	if os.path.exists("/media/hdd/images/config/autorestore"):
		f = open("/media/hdd/images/config/autorestore", "r")
		try:
			count = int(f.read())
		except:
			count = 0;
		f.close()
		if count >= 3:
			return False
	count += 1
	f = open("/media/hdd/images/config/autorestore", "w")
	f.write(str(count))
	f.close()
	return True

def runScreenTest():
	config.misc.startCounter.value += 1
	config.misc.startCounter.save()

	profile("readPluginList")
	enigma.pauseInit()
	plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
	enigma.resumeInit()

	profile("Init:Session")
	nav = Navigation(config.misc.nextWakeup.value)
	session = Session(desktop = enigma.getDesktop(0), summary_desktop = enigma.getDesktop(1), navigation = nav)

	CiHandler.setSession(session)

	profile("wizards")
	screensToRun = []
	RestoreSettings = None
	if os.path.exists("/media/hdd/images/config/settings") and config.misc.firstrun.value:
		if autorestoreLoop():
			RestoreSettings = True
			from Plugins.SystemPlugins.SoftwareManager.BackupRestore import RestoreScreen
			session.open(RestoreScreen, runRestore = True)
		else:
			screensToRun = [ p.__call__ for p in plugins.getPlugins(PluginDescriptor.WHERE_WIZARD) ]
			screensToRun += wizardManager.getWizards()
	else:
		if os.path.exists("/media/hdd/images/config/autorestore"):
			os.system('rm -f /media/hdd/images/config/autorestore')
		screensToRun = [ p.__call__ for p in plugins.getPlugins(PluginDescriptor.WHERE_WIZARD) ]
		screensToRun += wizardManager.getWizards()

	screensToRun.append((100, InfoBar.InfoBar))
	screensToRun.sort()
	print screensToRun

	enigma.ePythonConfigQuery.setQueryFunc(configfile.getResolvedKey)

	def runNextScreen(session, screensToRun, *result):
		if result:
			#print "[mytest.py] quitMainloop #3"
			enigma.quitMainloop(*result)
			return

		screen = screensToRun[0][1]
		args = screensToRun[0][2:]
		if screensToRun:
			session.openWithCallback(boundFunction(runNextScreen, session, screensToRun[1:]), screen, *args)
		else:
			session.open(screen, *args)

	config.misc.epgcache_filename.addNotifier(setEPGCachePath)

	if not RestoreSettings:
		runNextScreen(session, screensToRun)

	profile("Init:VolumeControl")
	vol = VolumeControl(session)
	profile("Init:PowerKey")
	power = PowerKey(session)

	if boxtype in ('alien5','osninopro','osnino','osninoplus','alphatriple','spycat4kmini','tmtwin4k','mbmicrov2','revo4k','force3uhd','wetekplay', 'wetekplay2', 'wetekhub', 'dm7020hd', 'dm7020hdv2', 'osminiplus', 'osmega', 'sf3038', 'spycat', 'e4hd', 'e4hdhybrid', 'mbmicro', 'et7500', 'mixosf5', 'mixosf7', 'mixoslumi', 'gi9196m', 'maram9', 'ixussone', 'ixusszero', 'uniboxhd1', 'uniboxhd2', 'uniboxhd3', 'sezam5000hd', 'mbtwin', 'sezam1000hd', 'mbmini', 'atemio5x00', 'beyonwizt3', '9910lx', '9911lx') or getBrandOEM() in ('fulan') or getMachineBuild() in ('dags7362' , 'dags73625', 'dags5'):
		profile("VFDSYMBOLS")
		import Components.VfdSymbols
		Components.VfdSymbols.SymbolsCheck(session)

	# we need session.scart to access it from within menu.xml
	session.scart = AutoScartControl(session)

	profile("Init:Trashcan")
	import Tools.Trashcan
	Tools.Trashcan.init(session)

	profile("Init:AutoVideoMode")
	import Screens.VideoMode
	Screens.VideoMode.autostart(session)

	profile("RunReactor")
	profile_final()

	if boxtype in ('sf8', 'classm', 'axodin', 'axodinc', 'starsatlx', 'genius', 'evo'):
		f = open("/dev/dbox/oled0", "w")
		f.write('-E2-')
		f.close()

	print "lastshutdown=%s		(True = last shutdown was OK)" % config.usage.shutdownOK.value
	print "NOK shutdown action=%s" % config.usage.shutdownNOK_action.value
	print "bootup action=%s" % config.usage.boot_action.value
	if not config.usage.shutdownOK.value and not config.usage.shutdownNOK_action.value == 'normal' or not config.usage.boot_action.value == 'normal':
		print "last shutdown = %s" % config.usage.shutdownOK.value
		import Screens.PowerLost
		Screens.PowerLost.PowerLost(session)

	if not RestoreSettings:
		config.usage.shutdownOK.setValue(False)
		config.usage.shutdownOK.save()
		configfile.save()

	# kill showiframe if it is running (sh4 hack...)
	if getMachineBuild() in ('spark' , 'spark7162'):
		os.system("killall -9 showiframe")

	runReactor()

	print "[mytest.py] normal shutdown"
	config.misc.startCounter.save()
	config.usage.shutdownOK.setValue(True)
	config.usage.shutdownOK.save()

	profile("wakeup")

	#get currentTime
	nowTime = time()
#	if not config.misc.SyncTimeUsing.value == "0" or getBrandOEM() == 'gigablue':
	if not config.misc.SyncTimeUsing.value == "0" or boxtype.startswith('gb') or getBrandOEM().startswith('ini'):
		print "dvb time sync disabled... so set RTC now to current linux time!", strftime("%Y/%m/%d %H:%M", localtime(nowTime))
		setRTCtime(nowTime)

	#recordtimer
	if session.nav.isRecordTimerImageStandard:	#check RecordTimer instance
		tmp = session.nav.RecordTimer.getNextRecordingTime(getNextStbPowerOn = True)
		nextRecordTime = tmp[0]
		nextRecordTimeInStandby = tmp[1]
	else:
		nextRecordTime = session.nav.RecordTimer.getNextRecordingTime()
		nextRecordTimeInStandby = session.nav.RecordTimer.isNextRecordAfterEventActionAuto()
	#zaptimer
	nextZapTime = session.nav.RecordTimer.getNextZapTime()
	nextZapTimeInStandby = 0
	#powertimer
	tmp = session.nav.PowerTimer.getNextPowerManagerTime(getNextStbPowerOn = True)
	nextPowerTime = tmp[0]
	nextPowerTimeInStandby = tmp[1]
	#plugintimer
	tmp = plugins.getNextWakeupTime(getPluginIdent = True)
	nextPluginTime = tmp[0]
	nextPluginIdent = tmp[1] #"pluginname | pluginfolder"
	tmp = tmp[1].lower()
	#start in standby, depending on plugin type
	if "epgrefresh" in tmp:
		nextPluginName = "EPGRefresh"
		nextPluginTimeInStandby = 1
	elif "vps" in tmp:
		nextPluginName = "VPS"
		nextPluginTimeInStandby = 1
	elif "serienrecorder" in tmp:
		nextPluginName = "SerienRecorder"
		nextPluginTimeInStandby = 0 # plugin function for deep standby from standby not compatible (not available)
	elif "elektro" in tmp:
		nextPluginName = "Elektro"
		nextPluginTimeInStandby = 1
	elif "minipowersave" in tmp:
		nextPluginName = "MiniPowersave"
		nextPluginTimeInStandby = 1
	elif "enhancedpowersave" in tmp:
		nextPluginName = "EnhancedPowersave"
		nextPluginTimeInStandby = 1
	else:
		#default for plugins
		nextPluginName = nextPluginIdent
		nextPluginTimeInStandby = 0

	wakeupList = [
		x for x in ((nextRecordTime, 0, nextRecordTimeInStandby),
					(nextZapTime, 1, nextZapTimeInStandby),
					(nextPowerTime, 2, nextPowerTimeInStandby),
					(nextPluginTime, 3, nextPluginTimeInStandby))
		if x[0] != -1
	]
	wakeupList.sort()

	print "="*100
	if wakeupList and wakeupList[0][0] > 0:
		startTime = wakeupList[0]
		# wakeup time before timer begins
		wptime = startTime[0] - (config.workaround.wakeuptime.value * 60)
		if (wptime - nowTime) < 120: # no time to switch box back on
			wptime = int(nowTime) + 120  # so switch back on in 120 seconds

		#check for plugin-, zap- or power-timer to enable the 'forced' record-timer wakeup
		forceNextRecord = 0
		setStandby = startTime[2]
		if startTime[1] != 0 and nextRecordTime > 0:
			#when next record starts in 15 mins
			if abs(nextRecordTime - startTime[0]) <= 900:
				setStandby = forceNextRecord = 1
			#by vps-plugin
			elif startTime[1] == 3 and nextPluginName == "VPS":
				setStandby = forceNextRecord = 1

		if startTime[1] == 3:
			nextPluginName = " (%s)" % nextPluginName
		else:
			nextPluginName = ""
		print "[mytest.py] set next wakeup type to '%s'%s %s" % ({0:"record-timer",1:"zap-timer",2:"power-timer",3:"plugin-timer"}[startTime[1]], nextPluginName, {0:"and starts normal",1:"and starts in standby"}[setStandby])
		if forceNextRecord:
			print "[mytest.py] set from 'vps-plugin' or just before a 'record-timer' starts, set 'record-timer' wakeup flag"
		print "[mytest.py] set next wakeup time to", strftime("%a, %Y/%m/%d %H:%M:%S", localtime(wptime))
		#set next wakeup
		setFPWakeuptime(wptime)
		#set next standby only after shutdown in deep standby
		if Screens.Standby.quitMainloopCode != 1 and Screens.Standby.quitMainloopCode != 45:
			setStandby = 2 # 0=no standby, but get in standby if wakeup to timer start > 60 sec (not for plugin-timer, here is no standby), 1=standby, 2=no standby, when before was not in deep-standby
		config.misc.nextWakeup.value = "%d,%d,%d,%d,%d,%d,%d" % (int(nowTime),wptime,startTime[0],startTime[1],setStandby,nextRecordTime,forceNextRecord)
	else:
		config.misc.nextWakeup.value = "%d,-1,-1,0,0,-1,0" % (int(nowTime))
		if not boxtype.startswith('azboxm'): #skip for Azbox (mini)ME - setting wakeup time to past reboots box 
			setFPWakeuptime(int(nowTime) - 3600) #minus one hour -> overwrite old wakeup time
		print "[mytest.py] no set next wakeup time"
	config.misc.nextWakeup.save()
	print "="*100

	profile("stopService")
	session.nav.stopService()
	profile("nav shutdown")
	session.nav.shutdown()

	profile("configfile.save")
	configfile.save()
	from Screens import InfoBarGenerics
	InfoBarGenerics.saveResumePoints()

	return 0

profile("Init:skin")
import skin
skin.loadSkinData(enigma.getDesktop(0))

profile("InputDevice")
import Components.InputDevice
Components.InputDevice.InitInputDevices()
import Components.InputHotplug

profile("SetupDevices")
import Components.SetupDevices
Components.SetupDevices.InitSetupDevices()

profile("AVSwitch")
import Components.AVSwitch
Components.AVSwitch.InitAVSwitch()
Components.AVSwitch.InitiVideomodeHotplug()

profile("HdmiRecord")
import Components.HdmiRecord
Components.HdmiRecord.InitHdmiRecord()

profile("RecordingConfig")
import Components.RecordingConfig
Components.RecordingConfig.InitRecordingConfig()

profile("UsageConfig")
import Components.UsageConfig
Components.UsageConfig.InitUsageConfig()

profile("Init:DebugLogCheck")
import Screens.LogManager
Screens.LogManager.AutoLogManager()

#profile("Init:OnlineCheckState")
#import Components.OnlineUpdateCheck
#Components.OnlineUpdateCheck.OnlineUpdateCheck()

profile("Init:NTPSync")
import Components.NetworkTime
Components.NetworkTime.AutoNTPSync()

profile("keymapparser")
import keymapparser
keymapparser.readKeymap(config.usage.keymap.value)

profile("Network")
import Components.Network
Components.Network.InitNetwork()

profile("LCD")
import Components.Lcd
Components.Lcd.InitLcd()
Components.Lcd.IconCheck()
# Disable internal clock vfd for ini5000 until we can adjust it for standby
if boxtype in ('uniboxhd1', 'uniboxhd2', 'uniboxhd3', 'sezam5000hd', 'mbtwin', 'beyonwizt3'):
	try:
		f = open("/proc/stb/fp/enable_clock", "r").readline()[:-1]
		if f != '0':
			f = open("/proc/stb/fp/enable_clock", "w")
			f.write('0')
			f.close()
	except:
		print "Error disable enable_clock for ini5000 boxes"

if boxtype in ('dm7080', 'dm820', 'dm900', 'gb7252'):
	f=open("/proc/stb/hdmi-rx/0/hdmi_rx_monitor","r")
	check=f.read()
	f.close()
	if check.startswith("on"):
		f=open("/proc/stb/hdmi-rx/0/hdmi_rx_monitor","w")
		f.write("off")
		f.close()
	f=open("/proc/stb/audio/hdmi_rx_monitor","r")
	check=f.read()
	f.close()
	if check.startswith("on"):
		f=open("/proc/stb/audio/hdmi_rx_monitor","w")
		f.write("off")
		f.close()

profile("UserInterface")
import Screens.UserInterfacePositioner
Screens.UserInterfacePositioner.InitOsd()

profile("EpgCacheSched")
import Components.EpgLoadSave
Components.EpgLoadSave.EpgCacheSaveCheck()
Components.EpgLoadSave.EpgCacheLoadCheck()

profile("RFMod")
import Components.RFmod
Components.RFmod.InitRFmod()

profile("Init:CI")
import Screens.Ci
Screens.Ci.InitCiConfig()

profile("RcModel")
import Components.RcModel

profile("IPv6")
if os.path.exists('/etc/enigma2/ipv6'):
	try:
		fp = open('/proc/sys/net/ipv6/conf/all/disable_ipv6', 'w')
		fp.write("1")
		fp.close()
	except:
		pass

#from enigma import dump_malloc_stats
#t = eTimer()
#t.callback.append(dump_malloc_stats)
#t.start(1000)

# first, setup a screen
try:
	runScreenTest()

	plugins.shutdown()

	Components.ParentalControl.parentalControl.save()
except:
	print 'EXCEPTION IN PYTHON STARTUP CODE:'
	print '-'*60
	print_exc(file=stdout)
	print "[mytest.py] quitMainloop #4"
	enigma.quitMainloop(5)
	print '-'*60
