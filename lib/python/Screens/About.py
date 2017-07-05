from enigma import *
from Screen import Screen
from Components.Element import cached
from Components.config import config
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Sources.StaticText import StaticText
from Components.Harddisk import Harddisk
from Components.NimManager import nimmanager
from Components.About import about, getVersionString, getChipSetString, getKernelVersionString, getCPUString, \
    getCpuCoresString, getPythonVersionString, getFFmpegVersionString, getGStreamerVersionString, getDriverInstalledDate, \
    getRAMTotalString, getRAMFreeString, getRAMUsedString, getRAMSharingString, getRAMStoredString, getRAMCachedString, \
    getRAMSwapTotalString, getRAMSwapFreeString
from Components.ScrollLabel import ScrollLabel
from Components.Console import Console
from Components.Converter.Poll import Poll

from ServiceReference import ServiceReference
from enigma import iServiceInformation, eServiceReference, eServiceCenter, iPlayableService, iPlayableServicePtr, eTimer, eConsoleAppContainer, getEnigmaVersionString, eLabel, getBestPlayableServiceReference, eDVBFrontendParametersSatellite, eEPGCache
from boxbranding import getBoxType, getImageCodeName, getMachineBuild, getMachineBrand, getMachineName, getImageVersion, getImageType, getImageBuild, getDriverDate

from Components.Pixmap import MultiPixmap
from Components.Network import iNetwork

from Components.Label import Label
from Components.ProgressBar import ProgressBar

from os import popen
from Tools.StbHardware import getFPVersion
from Tools.Directories import fileExists, resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
from Tools.Transponder import ConvertToHumanReadable, getChannelNumber

from os import path
from re import search

from Components.HTMLComponent import HTMLComponent
from Components.GUIComponent import GUIComponent
import skin
import os
import time
import re

boxtype = getBoxType()

