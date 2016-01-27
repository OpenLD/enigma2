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
from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Components.Label import Label
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap

class ExtraActionBox(Screen):
	skin = """
	<screen name="ExtraActionBox" position="center,center" size="560,70" title=" ">
		<widget font="Regular;20" halign="center" name="message" position="10,10" size="538,48" valign="center" />
	</screen>"""

	def __init__(self, session, message, title, action):
		Screen.__init__(self, session)
		self.session = session
		self.ctitle = title
		self.caction = action

		self["message"] = Label(message)
		self["logo"] = Pixmap()
		self.timer = eTimer()
		self.timer.callback.append(self.__setTitle)
		self.timer.start(200, 1)

	def __setTitle(self):
		if self["logo"].instance is not None:
			self["logo"].instance.setPixmapFromFile(resolveFilename(SCOPE_CURRENT_SKIN, '/usr/lib/enigma2/python/Plugins/Extensions/LDteam/images/extra/run.png'))
		self.setTitle(self.ctitle)
		self.timer = eTimer()
		self.timer.callback.append(self.__start)
		self.timer.start(200, 1)

	def __start(self):
		self.close(self.caction())
