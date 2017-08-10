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
from enigma import *
from Screens.Screen import Screen
from Screens.Console import Console
from twisted.internet import threads
from Components.config import config
from Components.Button import Button
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.Harddisk import Harddisk
from Components.NimManager import nimmanager
from Components.About import about, getVersionString
from Components.Console import Console
from Components.Pixmap import MultiPixmap
from Components.Network import iNetwork
from Components.Language import language
from Components.Sources.StaticText import StaticText
from Components.PluginList import *
from Components.VariableText import VariableText
from Components.Element import cached
from Components.Converter.Converter import Converter
from Components.Converter.Poll import Poll
from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
from Tools.Directories import fileExists, resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
from Tools.StbHardware import getFPVersion
from Tools.LoadPixmap import LoadPixmap
from ServiceReference import ServiceReference
from enigma import eLabel, iServiceInformation, eTimer, eConsoleAppContainer, getEnigmaVersionString, RT_HALIGN_LEFT, eListboxPythonMultiContent, gFont, getDesktop, eSize, ePoint
from boxbranding import getBoxType, getImageCodeName, getMachineBuild, getMachineBrand, getMachineName, getImageVersion, getImageBuild, getDriverDate
from time import *
from types import *
import sys, socket, commands, re, new, os, gettext, _enigma, enigma, subprocess, threading, traceback, time, datetime
from os import path, popen, system, listdir, remove as os_remove, rename as os_rename, getcwd, chdir, statvfs
from re import search
from time import time
from random import randint
import os
import time
import re