def getAboutText():
	AboutText = ""

	AboutText += _("Model:\t %s %s\n") % (getMachineBrand(), getMachineName())

	if about.getChipSetString() != _("unavailable"):
		if about.getIsBroadcom():
			AboutText += _("Chipset:\t BCM%s\n") % about.getChipSetString().upper()
		else:
			AboutText += _("Chipset:\t %s\n") % about.getChipSetString().upper()

	bogoMIPS = ""
	if path.exists('/proc/cpuinfo'):
		f = open('/proc/cpuinfo', 'r')
		temp = f.readlines()
		f.close()
		try:
			for lines in temp:
				lisp = lines.split(': ')
				if lisp[0].startswith('BogoMIPS'):
					bogoMIPS = "" + str(int(float(lisp[1].replace('\n','')))) + ""
					#bogoMIPS = "" + lisp[1].replace('\n','') + ""
					break
		except:
			pass

	cpuMHz = ""
	if getMachineBuild() in ('vusolo4k', 'vuultimo4k'):
		cpuMHz = "   (1,5 GHz)"
	elif getMachineBuild() in ('vuuno4k', 'gbquad4k'):
		cpuMHz = "   (1,7 GHz)"
	elif getMachineBuild() in ('formuler1tc', 'formuler1'):
		cpuMHz = "   (1,3 GHz)"
	else:
		if path.exists('/proc/cpuinfo'):
			f = open('/proc/cpuinfo', 'r')
			temp = f.readlines()
			f.close()
			try:
				for lines in temp:
					lisp = lines.split(': ')
					if lisp[0].startswith('cpu MHz'):
						#cpuMHz = "   (" +  lisp[1].replace('\n', '') + " MHz)"
						cpuMHz = "   (" +  str(int(float(lisp[1].replace('\n', '')))) + " MHz)"
						break
			except:
				pass

	openLD = "OpenLD "

	AboutText += _("CPU:\t %s") % str(about.getCPUString()) + cpuMHz + " " + str(about.getCpuCoresString2()) + "\n"
	AboutText += _("Cores:\t %s") % str(about.getCpuCoresString()) + "\n"
	AboutText += _("Arch:\t %s") % str(about.getCPUArch()) + "\n"
	AboutText += _("BogoMIPS:\t %s") % bogoMIPS + "\n"
	AboutText += _("Firmware:\t %s") % openLD + str(getImageVersion()) + "\n"
	#AboutText += _("Build:\t %s") % getImageBuild() + "\n"
	#AboutText += _("Image Type:\t%s\n") % getImageType() + "\n"
	#AboutText += _("CodeName:\t %s") % getImageCodeName() + "\n"
	AboutText += _("Kernel:\t %s") % str(about.getKernelVersionString()) + "\n"
	AboutText += _("DVB drivers:\t %s") % str(getDriverInstalledDate()) + "\n"
	AboutText += _("Last update:\t %s") % str(getEnigmaVersionString()) + "\n"
	AboutText += _("Restarts:\t %d ") % config.misc.startCounter.value + "\n"
	AboutText += _("GStreamer:\t%s") % str(about.getGStreamerVersionString().replace('GStreamer','')) + "\n"
	AboutText += _("FFmpeg:\t %s") % str(about.getFFmpegVersionString()) + "\n"
	AboutText += _("Python:\t %s") % str(about.getPythonVersionString()) + "\n\n"
	#AboutText += _("CPU Load:\t %s") % str(about.getLoadCPUString()) + "\n"

	#AboutText += _("Installed:\t ") + about.getFlashDateString() + "\n"
	#AboutText += _("Restarts:\t %d ") % config.misc.startCounter.value + "\n\n"

	tempinfo = ""
	if path.exists('/proc/stb/sensors/temp0/value'):
		f = open('/proc/stb/sensors/temp0/value', 'r')
		tempinfo = f.read()
		f.close()
	elif path.exists('/proc/stb/fp/temp_sensor'):
		f = open('/proc/stb/fp/temp_sensor', 'r')
		tempinfo = f.read()
		f.close()
	elif path.exists('/proc/stb/sensors/temp/value'):
		f = open('/proc/stb/sensors/temp/value', 'r')
		tempinfo = f.read()
		f.close()
	elif path.exists('/sys/devices/virtual/thermal/thermal_zone0/temp'):
		f = open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r')
		tempinfo = f.read()
		tempinfo = tempinfo[:-4]
		f.close()
	if tempinfo and int(tempinfo.replace('\n', '')) > 0:
		mark = str('\xc2\xb0')
		AboutText += _("System temperature:\t%s") % tempinfo.replace('\n', '').replace(' ','') + mark + "C\n"

	tempinfo = ""
	if path.exists('/proc/stb/fp/temp_sensor_avs'):
		f = open('/proc/stb/fp/temp_sensor_avs', 'r')
		tempinfo = f.read()
		f.close()
	if tempinfo and int(tempinfo.replace('\n', '')) > 0:
		mark = str('\xc2\xb0')
		AboutText += _("Processor temperature:\t%s") % tempinfo.replace('\n', '').replace(' ','') + mark + "C\n"
	AboutLcdText = AboutText.replace('\t', ' ')

	fp_version = getFPVersion()
	if fp_version is None:
		fp_version = ""
	elif fp_version != 0:
		fp_version = _("Frontprocessor version: %s") % fp_version
		AboutText += fp_version + "\n"

	bootloader = ""
	if path.exists('/sys/firmware/devicetree/base/bolt/tag'):
		f = open('/sys/firmware/devicetree/base/bolt/tag', 'r')
		bootloader = f.readline().replace('\x00', '').replace('\n', '')
		f.close()
		AboutText += _("Bootloader:\t\t%s\n") % (bootloader)

	return AboutText, AboutLcdText

