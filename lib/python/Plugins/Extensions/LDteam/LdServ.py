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
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigYesNo, ConfigText, ConfigSelection, ConfigClock
from Components.Sources.List import List
from Components.Network import iNetwork
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_CURRENT_SKIN
from os import system, remove as os_remove, rename as os_rename, popen, getcwd, chdir
from Screens.Setup import Setup
from Screens.NetworkSetup import *
from Plugins.SystemPlugins.NetworkBrowser.MountManager import AutoMountManager
from Plugins.SystemPlugins.NetworkBrowser.NetworkBrowser import NetworkBrowser
from Plugins.SystemPlugins.NetworkWizard.NetworkWizard import NetworkWizard



class LDServices(Screen):
	skin = """
<screen name="LDServices" position="70,35" size="1150,650">
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
			from Plugins.Extensions.LDteam.LdNetworkSetup import NetworkSamba
			self.session.open(NetworkSamba)
		elif self.sel == 1:
			from Plugins.Extensions.LDteam.LdNetworkSetup import NetworkNfs
			self.session.open(NetworkNfs)
		elif self.sel == 2:
			from Plugins.Extensions.LDteam.LdNetworkSetup import NetworkOpenvpn
			self.session.open(NetworkOpenvpn)
		elif self.sel == 3:
			from Plugins.Extensions.LDteam.LdNetworkSetup import NetworkInadyn
			self.session.open(NetworkInadyn)
		elif self.sel == 4:
			from Plugins.Extensions.LDteam.LdNetworkSetup import NetworkMiniDLNA
			self.session.open(NetworkMiniDLNA)
		elif self.sel == 5:
			from Plugins.Extensions.LDteam.LdNetworkSetup import NetworkFtp
			self.session.open(NetworkFtp)
		elif self.sel == 6:
			from Plugins.Extensions.LDteam.LdNetworkSetup import NetworkAfp
			self.session.open(NetworkAfp)
		elif self.sel == 7:
			from Plugins.Extensions.LDteam.LdNetworkSetup import NetworkuShare
			self.session.open(NetworkuShare)
		elif self.sel == 8:
			from Plugins.Extensions.LDteam.LdNetworkSetup import NetworkTelnet
			self.session.open(NetworkTelnet)
		elif self.sel == 9:
			from Plugins.Extensions.LDteam.LdNetworkSetup import NetworkUdpxy
			self.session.open(NetworkUdpxy)
		elif self.sel == 10:
			from Plugins.Extensions.LDteam.LdNetworkSetup import NetworkXupnpd
			self.session.open(NetworkXupnpd)
		elif self.sel == 11:
			from Plugins.Extensions.LDteam.LdNetworkSetup import NetworkDjmount
			self.session.open(NetworkDjmount)
		elif self.sel == 12:
			from Plugins.Extensions.LDteam.LdNetworkSetup import NetworkMediatomb
			self.session.open(NetworkMediatomb)
		elif self.sel == 13:
			from Plugins.Extensions.LDteam.LdTunerServer import TunerServer
			self.session.open(TunerServer)
		elif self.sel == 14:
			from Plugins.Extensions.LDteam.LdNetworkSetup import NetworkTransmission
			self.session.open(NetworkTransmission)
		else:
			self.noYet()

	def noYet(self):
		nobox = self.session.open(MessageBox, "Funcion Todavia no disponible", MessageBox.TYPE_INFO)
		nobox.setTitle(_("Info"))


	def updateList(self):
		self.list = [ ]
		mypath = "/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/"

		mypixmap = mypath + "Mounts.png"
		png = LoadPixmap(mypixmap)
		name = _("Samba")
		idx = 0
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "MountManager.png"
		png = LoadPixmap(mypixmap)
		name = _("NFS")
		idx = 1
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Vpn.png"
		png = LoadPixmap(mypixmap)
		name = _("OpenVPN")
		idx = 2
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Inadyn.png"
		png = LoadPixmap(mypixmap)
		name = _("Inadyn")
		idx = 3
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Dlna.png"
		png = LoadPixmap(mypixmap)
		name = _("MiniDLNA")
		idx = 4
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Ftp.png"
		png = LoadPixmap(mypixmap)
		name = _("FTP")
		idx = 5
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Afp.png"
		png = LoadPixmap(mypixmap)
		name = _("AFP")
		idx = 6
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Ushare.png"
		png = LoadPixmap(mypixmap)
		name = _("uShare")
		idx = 7
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Telnet.png"
		png = LoadPixmap(mypixmap)
		name = _("Telnet")
		idx = 8
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Dlna.png"
		png = LoadPixmap(mypixmap)
		name = _("Udpxy")
		idx = 9
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Dlna.png"
		png = LoadPixmap(mypixmap)
		name = _("Xupnpd")
		idx = 10
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Ushare.png"
		png = LoadPixmap(mypixmap)
		name = _("Djmount")
		idx = 11
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Ushare.png"
		png = LoadPixmap(mypixmap)
		name = _("Mediatomb")
		idx = 12
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Tuner_Setup.png"
		png = LoadPixmap(mypixmap)
		name = _("RemoteTunerServer")
		idx = 13
		res = (name, png, idx)
		self.list.append(res)

		mypixmap = mypath + "Afp.png"
		png = LoadPixmap(mypixmap)
		name = _("Transmission")
		idx = 14
		res = (name, png, idx)
		self.list.append(res)

		self["list"].list = self.list
