#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from Components.HTMLComponent import HTMLComponent
from Components.GUIComponent import GUIComponent
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from ServiceReference import ServiceReference
from enigma import eListboxPythonMultiContent, eListbox, gFont, iServiceInformation, eServiceCenter, getDesktop, RT_HALIGN_LEFT, RT_VALIGN_CENTER, eDVBFrontendParametersSatellite
from Tools.Transponder import ConvertToHumanReadable, getChannelNumber
import skin
import os
import subprocess

RT_HALIGN_LEFT = 0

TYPE_TEXT = 0
TYPE_VALUE_HEX = 1
TYPE_VALUE_DEC = 2
TYPE_VALUE_HEX_DEC = 3
TYPE_SLIDER = 4
TYPE_VALUE_ORBIT_DEC = 5
TYPE_VALUE_FREQ = 6
TYPE_VALUE_FREQ_FLOAT = 7
TYPE_VALUE_BITRATE = 8

def to_unsigned(x):
	return x & 0xFFFFFFFF

def ServiceInfoListEntry(a, b, valueType=TYPE_TEXT, param=4):
	screenwidth = getDesktop(0).size().width()
	if not isinstance(b, str):
		if valueType == TYPE_VALUE_HEX:
			b = ("0x%0" + str(param) + "x") % to_unsigned(b)
		elif valueType == TYPE_VALUE_FREQ:
			b = "%s MHz" % (b / 1000)
		elif valueType == TYPE_VALUE_FREQ_FLOAT:
			b = "%s.%s MHz" % (b / 1000, b % 1000)
		elif valueType == TYPE_VALUE_BITRATE:
			b = "%s" % (b / 1000)
		elif valueType == TYPE_VALUE_HEX_DEC:
			b = ("0x%0" + str(param) + "x (%dd)") % (to_unsigned(b), b)
		elif valueType == TYPE_VALUE_ORBIT_DEC:
			direction = 'E'
			if b > 1800:
				b = 3600 - b
				direction = 'W'
			b = "%d.%d%s" % (b // 10, b % 10, direction)
		else:
			b = str(b)

	if screenwidth and screenwidth == 1920:
		return [
			#PyObject *type, *px, *py, *pwidth, *pheight, *pfnt, *pstring, *pflags;
			(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 330, 60, 1, RT_HALIGN_LEFT|RT_VALIGN_CENTER, ""),
			(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 330, 60, 1, RT_HALIGN_LEFT|RT_VALIGN_CENTER, a),
			(eListboxPythonMultiContent.TYPE_TEXT, 360, 0, 680, 60, 1, RT_HALIGN_LEFT|RT_VALIGN_CENTER, b)
		]
	else:
		return [
			#PyObject *type, *px, *py, *pwidth, *pheight, *pfnt, *pstring, *pflags;
			(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 320, 24, 0, RT_HALIGN_LEFT, ""),
			(eListboxPythonMultiContent.TYPE_TEXT, 0, 0, 320, 24, 0, RT_HALIGN_LEFT, a),
			(eListboxPythonMultiContent.TYPE_TEXT, 330, 0, 570, 24, 0, RT_HALIGN_LEFT, b)
		]

class ServiceInfoList(HTMLComponent, GUIComponent):
	def __init__(self, source):
		GUIComponent.__init__(self)
		self.l = eListboxPythonMultiContent()
		self.list = source
		self.l.setList(self.list)
		self.fontName = "Regular"
		self.fontSize = 22
		self.fontSize1080 = 30
		self.ItemHeight = 24

	def applySkin(self, desktop, screen):
		if self.skinAttributes is not None:
			attribs = [ ]
			for (attrib, value) in self.skinAttributes:
				if attrib == "font":
					font = skin.parseFont(value, ((1,1),(1,1)))
					self.fontName = font.family
					self.fontSize = font.pointSize
					self.fontSize1080 = font.pointSize
				elif attrib == "itemHeight":
					self.ItemHeight = int(value)
				else:
					attribs.append((attrib,value))
			self.skinAttributes = attribs
		rc = GUIComponent.applySkin(self, desktop, screen)
		self.setFontsize()
		self.l.setItemHeight(self.ItemHeight)
		return rc

	GUI_WIDGET = eListbox

	def setFontsize(self):
		screenwidth = getDesktop(0).size().width()
		if screenwidth and screenwidth == 1920:
			self.l.setFont(0, gFont(self.fontName, self.fontSize1080))
			self.l.setFont(1, gFont(self.fontName, self.fontSize1080 + 7))
		else:
			self.l.setFont(0, gFont(self.fontName, self.fontSize))
			self.l.setFont(1, gFont(self.fontName, self.fontSize + 5))

	def postWidgetCreate(self, instance):
		self.instance.setContent(self.l)
		self.setFontsize()

TYPE_SERVICE_INFO = 1
TYPE_TRANSPONDER_INFO = 2

class ServiceInfo(Screen):
	def __init__(self, session, serviceref=None):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Service Information"))

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"ok": self.close,
			"cancel": self.close,
			"red": self.information,
			"green": self.pids,
			"yellow": self.transponder,
			"blue": self.tuner
		}, -1)

		if serviceref:
			self.type = TYPE_TRANSPONDER_INFO
			self.skinName="ServiceInfoSimple"
			info = eServiceCenter.getInstance().info(serviceref)
			self.transponder_info = info.getInfoObject(serviceref, iServiceInformation.sTransponderData)
			# info is a iStaticServiceInformation, not a iServiceInformation
			self.info = None
			self.feinfo = None
		else:
			self.type = TYPE_SERVICE_INFO
			self["key_red"] = self["red"] = Label(_("Service"))
			self["key_green"] = self["green"] = Label(_("PIDs"))
			self["key_yellow"] = self["yellow"] = Label(_("Multiplex"))
			self["key_blue"] = self["blue"] = Label(_("Tuner status"))
			service = session.nav.getCurrentService()
			if service is not None:
				self.info = service.info()
				self.feinfo = service.frontendInfo()
			else:
				self.info = None
				self.feinfo = None

		tlist = [ ]

		self["infolist"] = ServiceInfoList(tlist)
		self.onShown.append(self.information)

	def information(self):
		if self.type == TYPE_SERVICE_INFO:
			if self.session.nav.getCurrentlyPlayingServiceOrGroup():
				name = ServiceReference(self.session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
				refstr = self.session.nav.getCurrentlyPlayingServiceReference().toString()
			else:
				name = _("N/A")
				refstr = _("N/A")
			is_crypted = None
			aspect = "-"
			videocodec = "-"
			videomode = "-"
			resolution = "-"
			if self.info:
				from Components.Converter.LdExtraInfo import codec_data
				is_crypted = self.info.getInfo(iServiceInformation.sIsCrypted)
				videocodec = codec_data.get(self.info.getInfo(iServiceInformation.sVideoType), "N/A")
				width = self.info.getInfo(iServiceInformation.sVideoWidth)
				height = self.info.getInfo(iServiceInformation.sVideoHeight)
				if width > 0 and height > 0:
					resolution = "%dx%d" % (width,height)
					resolution += ("i", "p", "-")[self.info.getInfo(iServiceInformation.sProgressive)]
					resolution += str((self.info.getInfo(iServiceInformation.sFrameRate) + 500) / 1000)
					aspect = self.getServiceInfoValue(iServiceInformation.sAspect)
					aspect = aspect in ( 1, 2, 5, 6, 9, 0xA, 0xD, 0xE ) and "4:3" or "16:9"
					resolution += " - ["+aspect+"]"
					gammas = ("SDR", "HDR", "HDR10", "HLG", "")
					if self.info.getInfo(iServiceInformation.sGamma) < len(gammas):
						gamma = gammas[self.info.getInfo(iServiceInformation.sGamma)]
						if gamma:
							resolution += " - " + gamma
				f = open("/proc/stb/video/videomode")
				videomode = f.read()[:-1].replace('\n','')
				f.close()
			import subprocess
			codenumbers = None
			codesystem = None
			caidssyst = None
			try:
				codenumbers = subprocess.check_output(["timeout -t 2 -s kill dvbsnoop -n 1 -nph 1 | grep CA_system_ID | awk -F '=' '{print $2}' | awk -F ']' '{print $1}' | wc -l"], shell=True)
				codesystem = subprocess.check_output(["timeout -t 2 -s kill dvbsnoop -n 1 -nph 1 | grep CA_system_ID | awk -F '=' '{print $2}' | awk -F ']' '{print $1}'"], shell=True)
				caidssyst = subprocess.check_output(["timeout -t 2 -s kill dvbsnoop -n 1 -nph 1 | grep CA_system_ID | awk -F '(' '{print $2}' | awk -F ')' '{print $1}'"], shell=True)
			except:
				pass
			urliptv = "%3a//"

			if urliptv in refstr:
				Labels = ( (_("Name"), name, TYPE_TEXT),
						(_("Provider"), self.getServiceInfoValue(iServiceInformation.sProvider), TYPE_TEXT),
						(_("Videoformat"), aspect, TYPE_TEXT),
						(_("Videomode"), videomode, TYPE_TEXT),
						(_("Videosize"), resolution, TYPE_TEXT),
						(_("Videocodec"), videocodec, TYPE_TEXT),
						(_("Namespace"), self.getServiceInfoValue(iServiceInformation.sNamespace), TYPE_VALUE_HEX, 8),
						(_("Encrypted"), is_crypted, TYPE_TEXT),
						(_("Coding Systems"), codenumbers, TYPE_TEXT),
						(_("Service reference"), ":".join(refstr.split(":")[:10]), TYPE_TEXT),
						(_("Stream"), refstr.split(":")[10].replace("%3a", ":"), TYPE_TEXT)
						)
			else:
				Labels = ( (_("Name"), name, TYPE_TEXT),
						(_("Provider"), self.getServiceInfoValue(iServiceInformation.sProvider), TYPE_TEXT),
						(_("Videoformat"), aspect, TYPE_TEXT),
						(_("Videomode"), videomode, TYPE_TEXT),
						(_("Videosize"), resolution, TYPE_TEXT),
						(_("Videocodec"), videocodec, TYPE_TEXT),
						(_("Namespace"), self.getServiceInfoValue(iServiceInformation.sNamespace), TYPE_VALUE_HEX, 8),
						(_("Encrypted"), is_crypted, TYPE_TEXT),
						(_("Coding Systems"), codenumbers, TYPE_TEXT),
						(_("Service reference"), ":".join(refstr.split(":")[:10]), TYPE_TEXT)
						)

			if is_crypted >= 0:
				try:
					i = 0
					caidssyst1 = caidssyst.splitlines()
					codesystem1 = codesystem.splitlines()
					while i < int(codenumbers):
						caidsystem = caidssyst1[i] + " " + codesystem1[i]
						i += 1
						newlabel = ( (_("%s " %i), caidsystem, TYPE_TEXT))
						Labels = Labels + (newlabel,)
				except:
					pass
			self.fillList(Labels)
		else:
			if self.transponder_info:
				tp_info = ConvertToHumanReadable(self.transponder_info)
				conv = { "tuner_type" 				: _("Transponder type"),
						 "system"					: _("System"),
						 "modulation"				: _("Modulation"),
						 "orbital_position"			: _("Orbital position"),
						 "frequency"				: _("Frequency"),
						 "symbol_rate"				: _("Symbol rate"),
						 "bandwidth"				: _("Bandwidth"),
						 "polarization"				: _("Polarization"),
						 "inversion"				: _("Inversion"),
						 "pilot"					: _("Pilot"),
						 "rolloff"					: _("Roll-off"),
						 "is_id"					: _("Input Stream ID"),
						 "pls_mode"					: _("PLS Mode"),
						 "pls_code"					: _("PLS Code"),
						 "t2mi_plp_id"				: _("T2MI PLP ID"),
						 "t2mi_pip"					: _("T2MI PID"),
						 "fec_inner"				: _("FEC"),
						 "code_rate_lp"				: _("Coderate LP"),
						 "code_rate_hp"				: _("Coderate HP"),
						 "constellation"			: _("Constellation"),
						 "transmission_mode"		: _("Transmission mode"),
						 "guard_interval"			: _("Guard interval"),
						 "hierarchy_information"	: _("Hierarchy information")}
				Labels = [(conv[i], tp_info[i], i == "orbital_position" and TYPE_VALUE_ORBIT_DEC or TYPE_VALUE_DEC) for i in tp_info.keys() if i in conv]
				self.fillList(Labels)

	def pids(self):
		if self.type == TYPE_SERVICE_INFO:
			Labels = ( (_("Video PID"), self.getServiceInfoValue(iServiceInformation.sVideoPID), TYPE_VALUE_HEX_DEC, 4),
					   (_("Audio PID"), self.getServiceInfoValue(iServiceInformation.sAudioPID), TYPE_VALUE_HEX_DEC, 4),
					   (_("PCR PID"), self.getServiceInfoValue(iServiceInformation.sPCRPID), TYPE_VALUE_HEX_DEC, 4),
					   (_("PMT PID"), self.getServiceInfoValue(iServiceInformation.sPMTPID), TYPE_VALUE_HEX_DEC, 4),
					   (_("TXT PID"), self.getServiceInfoValue(iServiceInformation.sTXTPID), TYPE_VALUE_HEX_DEC, 4),
					   (_("TSID"), self.getServiceInfoValue(iServiceInformation.sTSID), TYPE_VALUE_HEX_DEC, 4),
					   (_("ONID"), self.getServiceInfoValue(iServiceInformation.sONID), TYPE_VALUE_HEX_DEC, 4),
					   (_("SID"), self.getServiceInfoValue(iServiceInformation.sSID), TYPE_VALUE_HEX_DEC, 4))
			self.fillList(Labels)

	def showFrontendData(self, real):
		if self.type == TYPE_SERVICE_INFO:
			frontendData = self.feinfo and self.feinfo.getAll(real)
			Labels = self.getFEData(frontendData)
			self.fillList(Labels)

	def transponder(self):
		if self.type == TYPE_SERVICE_INFO:
			self.showFrontendData(True)

	def tuner(self):
		if self.type == TYPE_SERVICE_INFO:
			self.showFrontendData(False)

	def getFEData(self, frontendDataOrg):
		if frontendDataOrg and len(frontendDataOrg):
			frontendData = ConvertToHumanReadable(frontendDataOrg)
			if frontendDataOrg["tuner_type"] == "DVB-S" or frontendDataOrg["tuner_type"] == "DVB-S2":
				if frontendData["frequency"] > 11699999 :
					band = "High"
				else:
					band = "Low"
				t2mi = lambda x: None if x == -1 else str(x)
				return ((_("NIM"), chr(ord('A') + frontendData["tuner_number"]), TYPE_TEXT),
						(_("Type"), frontendData["tuner_type"], TYPE_TEXT),
						(_("System"), frontendData["system"], TYPE_TEXT),
						(_("Modulation"), frontendData["modulation"], TYPE_TEXT),
						(_("Orbital position"), frontendData["orbital_position"], TYPE_VALUE_DEC),
						(_("Frequency"), frontendData["frequency"], TYPE_VALUE_FREQ),
						(_("Symbol rate"), frontendData["symbol_rate"], TYPE_VALUE_BITRATE),
						(_("Polarization"), frontendData["polarization"], TYPE_TEXT),
						(_("Band"), band, TYPE_TEXT),
						(_("Inversion"), frontendData["inversion"], TYPE_TEXT),
						(_("FEC"), frontendData["fec_inner"], TYPE_TEXT),
						(_("Pilot"), frontendData.get("pilot", None), TYPE_TEXT),
						(_("Roll-off"), frontendData.get("rolloff", None), TYPE_TEXT),
						(_("Input Stream ID"), frontendData.get("is_id", 0), TYPE_VALUE_DEC),
						(_("PLS Mode"), frontendData.get("pls_mode", None), TYPE_TEXT),
						(_("PLS Code"), frontendData.get("pls_code", 0), TYPE_VALUE_DEC),
						(_("T2MI PLP ID"), t2mi(frontendData.get("t2mi_plp_id", -1)), TYPE_TEXT),
						(_("T2MI PID"), None if frontendData.get("t2mi_plp_id", -1) == -1 else str(frontendData.get("t2mi_pid", eDVBFrontendParametersSatellite.T2MI_Default_Pid)), TYPE_TEXT))
			elif frontendDataOrg["tuner_type"] == "DVB-C":
				return ((_("NIM"), chr(ord('A') + frontendData["tuner_number"]), TYPE_TEXT),
						(_("Type"), frontendData["tuner_type"], TYPE_TEXT),
						(_("System"), frontendData["system"], TYPE_TEXT),
						(_("Modulation"), frontendData["modulation"], TYPE_TEXT),
						(_("Frequency"), frontendData["frequency"], TYPE_VALUE_FREQ_FLOAT),
						(_("Symbol rate"), frontendData["symbol_rate"], TYPE_VALUE_BITRATE),
						(_("Inversion"), frontendData["inversion"], TYPE_TEXT),
						(_("FEC"), frontendData["fec_inner"], TYPE_TEXT))
			elif frontendDataOrg["tuner_type"] == "DVB-T" or frontendDataOrg["tuner_type"] == "DVB-T2":
				return ((_("NIM"), chr(ord('A') + frontendData["tuner_number"]), TYPE_TEXT),
						(_("Type"), frontendData["tuner_type"], TYPE_TEXT),
						(_("System"), frontendData["system"], TYPE_TEXT),
						(_("Frequency"), frontendData["frequency"], TYPE_VALUE_FREQ_FLOAT),
						(_("Inversion"), frontendData["inversion"], TYPE_TEXT),
						(_("Bandwidth"), frontendData["bandwidth"], TYPE_VALUE_DEC),
						(_("Code rate LP"), frontendData["code_rate_lp"], TYPE_TEXT),
						(_("Code rate HP"), frontendData["code_rate_hp"], TYPE_TEXT),
						(_("Constellation"), frontendData["constellation"], TYPE_TEXT),
						(_("Transmission mode"), frontendData["transmission_mode"], TYPE_TEXT),
						(_("Guard interval"), frontendData["guard_interval"], TYPE_TEXT),
						(_("Hierarchy info"), frontendData["hierarchy_information"], TYPE_TEXT))
			elif frontendDataOrg["tuner_type"] == "ATSC":
				return ((_("NIM"), chr(ord('A') + frontendData["tuner_number"]), TYPE_TEXT),
						(_("Type"), frontendData["tuner_type"], TYPE_TEXT),
						(_("System"), frontendData["system"], TYPE_TEXT),
						(_("Modulation"), frontendData["modulation"], TYPE_TEXT),
						(_("Frequency"), frontendData["frequency"], TYPE_VALUE_FREQ_FLOAT),
						(_("Inversion"), frontendData["inversion"], TYPE_TEXT))
		return [ ]

	def fillList(self, Labels):
		tlist = [ ]

		for item in Labels:
			if item[1] is None:
				continue
			value = item[1]
			if len(item) < 4:
				tlist.append(ServiceInfoListEntry(item[0]+":", value, item[2]))
			else:
				tlist.append(ServiceInfoListEntry(item[0]+":", value, item[2], item[3]))

		self["infolist"].l.setList(tlist)

	def getServiceInfoValue(self, what):
		if self.info is None:
			return ""

		v = self.info.getInfo(what)
		if v == -2:
			v = self.info.getInfoString(what)
		elif v == -1:
			v = _("N/A")

		return v