class About(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Image Information"))
		self.skinName = "AboutOE"
		self.populate()

		self["actions"] = ActionMap(["ColorActions", "SetupActions", "DirectionActions", "TimerEditActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"log": self.showCommits,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			})

	def populate(self):
		self["lab1"] = StaticText(_("Developer:\t Javier Sayago (Javilonas)"))
		self["lab2"] = StaticText(_("Support:\t https://www.lonasdigital.com"))
		self["lab3"] = StaticText(_("CodeName:\t %s") % str(getImageCodeName()))
		self["lab4"] = StaticText(_("Git:\t https://github.com/OpenLD"))
		self["lab5"] = StaticText(_("Web:\t http://www.odisealinux.com"))
		model = None

		AboutText = getAboutText()[0]

		self["AboutScrollLabel"] = ScrollLabel(AboutText)

	def showCommits(self):
		self.session.open(CommitInfo)

	def createSummary(self):
		return AboutSummary

class Devices(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Device Information"))
		self["TunerHeader"] = StaticText(_("Detected NIMs:"))
		self["HDDHeader"] = StaticText(_("Detected Devices:"))
		self["MountsHeader"] = StaticText(_("Network Servers:"))
		self["nims"] = StaticText()
		for count in (0, 1, 2, 3):
			self["Tuner" + str(count)] = StaticText("")
		self["hdd"] = StaticText()
		self["mounts"] = StaticText()
		self.list = []
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.populate2)
		self["actions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
			{
				"cancel": self.close,
				"ok": self.close
			})
		self.onLayoutFinish.append(self.populate)

	def populate(self):
		self.mountinfo = ''
		self["actions"].setEnabled(False)
		scanning = _("Wait please while scanning for devices...")
		self["nims"].setText(scanning)
		for count in (0, 1, 2, 3):
			self["Tuner" + str(count)].setText(scanning)
		self["hdd"].setText(scanning)
		self['mounts'].setText(scanning)
		self.activityTimer.start(1)

	def populate2(self):
		self.activityTimer.stop()
		self.Console = Console()
		niminfo = ""
		nims = nimmanager.nimList()
		for count in range(len(nims)):
			if niminfo:
				niminfo += "\n"
			niminfo += nims[count]
		self["nims"].setText(niminfo)

		nims = nimmanager.nimList()
		if len(nims) <= 4 :
			for count in (0, 1, 2, 3):
				if count < len(nims):
					self["Tuner" + str(count)].setText(nims[count])
				else:
					self["Tuner" + str(count)].setText("")
		else:
			desc_list = []
			count = 0
			cur_idx = -1
			while count < len(nims):
				data = nims[count].split(":")
				idx = data[0].strip('Tuner').strip()
				desc = data[1].strip()
				if desc_list and desc_list[cur_idx]['desc'] == desc:
					desc_list[cur_idx]['end'] = idx
				else:
					desc_list.append({'desc' : desc, 'start' : idx, 'end' : idx})
					cur_idx += 1
				count += 1

			for count in (0, 1, 2, 3):
				if count < len(desc_list):
					if desc_list[count]['start'] == desc_list[count]['end']:
						text = "Tuner %s: %s" % (desc_list[count]['start'], desc_list[count]['desc'])
					else:
						text = "Tuner %s-%s: %s" % (desc_list[count]['start'], desc_list[count]['end'], desc_list[count]['desc'])
				else:
					text = ""

				self["Tuner" + str(count)].setText(text)

		self.list = []
		list2 = []
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			parts = line.strip().split()
			if not parts:
				continue
			device = parts[3]
			if not search('[a-z][1-9]', device):
				continue
			if device in list2:
				continue

			mount = '/dev/' + device
			f = open('/proc/mounts', 'r')
			for line in f.readlines():
				if device in line:
					parts = line.strip().split()
					mount = str(parts[1])
					break
			f.close()

			if not mount.startswith('/dev/'):
				size = Harddisk(device).diskSize()
				free = Harddisk(device).free()

				if ((float(size) / 1024) / 1024) >= 1:
					sizeline = _("Size: ") + str(round(((float(size) / 1024) / 1024), 2)) + _("TB")
				elif (size / 1024) >= 1:
					sizeline = _("Size: ") + str(round((float(size) / 1024), 2)) + _("GB")
				elif size >= 1:
					sizeline = _("Size: ") + str(size) + _("MB")
				else:
					sizeline = _("Size: ") + _("unavailable")

				if ((float(free) / 1024) / 1024) >= 1:
					freeline = _("Free: ") + str(round(((float(free) / 1024) / 1024), 2)) + _("TB")
				elif (free / 1024) >= 1:
					freeline = _("Free: ") + str(round((float(free) / 1024), 2)) + _("GB")
				elif free >= 1:
					freeline = _("Free: ") + str(free) + _("MB")
				else:
					freeline = _("Free: ") + _("full")
				self.list.append(mount + '\t' + sizeline + ' \t' + freeline)
#			else:
#				self.list.append(mount + '\t' + _('Not mounted'))
# A hdd/usb/mmc is not displayed until it is mapped.

			list2.append(device)
		self.list = '\n'.join(self.list)
		self["hdd"].setText(self.list)

		self.Console.ePopen("df -mh | grep -v '^Filesystem'", self.Stage1Complete)

	def Stage1Complete(self, result, retval, extra_args=None):
		result = result.replace('\n                        ', ' ').split('\n')
		self.mountinfo = ""
		for line in result:
			self.parts = line.split()
			if line and self.parts[0] and (self.parts[0].startswith('192') or self.parts[0].startswith('//192')):
				line = line.split()
				try:
					ipaddress = line[0]
				except:
					ipaddress = ""
				try:
					mounttotal = line[1]
				except:
					mounttotal = ""
				try:
					mountfree = line[3]
				except:
					mountfree = ""
				if self.mountinfo:
					self.mountinfo += "\n"
				self.mountinfo += "%s (%sB, %sB %s)" % (ipaddress, mounttotal, mountfree, _("free"))

		if self.mountinfo:
			self["mounts"].setText(self.mountinfo)
		else:
			self["mounts"].setText(_('none'))
		self["actions"].setEnabled(True)

	def createSummary(self):
		return AboutSummary

class SystemMemoryInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Memory Information"))
		self.DynamicSwitch = False
		self.skinName = ["SystemMemoryInfo", "About"]
		self["lab1"] = StaticText(_("INFO RAM / FLASH"))
		self.DynamicTimer = eTimer()
		if self.updateInfo:
			try:
				self.DynamicTimer.callback.append(self.updateInfo)
				self.onShow.append(self.updateInfo)
			except:
				return
		self["AboutScrollLabel"] = ScrollLabel()

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
			{
				"cancel": self.end,
				"ok": self.end,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown,
			})

	def updateInfo(self):
		self.DynamicTimer.start(6000)
		self.AboutText = _("MEMORY") + '\n'
		if config.osd.language.value == 'es_ES':
			self.AboutText += "Total:\t%s" % str(about.getRAMTotalString()) + " MB\n"
		else:
			self.AboutText += "Total:\t%s" % str(about.getRAMTotalString()) + " MB\n"
		if config.osd.language.value == 'es_ES':
			self.AboutText += "Libre:\t%s " % str(about.getRAMFreeString()) + " MB  (" + str(about.getRAMFreePorcString()) + ")\n"
		else:
			self.AboutText += "Free:\t%s " % str(about.getRAMFreeString()) + " MB  (" + str(about.getRAMFreePorcString()) + ")\n"
		if config.osd.language.value == 'es_ES':
			self.AboutText += "Usada:\t%s" % str(about.getRAMUsedString()) + " MB  (" + str(about.getRAMusageString()) + ")\n"
		else:
			self.AboutText += "Usage:\t%s" % str(about.getRAMUsedString()) + " MB  (" + str(about.getRAMusageString()) + ")\n"
		if config.osd.language.value == 'es_ES':
			self.AboutText += "Compartida:\t%s" % str(about.getRAMSharingString()) + " MB" + "\n"
		else:
			self.AboutText += "Shared:\t%s" % str(about.getRAMSharingString()) + " MB" +  "\n"
		if config.osd.language.value == 'es_ES':
			self.AboutText += "Almacenada:\t%s" % str(about.getRAMStoredString()) + " MB" + "\n"
		else:
			self.AboutText += "Stored:\t%s" % str(about.getRAMStoredString()) + " MB" +  "\n"
		if config.osd.language.value == 'es_ES':
			self.AboutText += "Cacheada:\t%s" % str(about.getRAMCachedString()) + " MB" + "\n"
		else:
			self.AboutText += "Cached:\t%s" % str(about.getRAMCachedString()) + " MB" +  "\n"
		out_lines = file("/proc/meminfo").readlines()
		for lidx in range(len(out_lines) - 1):
			tstLine = out_lines[lidx].split()
			if "Buffers:" in tstLine:
				Buffers = out_lines[lidx].split()
				self.AboutText += _("Buffers:") + "\t" + Buffers[1] + ' kB'"\n"
			if "Cached:" in tstLine:
				Cached = out_lines[lidx].split()
				self.AboutText += _("Cached:") + "\t" + Cached[1] + ' kB'"\n"
		if config.osd.language.value == 'es_ES':
			self.AboutText += "Swap total:\t%s" % str(about.getRAMSwapTotalString()) + " MB\n"
		else:
			self.AboutText += "Swap total:\t%s" % str(about.getRAMSwapTotalString()) + " MB\n"
		if config.osd.language.value == 'es_ES':
			self.AboutText += "Swap libre:\t%s" % str(about.getRAMSwapFreeString()) + " MB\n\n"
		else:
			self.AboutText += "Swap free:\t%s" % str(about.getRAMSwapFreeString()) + " MB\n\n"

		self["actions"].setEnabled(False)
		self.Console = Console()
		self.Console.ePopen("df -mh / | grep -v '^Filesystem'", self.Stage1Complete)

	def end(self):
		self.DynamicSwitch = True
		self.DynamicTimer.stop()
		del self.DynamicTimer
		self.close()

	def Stage1Complete(self, result, retval, extra_args=None):
		flash = str(result).replace('\n', '')
		flash = flash.split()
		FlashTotal = flash[1]
		FlashFree = flash[3]
		FlashUsed = flash[2]
		FlashUse = flash[4]

		self.AboutText += _("FLASH") + '\n'
		self.AboutText += _("Total:") + "\t" + FlashTotal + "\n"
		self.AboutText += _("Free:") + "\t" + FlashFree + "\n"
		self.AboutText += _("Used:") + "\t" + FlashUsed + ' (' + FlashUse + ')'"\n\n"

		self["AboutScrollLabel"].setText(self.AboutText)
		self["actions"].setEnabled(True)

	def createSummary(self):
		return AboutSummary

class SystemNetworkInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Network Information"))
		self.skinName = ["SystemNetworkInfo", "WlanStatus"]
		self["LabelBSSID"] = StaticText()
		self["LabelESSID"] = StaticText()
		self["LabelQuality"] = StaticText()
		self["LabelSignal"] = StaticText()
		self["LabelBitrate"] = StaticText()
		self["LabelEnc"] = StaticText()
		self["BSSID"] = StaticText()
		self["ESSID"] = StaticText()
		self["quality"] = StaticText()
		self["signal"] = StaticText()
		self["bitrate"] = StaticText()
		self["enc"] = StaticText()

		self["IFtext"] = StaticText()
		self["IF"] = StaticText()
		self["Statustext"] = StaticText()
		self["statuspic"] = MultiPixmap()
		self["statuspic"].setPixmapNum(1)
		self["statuspic"].show()
		self["devicepic"] = MultiPixmap()

		self["AboutScrollLabel"] = ScrollLabel()

		self.iface = None
		self.createscreen()
		self.iStatus = None

		if iNetwork.isWirelessInterface(self.iface):
			try:
				from Plugins.SystemPlugins.WirelessLan.Wlan import iStatus
				self.iStatus = iStatus
			except:
				pass
			self.resetList()
			self.onClose.append(self.cleanup)

		self["key_red"] = StaticText(_("Close"))

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			})
		self.onLayoutFinish.append(self.updateStatusbar)

	def createscreen(self):
		self.AboutText = ""
		self.iface = "eth0"
		eth0 = about.getIfConfig('eth0')
		if eth0.has_key('addr'):
			if eth0.has_key('ifname'):
				self.AboutText += _('Interface:\t/dev/' + eth0['ifname'] + "\n")
			self.AboutText += _("IP:") + "\t" + eth0['addr'] + "\n"
			if eth0.has_key('netmask'):
				self.AboutText += _("Netmask:") + "\t" + eth0['netmask'] + "\n"
			if eth0.has_key('brdaddr'):
				self.AboutText += _('Broadcast:\t' + eth0['brdaddr'] + "\n")
			if eth0.has_key('hwaddr'):
				self.AboutText += _("MAC:") + "\t" + eth0['hwaddr'] + "\n"
			self.iface = 'eth0'

		eth1 = about.getIfConfig('eth1')
		if eth1.has_key('addr'):
			if eth1.has_key('ifname'):
				self.AboutText += _('Interface:\t/dev/' + eth1['ifname'] + "\n")
			self.AboutText += _("IP:") + "\t" + eth1['addr'] + "\n"
			if eth1.has_key('netmask'):
				self.AboutText += _("Netmask:") + "\t" + eth1['netmask'] + "\n"
			if eth1.has_key('brdaddr'):
				self.AboutText += _('Broadcast:\t' + eth1['brdaddr'] + "\n")
			if eth1.has_key('hwaddr'):
				self.AboutText += _("MAC:") + "\t" + eth1['hwaddr'] + "\n"
			self.iface = 'eth1'

		ra0 = about.getIfConfig('ra0')
		if ra0.has_key('addr'):
			if ra0.has_key('ifname'):
				self.AboutText += _('Interface:\t/dev/' + ra0['ifname'] + "\n")
			self.AboutText += _("IP:") + "\t" + ra0['addr'] + "\n"
			if ra0.has_key('netmask'):
				self.AboutText += _("Netmask:") + "\t" + ra0['netmask'] + "\n"
			if ra0.has_key('brdaddr'):
				self.AboutText += _('Broadcast:\t' + ra0['brdaddr'] + "\n")
			if ra0.has_key('hwaddr'):
				self.AboutText += _("MAC:") + "\t" + ra0['hwaddr'] + "\n"
			self.iface = 'ra0'

		wlan0 = about.getIfConfig('wlan0')
		if wlan0.has_key('addr'):
			if wlan0.has_key('ifname'):
				self.AboutText += _('Interface:\t/dev/' + wlan0['ifname'] + "\n")
			self.AboutText += _("IP:") + "\t" + wlan0['addr'] + "\n"
			if wlan0.has_key('netmask'):
				self.AboutText += _("Netmask:") + "\t" + wlan0['netmask'] + "\n"
			if wlan0.has_key('brdaddr'):
				self.AboutText += _('Broadcast:\t' + wlan0['brdaddr'] + "\n")
			if wlan0.has_key('hwaddr'):
				self.AboutText += _("MAC:") + "\t" + wlan0['hwaddr'] + "\n"
			self.iface = 'wlan0'

		wlan3 = about.getIfConfig('wlan3')
		if wlan3.has_key('addr'):
			if wlan3.has_key('ifname'):
				self.AboutText += _('Interface:\t/dev/' + wlan3['ifname'] + "\n")
			self.AboutText += _("IP:") + "\t" + wlan3['addr'] + "\n"
			if wlan3.has_key('netmask'):
				self.AboutText += _("Netmask:") + "\t" + wlan3['netmask'] + "\n"
			if wlan3.has_key('brdaddr'):
				self.AboutText += _('Broadcast:\t' + wlan3['brdaddr'] + "\n")
			if wlan3.has_key('hwaddr'):
				self.AboutText += _("MAC:") + "\t" + wlan3['hwaddr'] + "\n"
			self.iface = 'wlan3'

		rx_bytes, tx_bytes = about.getIfTransferredData(self.iface)
		self.AboutText += "\n" + _("Bytes received:") + "\t" + rx_bytes + '  (~'  + str(int(rx_bytes)/1024/1024)  + ' MB)'  + "\n"
		self.AboutText += _("Bytes sent:") + "\t" + tx_bytes + '  (~'  + str(int(tx_bytes)/1024/1024)+ ' MB)'  + "\n"

		self.console = Console()
		self.console.ePopen('ethtool %s' % self.iface, self.SpeedFinished)

	def SpeedFinished(self, result, retval, extra_args):
		result_tmp = result.split('\n')
		for line in result_tmp:
			if 'Speed:' in line:
				speed = line.split(': ')[1][:-4]
				self.AboutText += _("Speed:") + "\t" + speed + _('Mb/s')

		hostname = file('/proc/sys/kernel/hostname').read()
		self.AboutText += "\n" + _("Hostname:") + "\t" + hostname + "\n"
		self["AboutScrollLabel"].setText(self.AboutText)

	def cleanup(self):
		if self.iStatus:
			self.iStatus.stopWlanConsole()

	def resetList(self):
		if self.iStatus:
			self.iStatus.getDataForInterface(self.iface, self.getInfoCB)

	def getInfoCB(self, data, status):
		self.LinkState = None
		if data is not None:
			if data is True:
				if status is not None:
					if self.iface == 'wlan0' or self.iface == 'wlan3' or self.iface == 'ra0':
						if status[self.iface]["essid"] == "off":
							essid = _("No Connection")
						else:
							essid = str(status[self.iface]["essid"])
						if status[self.iface]["accesspoint"] == "Not-Associated":
							accesspoint = _("Not-Associated")
							essid = _("No Connection")
						else:
							accesspoint = str(status[self.iface]["accesspoint"])
						if self.has_key("BSSID"):
							self.AboutText += _('Accesspoint:') + '\t' + accesspoint + '\n'
						if self.has_key("ESSID"):
							self.AboutText += _('SSID:') + '\t' + essid + '\n'

						quality = str(status[self.iface]["quality"])
						if self.has_key("quality"):
							self.AboutText += _('Link Quality:') + '\t' + quality + '\n'

						if status[self.iface]["bitrate"] == '0':
							bitrate = _("Unsupported")
						else:
							bitrate = str(status[self.iface]["bitrate"]) + " Mb/s"
						if self.has_key("bitrate"):
							self.AboutText += _('Bitrate:') + '\t' + bitrate + '\n'

						signal = str(status[self.iface]["signal"])
						if self.has_key("signal"):
							self.AboutText += _('Signal Strength:') + '\t' + signal + '\n'

						if status[self.iface]["encryption"] == "off":
							if accesspoint == "Not-Associated":
								encryption = _("Disabled")
							else:
								encryption = _("Unsupported")
						else:
							encryption = _("Enabled")
						if self.has_key("enc"):
							self.AboutText += _('Encryption:') + '\t' + encryption + '\n'

						if status[self.iface]["essid"] == "off" or status[self.iface]["accesspoint"] == "Not-Associated" or status[self.iface]["accesspoint"] is False:
							self.LinkState = False
							self["statuspic"].setPixmapNum(1)
							self["statuspic"].show()
						else:
							self.LinkState = True
							iNetwork.checkNetworkState(self.checkNetworkCB)
						self["AboutScrollLabel"].setText(self.AboutText)

	def exit(self):
		self.close(True)

	def updateStatusbar(self):
		self["IFtext"].setText(_("Network:"))
		self["IF"].setText(iNetwork.getFriendlyAdapterName(self.iface))
		self["Statustext"].setText(_("Link:"))
		if iNetwork.isWirelessInterface(self.iface):
			self["devicepic"].setPixmapNum(1)
			try:
				self.iStatus.getDataForInterface(self.iface, self.getInfoCB)
			except:
				self["statuspic"].setPixmapNum(1)
				self["statuspic"].show()
		else:
			iNetwork.getLinkState(self.iface, self.dataAvail)
			self["devicepic"].setPixmapNum(0)
		self["devicepic"].show()

	def dataAvail(self, data):
		self.LinkState = None
		for line in data.splitlines():
			line = line.strip()
			if 'Link detected:' in line:
				if "yes" in line:
					self.LinkState = True
				else:
					self.LinkState = False
		if self.LinkState:
			iNetwork.checkNetworkState(self.checkNetworkCB)
		else:
			self["statuspic"].setPixmapNum(1)
			self["statuspic"].show()

	def checkNetworkCB(self, data):
		try:
			if iNetwork.getAdapterAttribute(self.iface, "up") is True:
				if self.LinkState is True:
					if data <= 2:
						self["statuspic"].setPixmapNum(0)
					else:
						self["statuspic"].setPixmapNum(1)
				else:
					self["statuspic"].setPixmapNum(1)
			else:
				self["statuspic"].setPixmapNum(1)
			self["statuspic"].show()
		except:
			pass

	def createSummary(self):
		return AboutSummary

