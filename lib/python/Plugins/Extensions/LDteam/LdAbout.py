#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##
## Blue Panel OpenLD
##
## Copyright (c) 2012-2022 OpenLD
##          Javier Sayago <admin@lonasdigital.com>
## 
## Git:      https://github.com/OpenLD
## Support:  https://lonasdigital.com
## Download: https://odisealinux.com
##
## Donate: https://www.lonasdigital.com/donaciones/
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
from Screens.About import MyDateConverter
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
		rc = system("df -h > /tmp/syinfo.tmp")
		self.text = _("BOX\n")
		f = open("/proc/stb/info/model",'r')
		self.text += _("Model:\t%s") % str(getMachineBrand()) + " " + str(getMachineName()) + "\n"
		f.close()
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
		if getMachineBuild() in ('vusolo4k','vuultimo4k','vuzero4k'):
			cpuMHz = "  \t(1,5 GHz)"
		elif getMachineBuild() in ('formuler1tc','formuler1','triplex','tiviaraplus'):
			cpuMHz = "  \t(1,3 GHz)"
		elif getMachineBuild() in ('u51','u5','u53','u52','u5pvr','h9'):
			cpuMHz = "  \t(1,6 GHz)"
		elif getMachineBuild() in ('vuuno4kse','vuuno4k','gbquad4k','dm900','dm920','gb7252','dags7252','xc7439','8100s'):
			cpuMHz = "  \t(1,7 GHz)"
		elif getMachineBuild() in ('alien5'):
			cpuMHz = "  \t(2,0 GHz)"
		elif getMachineBuild() in ('sf5008','et13000','et1x000','hd52','hd51','sf4008','vs1500','h7'):
			try:
				import binascii
				f = open('/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency', 'rb')
				clockfrequency = f.read()
				f.close()
				cpuMHz = "  \t(%s MHz)" % str(round(int(binascii.hexlify(clockfrequency), 16)/1000000,1))
			except:
				cpuMHz = "  \t(1,7 GHz)"
		elif res:
			cpuMHz = "  \t(" + res.replace("\n", "") + " MHz)"
		if res2:
			bogoMIPS = "" + res2.replace("\n", "")
		f = open('/proc/cpuinfo', 'r')
		self.text += "CPU: \t" + str(about.getCPUString()) + cpuMHz + "  " + str(about.getCpuCoresString2()) + "\n"
		self.text += _("Cores:\t %s") % str(about.getCpuCoresString()) + "\n"
		self.text += _("Architecture:\t %s") % str(about.getCPUArch()) + "\n"
		self.text += "BogoMIPS: \t" + bogoMIPS + "\n"
		f.close()

		self.text += "\nSOFTWARE\n"
		openLD = "OpenLD "
		self.text += "Firmware:\t %s" % openLD + str(about.getImageVersion()) + "\n"
		self.text += _("CodeName:\t %s") % str(getImageCodeName()) + "\n"
		self.text += "Kernel: \t " + about.getKernelVersionString() + "\n"
		self.text += _("DVB drivers:\t %s") % MyDateConverter(str(about.getDriverInstalledDate())) + "\n"
		self.text += _("Last update:\t %s") % MyDateConverter(str(getEnigmaVersionString())) + "\n"
		self.text += _("Restarts:\t %d ") % config.misc.startCounter.value + "\n"
		self.text += _("Uptime:\t %s") % str(about.getUptimeString()) + "\n"
		self.text += _("GStreamer:\t %s") % str(about.getGStreamerVersionString().replace('GStreamer','')) + "\n"
		if path.exists('/usr/bin/ffmpeg'):
			try:
				self.text += _("FFmpeg:\t %s") % str(about.getFFmpegVersionString()) + "\n"
			except:
				pass
		self.text += _("Python:\t %s") % about.getPythonVersionString() + "\n\n"

		self["lab1"].setText(self.text)

	def end(self):
		self.close()
