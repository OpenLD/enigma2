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

from Components.Converter.Converter import Converter
from enigma import eServiceReference, eServiceCenter, eConsoleAppContainer, getBestPlayableServiceReference, \
		pNavigation, iServiceInformation, iPlayableService, eLabel, eTimer, iStreamedService, iFrontendInformation
from Components.Element import cached
import NavigationInstance
import os


if os.path.isfile('/usr/lib/enigma2/python/Components/Converter/bitratecalc.so'):
	from bitratecalc import eBitrateCalculator
	binaryfound = True
else:
	binaryfound = False

class LdBitrate(Converter, object):
	VPID = 0
	APID = 1
	FORMAT = 2

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == 'VideoBitrate':
			self.type = self.VPID
		elif type == 'AudioBitrate':
			self.type = self.APID
		else:
			# format:
			#   %V - video bitrate value
			#   %A - audio bitrate value
			self.type = self.FORMAT
			self.sfmt = type[:]
			if self.sfmt == '':
				self.sfmt = "V:%V Kb/s A:%A Kb/s"
		self.CleanData()
		self.Start_Timer()

	def addspace(text):
		if text:
			text += "  "
		return text

	def CleanData(self):
		self.videoBitrate = None
		self.audioBitrate = None
		self.video = self.audio = 0

	def initBitrateCalc(self):
		vpid = apid = dvbnamespace = tsid = onid = -1
		service = self.source.service
		if binaryfound:
			if service:
				serviceInfo = service and service.info()
				vpid = serviceInfo.getInfo(iServiceInformation.sVideoPID)
				apid = serviceInfo.getInfo(iServiceInformation.sAudioPID)
				tsid = serviceInfo.getInfo(iServiceInformation.sTSID)
				onid = serviceInfo.getInfo(iServiceInformation.sONID)
				dvbnamespace = serviceInfo.getInfo(iServiceInformation.sNamespace)
			if vpid > 0 and (self.type == self.VPID or (self.type == self.FORMAT and "%V" in self.sfmt)):
				self.videoBitrate = eBitrateCalculator(vpid, dvbnamespace, tsid, onid, 1000, 1024*1024) # pid, dvbnamespace, tsid, onid, refresh intervall, buffer size
				self.videoBitrate.callback.append(self.getVideoBitrateData)
			if apid > 0 and (self.type == self.APID or (self.type == self.FORMAT and "%A" in self.sfmt)):
				self.audioBitrate = eBitrateCalculator(apid, dvbnamespace, tsid, onid, 1000, 64*1024)
				self.audioBitrate.callback.append(self.getAudioBitrateData)

	@cached
	def getText(self):
		if not binaryfound:
			return 'Opps'
		if self.type == self.VPID:
			return '%d' % self.video
		elif self.type == self.APID:
			return '%d' % self.audio
		else:
			return self.sfmt[:].replace('%A', '%d' % self.audio).replace('%V', '%d' % self.video)

	text = property(getText)

	def getVideoBitrateData(self, value, status): # value = rate in kbit/s, status ( 1  = ok || 0 = nok (zapped?))
		if status:
			self.video = value
		else:
			self.videoBitrate = None
			self.video = 0
		Converter.changed(self, (self.CHANGED_POLL,))

	def getAudioBitrateData(self, value, status):
		if status:
			self.audio = value
		else:
			self.audioBitrate = None
			self.audio = 0
		Converter.changed(self, (self.CHANGED_POLL,))

	def Start_Timer(self):
		self.poll_timer = eTimer()
		if self.initBitrateCalc:
			self.poll_timer.callback.append(self.initBitrateCalc)
		self.poll_timer.start(1600, True)

	def Stop_Timer(self):
		self.CleanData()
		if self.initBitrateCalc in self.poll_timer.callback:
			self.poll_timer.callback.remove(self.initBitrateCalc)
		self.poll_timer.stop()
		self.CleanMemo()

	def CleanMemo(self):
		import sys, commands
		commands.getstatusoutput('sync ; echo 3 > /proc/sys/vm/drop_caches')

	def changed(self, what):
		if what[0] == self.CHANGED_SPECIFIC:
			if what[1] in [iFrontendInformation.signalPower]:
				self.Start_Timer()
			elif what[1] in [iPlayableService.evEnd] or what[1] == iPlayableService.evSeekableStatusChanged \
			or what[1] == iPlayableService.evStopped or what[1] == iPlayableService.evCuesheetChanged \
			or what[1] == iPlayableService.evUser+1 or what[1] == iPlayableService.evUser+2 \
			or what[1] == iPlayableService.evUser+11 or what[1] == iPlayableService.evUser+12:
				self.Stop_Timer()
			Converter.changed(self, what)
		elif what[0] == self.CHANGED_POLL:
			self.downstream_elements.changed(what)
			self.Start_Timer()