class AboutSummary(Screen):
	def __init__(self, session, parent):
		Screen.__init__(self, session, parent=parent)
		self["selected"] = StaticText("openLD:" + getImageVersion())

		AboutText = getAboutText()[1]

		self["AboutText"] = StaticText(AboutText)

class TranslationInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Translation Information"))
		# don't remove the string out of the _(), or it can't be "translated" anymore.

		# TRANSLATORS: Add here whatever should be shown in the "translator" about screen, up to 6 lines (use \n for newline)
		info = _("TRANSLATOR_INFO")

		if info == "TRANSLATOR_INFO":
			info = ""

		infolines = _("").split("\n")
		infomap = {}
		for x in infolines:
			l = x.split(': ')
			if len(l) != 2:
				continue
			(type, value) = l
			infomap[type] = value
		print infomap

		self["key_red"] = Button(_("Cancel"))
		self["TranslationInfo"] = StaticText(info)

		translator_name = infomap.get("Language-Team", "none")
		if translator_name == "none":
			translator_name = infomap.get("Last-Translator", "")

		self["TranslatorName"] = StaticText(translator_name)

		self["actions"] = ActionMap(["SetupActions"],
			{
				"cancel": self.close,
				"ok": self.close
			})

class CommitInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("Latest Commits"))
		self.skinName = ["CommitInfo", "About"]
		self["AboutScrollLabel"] = ScrollLabel(_("Please wait"))

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Translations"))
		self["actions"] = ActionMap(["ColorActions", "SetupActions", "DirectionActions", "TimerEditActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown,
				"left": self.left,
				"right": self.right,
				"green": self.showTranslationInfo,
				"red": self.close
			})

		self.project = 0
		self.projects = [
			("enigma2", "Enigma2"),
			("enigma2-plugins", "Enigma2 Plugins"),
			("branding-module", "Branding Module"),
			("3rdparty-plugins", "3rdparty Plugins"),
			("e2openplugin-OpenWebif", "OpenWebif"),
			("enigma2-plugin-skins-metrixhd", "Skin MetrixHD OpenLD"),
			("enigma2-plugin-picons-openld-19edark_on_white", "Picons (TSCNEO) Dark_on_white"),
			("enigma2-plugin-picons-openld-19elight_on_transparent", "Picons (TSCNEO) Elight_on_transparent"),
			("enigma2-plugin-settings-defaultsatld", "Channel Settings for default."),
			("openld-settings", "Settings OpenLD (Collection channel settings)."),
			("openld-plugins", "OpenLD Plugins"),
			("openld-skins", "OpenLD Skins"),
			("openld-tuxbox-common", "Tuxbox Common (list of known transponders)"),
			("enigma2-skindefault", "Enigma2 Skindefault"),
			("enigma2-skins", "Enigma2 Skins"),
			("enigma2-display-skins", "Enigma2 Display Skins")
		]
		self.cachedProjects = {}
		self.Timer = eTimer()
		self.Timer.callback.append(self.readGithubCommitLogs)
		self.Timer.start(50, True)

	def showTranslationInfo(self):
		self.session.open(TranslationInfo)

	def readGithubCommitLogs(self):
		url = 'https://api.github.com/repos/OpenLD/%s/commits' % self.projects[self.project][0]
		commitlog = ""
		from datetime import datetime
		from json import loads
		from urllib2 import urlopen
		try:
			commitlog += 80 * '-' + '\n'
			commitlog += url.split('/')[-2] + '\n'
			commitlog += 80 * '-' + '\n'
			try:
				# OpenLD 3.0 uses python 2.7.12 and here we need to bypass the certificate check
				from ssl import _create_unverified_context
				log = loads(urlopen(url, timeout=5, context=_create_unverified_context()).read())
			except:
				log = loads(urlopen(url, timeout=5).read())
			for c in log:
				creator = c['commit']['author']['name']
				title = c['commit']['message']
				date = datetime.strptime(c['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%x %X')
				commitlog += date + ' ' + creator + '\n' + title + 2 * '\n'
			commitlog = commitlog.encode('utf-8')
			self.cachedProjects[self.projects[self.project][1]] = commitlog
		except:
			commitlog += _("Currently the commit log cannot be retrieved - please try later again")
		self["AboutScrollLabel"].setText(commitlog)

	def updateCommitLogs(self):
		if self.cachedProjects.has_key(self.projects[self.project][1]):
			self["AboutScrollLabel"].setText(self.cachedProjects[self.projects[self.project][1]])
		else:
			self["AboutScrollLabel"].setText(_("Please wait"))
			self.Timer.start(50, True)

	def left(self):
		self.project = self.project == 0 and len(self.projects) - 1 or self.project - 1
		self.updateCommitLogs()

	def right(self):
		self.project = self.project != len(self.projects) - 1 and self.project + 1 or 0
		self.updateCommitLogs()
