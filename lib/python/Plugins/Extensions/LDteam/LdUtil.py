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
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigYesNo, ConfigText, ConfigSelection, ConfigClock, configfile, NoSave
from Components.Sources.List import List
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest, MultiContentEntryPixmapAlphaBlend
from Components.Sources.StaticText import StaticText
from Components.Network import iNetwork
from Components.Language import language
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists, resolveFilename, createDir, SCOPE_CURRENT_SKIN, SCOPE_SKIN_IMAGE
from enigma import eListboxPythonMultiContent, gFont, eEnv, getDesktop, pNavigation
from os import system, environ, listdir, popen, getcwd, chdir, unlink, stat, mkdir, makedirs, access, remove as os_remove, rename as os_rename, W_OK, R_OK, F_OK
from Screens.Setup import Setup
from Screens.NetworkSetup import *
from random import random
import os, sys, gettext, commands, gettext, subprocess, threading, traceback, time, datetime


class LDUtiles(Screen):
	skin = """
<screen name="LDUtiles" position="70,35" size="1150,650">
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
			os.popen("wget -qO /tmp/.ip http://icanhazip.com/")
			f = open("/tmp/.ip")
			ip = f.readline()
			f.close()
			self.mbox = self.session.open(MessageBox,_("Your IP public is:\n %s") % (ip), MessageBox.TYPE_INFO)
		elif self.sel == 1:
			localip = os.popen("ifconfig eth0 | grep 'inet addr' | cut -d: -f2 | awk '{ print $1}'").read()
			self.mbox = self.session.open(MessageBox,_("Your IP local is:\n %s") % (localip), MessageBox.TYPE_INFO)
		elif self.sel == 2:
			macaddress = os.popen("cat /sys/class/net/eth?/address").read()
			self.mbox = self.session.open(MessageBox,_("Mac Adress:\n %s") % (macaddress), MessageBox.TYPE_INFO)
		elif self.sel == 3:
			os.popen("wget -qO /tmp/.ptr http://icanhazptr.com/")
			f = open("/tmp/.ptr")
			ptr = f.readline()
			f.close()
			self.mbox = self.session.open(MessageBox,_("Reverse DNS record:\n %s") % (ptr), MessageBox.TYPE_INFO)
		elif self.sel == 4:
			os.popen("wget -qO /tmp/.trace http://icanhaztrace.com/")
			f = open("/tmp/.trace")
			trace = f.readline()
			f.close()
			self.mbox = self.session.open(MessageBox,_("Trace:\n %s") % (trace), MessageBox.TYPE_INFO)
		elif self.sel == 5:
			os.popen("wget -qO /tmp/.traceroute http://icanhaztraceroute.com/")
			f = open("/tmp/.traceroute")
			traceroute = f.readline()
			f.close()
			self.mbox = self.session.open(MessageBox,_("Traceroute:\n %s") % (traceroute), MessageBox.TYPE_INFO)
		else:
			self.noYet()

	def noYet(self):
		nobox = self.session.open(MessageBox, "Funcion Todavia no disponible", MessageBox.TYPE_INFO)
		nobox.setTitle(_("Info"))


	def updateList(self):
		self.list = [ ]
		mypath = "/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/"

		mypixmap = mypath + "Network.png"
		png = LoadPixmap(mypixmap)
		name = _("IP Public")
		idx = 0
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Network.png"
		png = LoadPixmap(mypixmap)
		name = _("IP Local")
		idx = 1
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Network.png"
		png = LoadPixmap(mypixmap)
		name = _("Mac Adress")
		idx = 2
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Network.png"
		png = LoadPixmap(mypixmap)
		name = _("Reverse DNS record")
		idx = 3
		res = (name, png, idx)
		self.list.append(res)


		mypixmap = mypath + "Network.png"
		png = LoadPixmap(mypixmap)
		name = _("Trace")
		idx = 4
		res = (name, png, idx)
		self.list.append(res)


		mypixmap = mypath + "Network.png"
		png = LoadPixmap(mypixmap)
		name = _("Traceroute")
		idx = 5
		res = (name, png, idx)
		self.list.append(res)

		self["list"].list = self.list
