#
#  Converter Bitrate2
#
#
#  This plugin is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
#  Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.

#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially 
#  distributed other than under the conditions noted above.
#  
#  mod by 2boom 2013-15 08.12.2015

from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService, eTimer, eServiceReference, iStreamedService
from Components.Element import cached
import os

if os.path.isfile('/usr/lib/enigma2/python/Components/Converter/bitratecalc.so'):
	from bitratecalc import eBitrateCalculator
	binaryfound = True
else:
	binaryfound = False

class Bitrate2(Converter, object):
	VBIT = 0
	ABIT = 1
	FORMAT = 2

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "VideoBitrate":
			self.type = self.VBIT
		elif type == "AudioBitrate":
			self.type = self.ABIT
		else:
			# format:
			#   %V - video bitrate value
			#   %A - audio bitrate value
			self.type = self.FORMAT
			self.sfmt = type[:]
			if self.sfmt is '':
				self.sfmt = "V:%V Kb/s A:%A Kb/s"
		self.clearData()
		self.initTimer = eTimer()
		self.initTimer.callback.append(self.initBitrateCalc)

	def clearData(self):
		self.videoBitrate = None
		self.audioBitrate = None
		self.video = self.audio = 0

	def initBitrateCalc(self):
		service = self.source.service
		vpid = apid = dvbnamespace = tsid = onid = -1
		if binaryfound:
			if service:
				serviceInfo = service and service.info()
				vpid = serviceInfo.getInfo(iServiceInformation.sVideoPID)
				apid = serviceInfo.getInfo(iServiceInformation.sAudioPID)
				tsid = serviceInfo.getInfo(iServiceInformation.sTSID)
				onid = serviceInfo.getInfo(iServiceInformation.sONID)
				dvbnamespace = serviceInfo.getInfo(iServiceInformation.sNamespace)
			if vpid:
				self.videoBitrate = eBitrateCalculator(vpid, dvbnamespace, tsid, onid, 1000, 1024*1024) # pid, dvbnamespace, tsid, onid, refresh intervall, buffer size
				self.videoBitrate.callback.append(self.getVideoBitrateData)
			if apid:
				self.audioBitrate = eBitrateCalculator(apid, dvbnamespace, tsid, onid, 1000, 64*1024)
				self.audioBitrate.callback.append(self.getAudioBitrateData)

	@cached
	def getText(self):
		if not binaryfound:
			return 'Opps'
		if self.type is self.VBIT:
			return '%d' % self.video
		elif self.type is self.ABIT:
			return '%d' % self.audio
		else:
			return self.sfmt[:].replace('%A', '%d' % self.audio).replace('%V', '%d' % self.video)

	text = property(getText)

	def getVideoBitrateData(self, value, status):
		if status:
			self.video = value
		else:
			self.videoBitrate = None
		Converter.changed(self, (self.CHANGED_POLL,))

	def getAudioBitrateData(self, value, status):
		if status:
			self.audio = value
		else:
			self.audioBitrate = None
		Converter.changed(self, (self.CHANGED_POLL,))

	def changed(self, what):
		if what[0] is self.CHANGED_SPECIFIC:
			if what[1] is iPlayableService.evStart or what[1] is iPlayableService.evUpdatedInfo:
				self.initTimer.start(500, True)
			elif what[1] is iPlayableService.evEnd:
				self.clearData()
				Converter.changed(self, what)
		elif what[0] is self.CHANGED_POLL:
			#self.downstream_elements.changed(what)
			self.initTimer.start(500, True)
