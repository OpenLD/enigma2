#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#######################################################################
##
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
from Components.VariableText import VariableText
from enigma import eLabel, eEPGCache
from Components.config import config
from Renderer import Renderer
from time import localtime

class SimpleSingleEpgList(Renderer, VariableText):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		self.epgcache = eEPGCache.getInstance()

	GUI_WIDGET = eLabel

	def changed(self, what):
		if True:
			event = self.source.event
			service = self.source.service

			if event is None:
				self.text = ""
				return

			text = ""
			evt = None
			ENext = ""

			if self.epgcache is not None:
				evt = self.epgcache.lookupEvent(['BTM', (service.toString(), 0, -1, -1)])

			if evt:
				maxx = 0
				if config.osd.language.value == "es_ES":
					ENext = _("Siguientes eventos: ") + '\n'
				else:
					ENext = _("Next events: ") + '\n'
				for x in evt:
					if maxx > 0:
						if x[1]:
							t = localtime(x[0])
							text = text + "%02d:%02d %s\n" % (t[3], t[4], x[1])
						else:
							text = text + "n/a\n"

					maxx += 1
					if maxx > 8:
						break

			self.text = '\n' + ENext + text
