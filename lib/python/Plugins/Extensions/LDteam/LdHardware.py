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
import os
from Plugins.Plugin import PluginDescriptor
from Components.Input import Input
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap
from Screens.InputBox import InputBox
from Components.ActionMap import ActionMap, NumberActionMap
from Components.FileList import FileList
from Components.Button import Button
from Components.Label import Label
from Components.Language import language
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists, resolveFilename, createDir, SCOPE_CURRENT_SKIN, SCOPE_SKIN_IMAGE
from enigma import eListboxPythonMultiContent, gFont, eEnv, getDesktop, pNavigation
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.MenuList import MenuList
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Console import Console
import gettext
from Screens.Textexit import Textexit


class HardwareInfo(Screen):
	skin = """
<screen name="HardwareInfobis" position="center,center" size="640,480">
	<ePixmap position="20,30" zPosition="5" size="50,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/ram.png" alphatest="blend" />
	<widget source="session.Event_Now" render="Progress" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/bar.png" position="90,30" size="515,20" transparent="1" zPosition="6">
		<convert type="SpaceInfo">MemTotal</convert>
	</widget>
	<widget source="session.CurrentService" render="Label" zPosition="6" position="90,56" size="515,26" halign="left" valign="center" font="Regular; 23" transparent="0">
		<convert type="SpaceInfo">MemTotal,Full</convert>
	</widget>
	<ePixmap position="20,110" zPosition="1" size="50,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/swap.png" alphatest="blend" />
	<widget source="session.Event_Now" render="Progress" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/bar.png" position="90,110" size="515,20" transparent="1" zPosition="6">
		<convert type="SpaceInfo">SwapTotal</convert>
	</widget>
	<widget source="session.CurrentService" render="Label" zPosition="6" position="90,134" size="515,26" halign="left" valign="center" font="Regular; 23" transparent="0">
		<convert type="SpaceInfo">SwapTotal,Full</convert>
	</widget>
	<ePixmap position="20,190" zPosition="1" size="50,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/flash.png" alphatest="blend" />
	<widget source="session.Event_Now" render="Progress" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/bar.png" position="90,190" size="515,20" transparent="1" zPosition="6">
		<convert type="SpaceInfo">FleshInfo</convert>
	</widget>
	<widget source="session.CurrentService" render="Label" zPosition="6" position="90,213" size="515,26" halign="left" valign="center" font="Regular; 23" transparent="0">
		<convert type="SpaceInfo">Flesh,Full</convert>
	</widget>
	<ePixmap position="20,270" zPosition="1" size="50,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/hdd.png" alphatest="blend" />
	<widget source="session.Event_Now" render="Progress" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/bar.png" position="90,270" size="515,20" transparent="1" zPosition="6">
		<convert type="SpaceInfo">HddInfo</convert>
	</widget>
	<widget source="session.CurrentService" render="Label" zPosition="6" position="90,293" size="515,26" halign="left" valign="center" font="Regular; 23" transparent="0">
		<convert type="SpaceInfo">HddInfo,Full</convert>
	</widget>
	<ePixmap position="20,350" zPosition="1" size="50,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/usb.png" alphatest="blend" />
	<widget source="session.Event_Now" render="Progress" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/icons/bar.png" position="90,350" size="515,20" transparent="1" zPosition="6">
		<convert type="SpaceInfo">UsbInfo</convert>
	</widget>
	<widget source="session.CurrentService" render="Label" zPosition="6" position="90,378" size="515,26" halign="left" valign="center" font="Regular; 23" transparent="0">
		<convert type="SpaceInfo">UsbInfo,Full</convert>
	</widget>
	<widget backgroundColor="#000015" font="Regular; 23" foregroundColor="green" halign="center" position="20,440" render="Label" size="120,23" source="session.CurrentService" transparent="1" zPosition="1" valign="center">
		<convert type="CpuUsage">Total</convert>
	</widget>
</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session

		self.setup_title = _("Hardware Info")
		self.onLayoutFinish.append(self.layoutFinished)
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "WizardActions", "DirectionActions"],{"ok": self.close, "back": self.close,}, -1)

	def layoutFinished(self):
		self.setTitle(self.setup_title)

