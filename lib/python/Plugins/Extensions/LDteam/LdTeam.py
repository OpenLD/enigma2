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
from Components.ScrollLabel import ScrollLabel
from Components.MenuList import MenuList
from Components.Button import Button
from Components.Label import Label
from Tools.LoadPixmap import LoadPixmap
from Components.ActionMap import ActionMap

class LdAboutTeam(Screen):

	def __init__(self, session, args = 0):
		self.skin = """
			<screen name="AboutTeam" position="332,120" size="602,460" title="OpenLD Team">
				<eLabel text="Developer:" position="10,40" size="108,20" font="Regular; 18" halign="left" />
				<eLabel text="Javilonas (Javier Sayago)" position="85,68" size="244,24" font="Regular; 20" halign="left" />
				<eLabel text="Contact:" position="10,125" size="84,20" font="Regular; 18" halign="left" />
				<eLabel text="Github: https://github.com/javilonas" position="85,153" size="342,24" font="Regular;20" halign="left" />
				<eLabel text="Donations:" position="10,200" size="100,20" font="Regular; 18" halign="left" />
				<eLabel text="Paypal: https://www.paypal.me/Javilonas" position="86,229" size="383,24" font="Regular;20" halign="left" />
				<eLabel text="Support:" position="10,286" size="87,20" font="Regular; 18" halign="left" />
				<eLabel text="https://www.lonasdigital.com" position="85,313" size="342,24" font="Regular;20" halign="left" />
				<eLabel text="Thank you for trust in OpenLD ;)" position="24,375" size="554,42" font="Regular; 17" halign="center" zPosition="1" transparent="1" />
			</screen>"""

		Screen.__init__(self, session)
		self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok': self.close,
		 'cancel': self.close}, -1)

	def quit(self):
		self.close()