class LdsysInfo(Screen):
	skin = """
<screen name="LdsysInfo" position="70,35" size="1150,650">
	<ePixmap position="700,10" zPosition="1" size="450,700" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/menu/fondo.png" alphatest="blend" transparent="1" />
	<widget name="lab1" halign="left" position="15,10" size="660,650" font="Regular;15" scrollbarMode="showOnDemand">
	</widget>
</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Image Information"))
		self.skinName = "LdsysInfo"
		self['key_green'] = Label(_("HW Info"))
		self['key_red'] = Label(_("Info Team"))
		self["lab1"] =  ScrollLabel()
		#self.DynamicTimer = eTimer()
		#self.DynamicTimer.callback.append(self.updateInfo)
		self.onShow.append(self.updateInfo)
		self["myactions"] = ActionMap(["OkCancelActions", "WizardActions", "ColorActions", "DirectionActions"],
		{
			"green": self.infohard,
			"red": self.infoteam,
			"ok": self.end,
			"cancel": self.end,
			"up": self["lab1"].pageUp,
			"down": self["lab1"].pageDown
		}, -1)

	def infohard(self):
		from Plugins.Extensions.LDteam.LdHardware import HardwareInfo
		self.session.open(HardwareInfo)

	def infoteam(self):
		from Plugins.Extensions.LDteam.LdTeam import LdAboutTeam
		self.session.open(LdAboutTeam)

	def updateInfo(self):
		#self.DynamicTimer.start(6000)
		rc = system("df -h > /tmp/syinfo.tmp")
		self.text = _("BOX\n")
		f = open("/proc/stb/info/model",'r')
		self.text += _("Model:\t%s") % str(getMachineBrand()) + " " + str(getMachineName()) + "\n"
		f.close()
		#f = open("/proc/stb/info/chipset",'r')
		#self.text += "Chipset:\t" + about.getChipSetString() + "\n"
		#f.close()
		cmd = 'cat /proc/cpuinfo | grep "cpu MHz" -m 1 | awk -F ": " ' + "'{print $2}'"
		cmd2 = 'cat /proc/cpuinfo | grep "BogoMIPS" -m 1 | awk -F ": " ' + "'{print $2}'"
		try:
			res = popen(cmd).read()
			res2 = popen(cmd2).read()
		except:
			res = ""
			res2 = ""
		cpuMHz = ""
		bogoMIPS = ""
		if getMachineBuild() in ('vusolo4k', 'vuultimo4k'):
			cpuMHz = "  \t(1,5 GHz)"
		elif getMachineBuild() in ('vuuno4k', 'gbquad4k'):
			cpuMHz = "  \t(1,7 GHz)"
		elif getMachineBuild() in ('formuler1tc', 'formuler1'):
			cpuMHz = "  \t(1,3 GHz)"
		elif res:
			cpuMHz = "  \t(" + res.replace("\n", "") + " MHz)"
		if res2:
			bogoMIPS = "" + res2.replace("\n", "")
		f = open('/proc/cpuinfo', 'r')
		self.text += "CPU: \t" + str(about.getCPUString()) + cpuMHz + "  " + str(about.getCpuCoresString2()) + "\n"
		self.text += _("Cores:\t %s") % str(about.getCpuCoresString()) + "\n"
		self.text += _("Architecture:\t %s") % str(about.getCPUArch()) + "\n"
		#self.text += _("CPU Load:\t %s") % str(about.getLoadCPUString()) + "\n"
		self.text += "BogoMIPS: \t" + bogoMIPS + "\n"
		f.close()
		#self.text += _("\nMEMORY\n")
		#self.text += _("Total:\t%s") % str(about.getRAMTotalString()) + " MB\n"
		#self.text += _("Free:\t%s ") % str(about.getRAMFreeString()) + " MB  (" + str(about.getRAMFreePorcString()) + ")\n"
		#self.text += _("Usage:\t%s") % str(about.getRAMUsedString()) + " MB  (" + str(about.getRAMusageString()) + ")\n"
		#self.text += _("Shared:\t%s") % str(about.getRAMSharingString()) + " MB" +  "\n"
		#self.text += _("Stored:\t%s") % str(about.getRAMStoredString()) + " MB" +  "\n"
		#self.text += _("Cached:\t%s") % str(about.getRAMCachedString()) + " MB" +  "\n"
		#out_lines = file("/proc/meminfo").readlines()
		#for lidx in range(len(out_lines) - 1):
		#	tstLine = out_lines[lidx].split()
		#	if "Buffers:" in tstLine:
		#		Buffers = out_lines[lidx].split()
		#		self.text += _("Buffers:") + "\t" + Buffers[1] + ' kB'"\n"
		#	if "Cached:" in tstLine:
		#		Cached = out_lines[lidx].split()
		#		self.text += _("Cached:") + "\t" + Cached[1] + ' kB'"\n"
		#self.text += _("Swap total:\t%s") % str(about.getRAMSwapTotalString()) + " MB\n"
		#self.text += _("Swap free:\t%s") % str(about.getRAMSwapFreeString()) + " MB\n"
		#self.text += _("\nSTORAGE\n")
		#if os.path.exists('/tmp/syinfo.tmp'):
		#	try:
		#		f = open("/tmp/syinfo.tmp",'r')
		#		line = f.readline()
		#		parts = line.split()
		#		self.text += parts[0] + "\t" + parts[1].strip() + "      " + parts[2].strip() + "    " + parts[3].strip() + "    " + parts[4] + "\n"
		#		line = f.readline()
		#		parts = line.split()
		#		self.text += "Flash" + "\t" + parts[1].strip() + "  " + parts[2].strip()  + "  " +  parts[3].strip()  + "  " +  parts[4] + "\n"
		#		for line in f.readlines():
		#			if line.find('/media/') != -1:
		#				line = line.replace('/media/', '   ')
		#				parts = line.split()
		#				if len(parts) == 6:
		#					self.text += parts[5] + "\t" + parts[1].strip() + "  " + parts[2].strip() + "  " + parts[3].strip() + "  " + parts[4] + "\n"
		#		f.close()
		#		os_remove("/tmp/syinfo.tmp")
		#	except:
		#		return

		self.text += "\nSOFTWARE\n"
		openLD = "OpenLD "
		self.text += "Firmware:\t %s" % openLD + str(about.getImageVersion()) + "\n"
		self.text += _("CodeName:\t %s") % str(getImageCodeName()) + "\n"
		self.text += "Kernel: \t " + about.getKernelVersionString() + "\n"
		self.text += _("DVB drivers:\t %s") % str(about.getDriverInstalledDate()) + "\n"
		self.text += _("Last update:\t %s") % str(getEnigmaVersionString()) + "\n"
		self.text += _("Restarts:\t %d ") % config.misc.startCounter.value + "\n"
		self.text += _("Uptime:\t %s") % str(about.getUptimeString()) + "\n"
		self.text += _("GStreamer:\t%s") % str(about.getGStreamerVersionString().replace('GStreamer','')) + "\n"
		self.text += _("FFmpeg:\t %s") % str(about.getFFmpegVersionString()) + "\n"
		self.text += _("Python:\t %s") % about.getPythonVersionString() + "\n\n"

		self["lab1"].setText(self.text)

	def end(self):
		#if self.updateInfo in self.DynamicTimer.callback:
		#	self.DynamicTimer.callback.remove(self.updateInfo)
		#self.DynamicTimer.stop()
		#del self.DynamicTimer
		self.close()
